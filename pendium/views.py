from json import dumps as json_dumps
from mimetypes import guess_type
from traceback import format_exc

from flask import Response
from flask import abort
from flask import escape
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from pendium import app
from pendium.filesystem import PathExists
from pendium.filesystem import PathNotFound
from pendium.filesystem import Wiki


@app.route('/')
@app.route('/<path:path>')
def view(path=None, ref=None):
    path = _get_wiki_obj_from_path(path)

    if path.is_leaf and not path.is_binary:
        if not path.can_render:
            flash('No renderer found, fallback to plain text', 'warning')

        if request.args.get('ref', None) and g.wiki.has_vcs:
            path.ref(request.args.get('ref'))

        response = render_template(
            'view.html',
            file=path,
            files=path.items(),
            refs=path.refs,
            rendered=path.render(),
        )
    elif path.is_node:
        response = render_template(
            'list.html',
            file=path,
            files=path.items(),
        )
    else:
        (mimetype, enc) = guess_type(path.path)
        response = Response(
            path.render(),
            mimetype=mimetype,
        )
    return response


@app.route('/_create_folder_/', methods=['GET', 'POST'])
@app.route('/_create_folder_/<path:path>', methods=['GET', 'POST'])
def create_folder(path=None):
    path = _get_wiki_obj_from_path(path)

    if not path.is_node or not path.editable:
        abort(500)

    if request.form.get('save', None):
        dir_name = request.form.get('dir_name')
        try:
            path.create_directory(dir_name)
            flash('New folder created', 'success')
            return redirect(url_for('view', path=path.path))
        except PathExists:
            app.logger.error(format_exc())
            flash('There is already a folder by that name', 'error')

        except Exception, e:
            app.logger.error(format_exc())
            flash('There was a problem creating your folder: %s' % e, 'error')

    return render_template('create_folder.html', file=path)


@app.route('/_delete_/<path:path>', methods=['GET', 'POST'])
def delete(path):
    path = _get_wiki_obj_from_path(path)

    if not path.editable:
        abort(500)

    if request.form.get('delete', None):
        try:
            parent = path.ancestor()
            path.delete()
            flash('\'%s\' successfull deleted' % path.name, 'success')
            return redirect(url_for('view', path=parent.path))

        except Exception, e:
            app.logger.error(format_exc())
            msg = 'There was a problem deleting \'%s\': %s' % (path.name, e)
            flash(msg, 'error')

    return render_template('delete.html', file=path)


@app.route('/_create_file_/', methods=['GET', 'POST'])
@app.route('/_create_file_/<path:path>', methods=['GET', 'POST'])
def create_file(path=None):
    path = _get_wiki_obj_from_path(path)

    if not path.is_node or not path.editable:
        abort(500)

    filename = None
    filecontent = None

    if request.form.get('save', None):
        filename = request.form.get('filename')
        extension = request.form.get('extension')
        filecontent = request.form.get('content')
        try:
            if extension != '':
                filename += '.' + extension
            new_file = path.create_file(filename)
            new_file.content(content=filecontent)
            new_file.save(comment=request.form.get('message', None))
            flash('File created with the provided content', 'success')

            response = redirect(url_for('view', path=path.path))

        except PathExists:
            app.logger.error(format_exc())
            flash('There is already a file by that name', 'error')

        except Exception, e:
            app.logger.error(format_exc())
            flash('There was a problem saving your file : %s' % e, 'error')
    else:
        response = render_template(
            'create.html',
            file=path,
            filename=filename,
            extensions=_get_extensions(),
            filecontent=filecontent,
        )
    return response


@app.route('/_edit_/<path:path>', methods=['GET', 'POST'])
def edit(path):
    path = _get_wiki_obj_from_path(path)

    if not path.is_leaf or path.is_binary or not path.editable:
        abort(500)

    if request.form.get('save') or request.form.get('quiet_save'):
        try:
            path.content(content=request.form.get('content'))
            path.save(comment=request.form.get('message', None))
            flash('File saved with the new provided content', 'success')
        except Exception, e:
            app.logger.error(format_exc())
            flash('There was a problem saving your file : %s' % e, 'error')

    if request.form.get('save'):
        response = redirect(url_for('view', path=path.path))
    else:
        response = render_template(
            'edit.html',
            file=path,
            files=path.items(),
            file_content=escape(path.content()),
        )
    return response


@app.route('/search/', methods=['GET', 'POST'])
def search():
    js = json_dumps({})
    if request.args.get('q'):
        term = request.args.get('q')
        app.logger.debug('Searching for \'%s\'' % term)
        hits = g.wiki.search(term)

        hits_dicts = []
        for hit in hits:
            hit_text = term + ': ' + hit.name
            hits_dicts.append({
                'hit': hit_text,
                'path': hit.path,
            })

        js = json_dumps({
            'searched': True,
            'term':     term,
            'hits':     len(hits),
            'results':  hits_dicts,
        })

    return Response(js, mimetype='application/json')


@app.route('/refresh/')
def refresh():
    try:
        info = g.wiki.refresh()
        flash('Your wiki has been refreshed. %s' % info, 'success')
    except Exception, e:
        app.logger.error(e)
        app.logger.error(format_exc())
        flash('Error refreshing git repository', 'error')

    return redirect(url_for('view'))


@app.route('/_raw_/<path:path>')
def raw(path):
    try:
        path = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    if not path.is_leaf:
        abort(404)

    return Response(path.content(), mimetype='text/plain')


@app.context_processor
def global_context_data():
    data = {'config': app.config}
    return data


@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404


@app.before_request
def before_request():
    config = app.config
    g.wiki = Wiki(
        config['WIKI_DIR'],
        extensions=config.get('WIKI_EXTENSIONS', {}),
        default_renderer=config.get('WIKI_DEFAULT_RENDERER', None),
        plugins_config=config.get('WIKI_PLUGINS_CONFIG', {}),
        has_vcs=config.get('WIKI_GIT_SUPPORT', False)
    )


def _get_extensions():
    extensions = []
    for wiki_ext in app.config['WIKI_EXTENSIONS'].values():
        extensions += wiki_ext
    return extensions


def _get_wiki_obj_from_path(path):
    if not path:
        wiki_obj = g.wiki.get_root().path

    try:
        wiki_obj = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    return wiki_obj
