from json import dumps as json_dumps
from mimetypes import guess_type
from os import getcwd
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
    wiki_obj = _get_wiki_obj_from_path(path)

    if wiki_obj.is_leaf and not wiki_obj.is_binary:
        if request.args.get('ref', None) and g.wiki.has_vcs:
            wiki_obj.ref(request.args.get('ref'))

        response = render_template(
            'view.html',
            file=wiki_obj,
            files=wiki_obj.items(),
            refs=wiki_obj.refs,
            rendered=wiki_obj.render(),
        )
    elif wiki_obj.is_node:
        response = render_template(
            'list.html',
            file=wiki_obj,
            files=wiki_obj.items(),
        )
    else:
        (mimetype, enc) = guess_type(wiki_obj.path)
        response = Response(
            wiki_obj.render(),
            mimetype=mimetype,
        )
    return response


@app.route('/_create_folder_/', methods=['GET', 'POST'])
@app.route('/_create_folder_/<path:path>', methods=['GET', 'POST'])
def create_folder(path=None):
    wiki_obj = _get_wiki_obj_from_path(path)

    if not wiki_obj.is_node or not wiki_obj.is_editable:
        abort(500)

    if request.form.get('save', None):
        dir_name = request.form.get('dir_name')
        try:
            new_directory = wiki_obj.create_directory(dir_name)
            flash('New folder created', 'success')
            return redirect(url_for('view', path=new_directory.path))

        except PathExists:
            app.logger.error(format_exc())
            flash('There is already a folder by that name', 'error')

        except Exception as e:
            app.logger.error(format_exc())
            flash('There was a problem creating your folder: %s' % e, 'error')

    return render_template('create_folder.html', file=wiki_obj)


@app.route('/_delete_/<path:path>', methods=['GET', 'POST'])
def delete(path):
    wiki_obj = _get_wiki_obj_from_path(path)

    if not wiki_obj.is_editable:
        abort(500)

    if request.form.get('delete', None):
        try:
            parent = wiki_obj.ancestor()
            wiki_obj.delete()
            flash('\'%s\' successfull deleted' % wiki_obj.name, 'success')
            return redirect(url_for('view', path=parent.path))

        except Exception as e:
            app.logger.error(format_exc())
            msg = 'There was a problem deleting \'%s\': %s' % (wiki_obj.name, e)
            flash(msg, 'error')

    return render_template('delete.html', file=wiki_obj)


@app.route('/_create_file_/', methods=['GET', 'POST'])
@app.route('/_create_file_/<path:path>', methods=['GET', 'POST'])
def create_file(path=None):
    wiki_obj = _get_wiki_obj_from_path(path)

    if not wiki_obj.is_node or not wiki_obj.is_editable:
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
            new_file = wiki_obj.create_file(filename)
            new_file.content(content=filecontent)
            new_file.save(comment=request.form.get('message', None))
            flash('File created with the provided content', 'success')

            response = redirect(url_for('view', path=wiki_obj.path))

        except PathExists:
            app.logger.error(format_exc())
            flash('There is already a file by that name', 'error')

        except Exception as e:
            app.logger.error(format_exc())
            flash('There was a problem saving your file : %s' % e, 'error')
    else:
        response = render_template(
            'create.html',
            file=wiki_obj,
            filename=filename,
            filecontent=filecontent,
        )
    return response


@app.route('/_edit_/<path:path>', methods=['GET', 'POST'])
def edit(path):
    wiki_obj = _get_wiki_obj_from_path(path)

    if not wiki_obj.is_leaf or wiki_obj.is_binary or not wiki_obj.is_editable:
        abort(500)

    if request.form.get('save') or request.form.get('quiet_save'):
        try:
            wiki_obj.content(content=request.form.get('content'))
            wiki_obj.save(comment=request.form.get('message', None))
            flash('File saved with the new provided content', 'success')
        except Exception as e:
            app.logger.error(format_exc())
            flash('There was a problem saving your file : %s' % e, 'error')

    if request.form.get('save'):
        response = redirect(url_for('view', path=wiki_obj.path))
    else:
        response = render_template(
            'edit.html',
            file=wiki_obj,
            files=wiki_obj.items(),
            file_content=escape(wiki_obj.content()),
        )
    return response


@app.route('/search/', methods=['GET', 'POST'])
def search():
    json_string = json_dumps({})
    if request.args.get('q'):
        term = request.args.get('q')
        hits = g.wiki.search(term)

        hits_dicts = []
        for hit in hits:
            hit_text = ': '.join((term, hit.name))
            hits_dicts.append({
                'hit': hit_text,
                'path': hit.path,
            })

        json_string = json_dumps({
            'searched': True,
            'term': term,
            'hits': len(hits),
            'results': hits_dicts,
        })

    return Response(json_string, mimetype='application/json')


@app.route('/refresh/')
def refresh():
    try:
        info = g.wiki.refresh()
        flash('Your wiki has been refreshed. %s' % info, 'success')
    except Exception as e:
        app.logger.error(e)
        app.logger.error(format_exc())
        flash('Error refreshing git repository', 'error')

    return redirect(url_for('view'))


@app.route('/_raw_/<path:path>')
def raw(path):
    try:
        wiki_obj = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    if not wiki_obj.is_leaf:
        abort(404)

    return Response(wiki_obj.content(), mimetype='text/plain')


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
        config.get('WIKI_DIR', getcwd()),
        has_vcs=config.get('WIKI_GIT_SUPPORT', False),
    )


def _get_wiki_obj_from_path(path):
    if not path:
        path = g.wiki.get_root().path

    try:
        wiki_obj = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    return wiki_obj
