import os
import json
import traceback
import mimetypes

from flask import (render_template, flash, redirect, url_for,
                   abort, g, request, escape, Response)

from pendium import app
from pendium.filesystem import (Wiki, PathNotFound, PathExists)


@app.route('/')
def index():
    p         = g.wiki.root()
    home_file = get_home()
    return render_template('index.html',
                           file=p,
                           files=p.items(),
                           home_file=home_file)


def get_home(path=''):
    home_file = None
    try:
        home_path = os.path.join(path, app.config['DEFAULT_HOME_FILE'])
        home_file = g.wiki.get(home_path)
        home_file = home_file.render()
    except:
        pass

    return home_file


@app.route('/_create_folder_/',            methods=['GET', 'POST'])
@app.route('/_create_folder_/<path:path>', methods=['GET', 'POST'])
def create_folder(path=None):
    p = g.wiki.root()
    if path is not None:
        try:
            p = g.wiki.get(path)
        except PathNotFound:
            abort(404)

    if not p.is_node:
        abort(500)

    if not p.editable:
        abort(500)

    foldername = None

    if request.form.get('save', None):
        foldername = request.form.get('foldername')
        try:
            p.create_directory(foldername)
            flash("New folder created", 'success')
            return redirect(url_for('view', path=p.path))
        except PathExists:
            app.logger.error(traceback.format_exc())
            flash("There is already a folder by that name", 'error')

        except Exception, e:
            app.logger.error(traceback.format_exc())
            flash("There was a problem creating your folder: %s" % e, 'error')

    return render_template('create_folder.html',
                           file=p,
                           foldername=foldername)


@app.route('/_delete_/<path:path>', methods=['GET', 'POST'])
def delete(path):
    try:
        p = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    if not p.editable:
        abort(500)

    if request.form.get('delete', None):
        try:
            parent = p.ancestor()
            p.delete()
            flash("'%s' successfull deleted" % p.name, 'success')
            return redirect(url_for('view', path=parent.path))

        except Exception, e:
            app.logger.error(traceback.format_exc())
            msg = "There was a problem deleting '%s': %s" % (p.name, e)
            flash(msg, 'error')

    return render_template('delete.html', file=p)


@app.route('/_create_file_/',            methods=['GET', 'POST'])
@app.route('/_create_file_/<path:path>', methods=['GET', 'POST'])
def create_file(path=None):
    p = g.wiki.root()
    if path is not None:
        try:
            p = g.wiki.get(path)
        except PathNotFound:
            abort(404)

    if not p.is_node:
        abort(500)

    if not p.editable:
        abort(500)

    filename    = None
    filecontent = None

    if request.form.get('save', None):
        filename    = request.form.get('filename')
        extension   = request.form.get('extension')
        filecontent = request.form.get('content')
        try:
            if extension != '':
                filename += '.' + extension
            new_file = p.create_file(filename)
            new_file.content(content=filecontent)
            new_file.save(comment=request.form.get('message', None))
            flash("File created with the provided content", 'success')

            return redirect(url_for('view', path=p.path))
        except PathExists:
            app.logger.error(traceback.format_exc())
            flash("There is already a file by that name", 'error')

        except Exception, e:
            app.logger.error(traceback.format_exc())
            flash("There was a problem saving your file : %s" % e, 'error')

    return render_template('create.html',
                           file=p,
                           filename=filename,
                           extensions=get_extensions(),
                           filecontent=filecontent)


@app.route('/_edit_/<path:path>', methods=['GET', 'POST'])
def edit(path):
    try:
        p = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    if not p.is_leaf:
        abort(500)

    if p.is_binary:
        abort(500)

    if not p.editable:
        abort(500)

    if request.form.get('save', None) or request.form.get('quiet_save', None):
        try:
            p.content(content=request.form.get('content'))
            p.save(comment=request.form.get('message', None))
            flash("File saved with the new provided content", 'success')
        except Exception, e:
            app.logger.error(traceback.format_exc())
            flash("There was a problem saving your file : %s" % e, 'error')

    if request.form.get('save'):
        return view(path)

    return render_template('edit.html',
                           file=p,
                           files=p.items(),
                           file_content=escape(p.content()))


@app.route('/<path:path>', methods=['GET'])
def view(path, ref=None):
    try:
        p = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    if p.is_leaf and not p.is_binary:
        if not p.can_render:
            flash("No renderer found, fallback to plain text", 'warning')

        if request.args.get('ref', None) and g.wiki.has_vcs:
            p.ref(request.args.get('ref'))

        return render_template('view.html',
                               file=p,
                               files=p.items(),
                               refs=p.refs,
                               rendered=p.render())
    elif p.is_node:
        home_file = get_home(p.path)
        return render_template('list.html',
                               file=p,
                               files=p.items(),
                               home_file=home_file)
    else:
        (mimetype, enc) = mimetypes.guess_type(p.path)
        return Response(p.render(), mimetype=mimetype)


@app.route('/search/', methods=['GET', 'POST'])
def search():
    js = json.dumps({})
    if request.args.get('q', None):
        term = request.args.get('q')
        app.logger.debug("Searching for '%s'" % term)
        hits = g.wiki.search(term)

        hits_dicts = []
        for hit in hits:
            hits_dicts.append({'hit': term + ": " + hit.name,
                               'path': hit.path})

        js = json.dumps({
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
        flash("Your wiki has been refreshed. %s" % info, 'success')
    except Exception, e:
        app.logger.error(e)
        app.logger.error(traceback.format_exc())
        flash("Error refreshing git repository", 'error')

    return redirect(url_for('index'))


@app.route('/_raw_/<path:path>')
def raw(path):
    try:
        p = g.wiki.get(path)
    except PathNotFound:
        abort(404)

    if p.is_leaf:
        return Response(p.content(), mimetype='text/plain')

    abort(404)


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
    g.wiki = Wiki(config['WIKI_DIR'],
                  extensions       = config.get('WIKI_EXTENSIONS', {}),
                  default_renderer = config.get('WIKI_DEFAULT_RENDERER', None),
                  plugins_config   = config.get('WIKI_PLUGINS_CONFIG', {}),
                  has_vcs          = config.get('WIKI_GIT_SUPPORT', False))


def get_extensions():
    extensions = []
    for wiki_ext in app.config['WIKI_EXTENSIONS'].values():
        extensions += wiki_ext
    return extensions
