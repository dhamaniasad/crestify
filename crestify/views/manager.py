# -*- coding: utf-8 -*-
'''Routes and Views for the Bookmark Manager'''
from flask import render_template, request, redirect, url_for, abort, Markup, jsonify
from flask_security import login_required, current_user
from crestify import app, redis, hashids
from crestify.models import Bookmark, User, Tag, db, Tab
from crestify.forms import NewBookmarkForm, SearchForm, DeleteForm, EditBookmarkForm, NewTabSetForm
from crestify.services import bookmark, tab
from crestify.tasks import bookmark_tasks
from sqlalchemy_searchable import search
from sqlalchemy.sql import or_


@app.context_processor
def inject_addform():
    return dict(add_form=NewBookmarkForm())


@app.context_processor
def inject_user_tags():
    if not current_user.is_authenticated:
        return {
            "user_tags": None
        }
    else:
        user_tags = Tag.query.filter(Tag.user == current_user.id,
                                     Tag.count > 0).all()
        user_tags.sort(key=lambda k: k.text.lower())
        user_tags = [{'text': tag.text.encode('utf-8'),
                      'value': tag.text.encode('utf-8'),
                      'count': tag.count} for tag in user_tags if
                     tag.text != '']
        return {
            "user_tags": user_tags
        }


@app.context_processor
def inject_bmark_count():
    if current_user.is_authenticated:
        bookmark_count = Bookmark.query.filter_by(user=current_user.id, deleted=False).count()
        return dict(bookmark_count=bookmark_count)
    return dict(bookmark_count=0)


@app.context_processor
def inject_id_hasher():
    def hash_id(_id):
        return hashids.encode(_id)
    return dict(hash_id=hash_id)


@app.route('/manager')
@login_required
def manager_home():
    '''
    Return the Manager Home page
    '''
    return redirect(url_for('bookmark_list'))


@app.route('/manager/bookmark', methods=['GET'])
@login_required
def bookmark_list():
    '''
    Returns a list of bookmarks
    '''
    search_form = SearchForm(request.args)
    # Create the base query
    # After this query is created, we keep iterating over it until we reach the desired level of filtering
    query = Bookmark.query.filter_by(user=current_user.id, deleted=False).order_by(Bookmark.added_on.desc())
    # Get list of tags we'll be filtering by
    tag_args = request.values.getlist('tags')
    if len(tag_args) == 0:
        tag_args = None
    else:
        for tag in tag_args:
            # Check is any of the tags for the bookmark match up with tag
            query = query.filter(Bookmark.tags.any(tag))
    # This means that the search form has been used
    if search_form.query.data is not None:
        # Search query type can be either basic, full text, or url
        # This is basic search, which searches in the bookmark titles and descriptions
        if search_form.parameter.data == 'basic':
            query = search(query, search_form.query.data, vector=Bookmark.search_vector)  # XXX is this safe?
            user_count = Bookmark.query.filter_by(user=current_user.id, deleted=False).count()
            # Postgres full text search seems to fail when using non-ASCII characters
            # When the failure happens, all the bookmarks are returned instead
            # We check if this has happened, and if it has, we fall back to non-indexed search instead
            if query.count() == user_count:
                query = query.filter(or_(Bookmark.title.contains(search_form.query.data),
                                         Bookmark.description.contains(search_form.query.data)))
        elif search_form.parameter.data == 'ft':
            # We will search over the entire contents of the page here
            query = search(query, search_form.query.data, vector=Bookmark.fulltext_vector)
            user_count = Bookmark.query.filter_by(user=current_user.id, deleted=False).count()
            if query.count() == user_count:
                query = query.filter(Bookmark.full_text.contains(search_form.query.data))
        # URL search lets you filter by domains or other parts of the url
        elif search_form.parameter.data == 'url':
            query = query.filter(Bookmark.main_url.contains(search_form.query.data))
        else:
            pass
    # Context view takes you to the page the bookmark with a specific id is present on
    # Here the id is used to know which bookmark should be highlighted
    try:
        context_id = request.args['bid']
    except KeyError:
        context_id = 0
    # Pagination, with defaulting to the first page
    page = request.args.get('page', 1, type=int)
    # Users are allowed to specify how many bookmarks they want per page
    bookmarks_per_page = User.query.get(current_user.id).bookmarks_per_page
    # Paginate the results of our query
    pagination = query.paginate(page, per_page=bookmarks_per_page, error_out=False)
    delete_form = DeleteForm()
    return render_template("manager/bookmark_list.html",
                           pagination=pagination,
                           search_form=search_form,
                           delete_form=delete_form,
                           context_id=context_id,
                           tag_args=tag_args)


@app.route('/manager/bookmark/', methods=['GET'])
@login_required
def bookmark_list_redir():
    return redirect(url_for('bookmark_list'))


@app.route('/manager/bookmark/new', methods=['GET', 'POST'])
@login_required
def bookmark_new():
    '''
    BEWARE! No sanitation has been done yet!
    '''
    form = NewBookmarkForm(csrf_enabled=False)
    if request.method == 'GET':
        return render_template("manager/bookmark_new.html", form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            # If the form is validated, we hand off the new bookmark
            # creation to the bookmark.new function
            new_bookmark = bookmark.new(title=form.title.data,
                                        url=form.main_url.data,
                                        description=form.description.data,
                                        tags=form.tags.data,
                                        user_id=current_user.id)
            # And we queue the async background jobs
            bookmark_tasks.readable_extract.delay(new_bookmark)
            bookmark_tasks.fulltext_extract.delay(new_bookmark)
            # Title and description do not compulsorily need to be provided
            # But we still need them, so if they aren't provided, we'll fetch them ourselves
            if not new_bookmark.description:
                bookmark_tasks.fetch_description.delay(new_bookmark)
            if not new_bookmark.title:
                bookmark_tasks.fetch_title.delay(new_bookmark)
            return redirect(url_for('bookmark_list'))
        else:
            print("%s validation failed" % form.main_url.data)
            return render_template("manager/bookmark_new.html", form=form)


@app.route('/manager/bookmark/edit/<string:bookmark_id>', methods=['GET', 'POST'])
@login_required
def bookmark_edit(bookmark_id=None):
    if bookmark_id:
        bookmark_id = hashids.decode(str(bookmark_id))[0]  # Apparently, hashids.decode doesn't accept unicode input
        bookmarkobj = _get_user_object_or_404(Bookmark,
                                              bookmark_id,
                                              current_user.id)
        if bookmarkobj.tags:
            bookmarkobj.tags_2 = ','.join(bookmarkobj.tags).encode('utf-8')
        form = EditBookmarkForm(obj=bookmarkobj,
                                csrf_enabled=False)
        if form.validate_on_submit():
            bookmark.edit(id=bookmark_id,
                          title=form.title.data,
                          description=form.description.data,
                          tags=form.tags_1.data,
                          user_id=current_user.id)
            return redirect(url_for('bookmark_list'))
        return render_template("manager/bookmark_edit.html",
                               form=form,
                               bookmark_obj=bookmarkobj)


@app.route('/manager/bookmark/read/<string:bookmark_id>', methods=['GET'])
@login_required
def bookmark_reader(bookmark_id=None):
    bookmark_id = hashids.decode(str(bookmark_id))[0]
    bookmarkobj = _get_user_object_or_404(Bookmark, bookmark_id, current_user.id)
    if bookmarkobj.readability_html is None:
        return abort(404)
    else:
        readable_html = Markup(bookmarkobj.readability_html)
        return render_template("manager/bookmark_readable.html",
                               readable_html=readable_html,
                               title=bookmarkobj.title,
                               link=bookmarkobj.main_url)


@app.route('/manager/bookmark/context/<string:bookmark_id>', methods=['GET'])
@login_required
def bookmark_context(bookmark_id):
    bookmark_id = hashids.decode(str(bookmark_id))[0]
    query = db.session.query(Bookmark.id).filter_by(user=current_user.id, deleted=False).order_by(Bookmark.added_on.desc()).all()
    count = query.index((bookmark_id,)) + 1
    page_num = int(count/(current_user.bookmarks_per_page) + 1)
    bookmark_id = hashids.encode(bookmark_id)
    return redirect(url_for('bookmark_list', page=page_num, bid=bookmark_id))


@app.route('/manager/bookmark/delete', methods=['POST'])
@login_required
def bookmark_delete():
    deleteform = DeleteForm(request.form)
    if deleteform.validate_on_submit():
        bookmark.delete(id=deleteform.id.data,
                        user_id=current_user.id)
    return redirect(url_for('bookmark_list'))


@app.route('/manager/tabs', methods=['GET'])
@login_required
def tabs_list():
    query = Tab.query.filter_by(user=current_user.id).order_by(Tab.added_on.desc())
    page = request.args.get('page', 1, type=int)
    bookmarks_per_page = User.query.get(current_user.id).bookmarks_per_page
    pagination = query.paginate(page, per_page=bookmarks_per_page, error_out=False)
    return render_template('manager/tabs_list.html', pagination=pagination)


@app.route('/manager/tabs/<tab_id>', methods=['GET'])
@login_required
def tabs_set(tab_id=None):
    tabobj = _get_user_object_or_404(Tab, tab_id, current_user.id)
    return render_template('manager/tab_view.html', tab=tabobj)


@app.route('/manager/tabs/new', methods=['POST', 'GET'])
@login_required
def new_tab_set():
    id = request.args.get('id', type=str)
    r = redis.get(id)
    if r is None:
        abort(404)
    else:
        tabobj = TabsSetObject(id)
        form = NewTabSetForm(csrf_enabled=False, obj=tabobj)
        if form.validate_on_submit():
            tabs = redis.get(form.uuid.data)
            tab.new(current_user.id, tabs, form.title.data)
            return redirect(url_for('tabs_list'))
    return render_template('manager/tabs_new.html', form=form)


def _get_user_object_or_404(model, bookmark_id, user, code=404):
    ''' get an object by id and owner user or raise an abort '''
    result = model.query.filter_by(id=bookmark_id, user=user).first()
    return result or abort(code)


class TabsSetObject:
    def __init__(self, uuid):
        self.uuid = uuid


# AJAX requests
@app.route('/_edit_tab_title', methods=['POST'])
@login_required
def _edit_tab_title():
    if len(request.form['value']) > 255:
        return jsonify({'status': 'error', 'msg': 'Title cannot be more than 255 characters long!'}), 400
    else:
        edit_tab = tab.edit_title(request.form['pk'], current_user.id, request.form['value'])
        if edit_tab:
            return jsonify(''), 200
        else:
            return jsonify({'status': 'error', 'msg': 'Editing failed!'}), 431


@app.route('/_delete_tab_set', methods=['POST'])
@login_required
def _delete_tab_set():
    delete_tab = tab.delete(request.form['tabSetId'], current_user.id)
    if delete_tab is False:
        return jsonify({'status': 'error', 'msg': 'Deletion Failed'}), 431
    else:
        return jsonify({'status': 'success', 'msg': 'Deletion Successful'}), 200
