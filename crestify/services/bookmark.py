# -*- coding: utf-8 -*-
from datetime import datetime
from crestify.models import db, Bookmark, User, Tag
from crestify.services import archive


def new(url, user_id, description=None, tags=None, title=None, added=None):
    new_bookmark = Bookmark()
    new_bookmark.main_url = url[:2000]
    if title is not None:
        new_bookmark.title = title[:1024]
    if description is not None:
        new_bookmark.description = description[:256]
    new_bookmark.user = user_id
    if added is None:
        new_bookmark.added_on = datetime.utcnow()
    else:
        try:
            datetime.datetime.utcfromtimestamp(added)
            new_bookmark.added_on = added  # UNIX timestamp in seconds since epoch, only
        except ValueError:
            new_bookmark.added_on = datetime.utcnow()
    new_bookmark.deleted = False
    if tags is not None:
        tags = tags.split(",")
        new_bookmark.tags = tags
        for tag in tags:
            # If tag is present, increment counter by one, or create if not present
            get_tag = Tag.query.filter_by(text=tag, user=user_id).first()
            if not get_tag:
                new_tag = Tag(text=tag, user=user_id)
                new_tag.count = 1
                db.session.add(new_tag)
            else:
                get_tag.count += 1
    db.session.add(new_bookmark)
    db.session.commit()
    # Send off for archiving
    archive.do_archives(new_bookmark)
    return new_bookmark


def delete(id, user_id):
    delete_bookmark = Bookmark.query.get(id)
    if delete_bookmark.user == user_id:
        delete_bookmark.deleted = True
        tags = delete_bookmark.tags
        # If tags are present, we'll want to decrement their counts here
        if tags and len(tags) > 0:
            for tag in tags:
                get_tag = Tag.query.filter_by(text=tag, user=user_id).first()
                if get_tag:
                    get_tag.count -= 1
        db.session.commit()


def per_page(user_id, per_page):
    per_page_bookmarks = User.query.get(user_id)
    per_page_bookmarks.bookmarks_per_page = per_page
    db.session.commit()


def edit(id, user_id, title=None, description=None, tags=None):
    edit_bookmark = Bookmark.query.get(id)
    if title is not None:
        edit_bookmark.title = title[:1024]
    if description is not None:
        edit_bookmark.description = description[:256]
    if tags != "" or tags is not None:
        if type(tags) is str:
            ls1 = edit_bookmark.tags or []
            ls2 = tags.split(",") or []
            # Compute deltas between new and current tags
            added_tags = set(ls1 + ls2) - set(ls1)
            removed_tags = set(ls1 + ls2) - set(ls2)
            for tag in added_tags:
                get_tag = Tag.query.filter_by(text=tag, user=user_id).first()
                if not get_tag:
                    new_tag = Tag(text=tag, user=user_id)
                    new_tag.count = 1
                    db.session.add(new_tag)
                else:
                    get_tag.count += 1
            for tag in removed_tags:
                get_tag = Tag.query.filter_by(text=tag, user=user_id).first()
                if not get_tag:
                    pass
                else:
                    get_tag.count -= 1
            edit_bookmark.tags = ls2
    db.session.commit()


def api_edit(id, tags, user_id):
    edit_bookmark = Bookmark.query.get(id)
    ls1 = edit_bookmark.tags or []
    ls2 = tags
    added_tags = None
    removed_tags = None
    if tags != [""]:
        if ls1:
            added_tags = set(ls1 + ls2) - set(ls1)
            removed_tags = set(ls1 + ls2) - set(ls2)
        else:
            added_tags = set(ls2)
        if added_tags:
            for tag in added_tags:
                get_tag = Tag.query.filter_by(text=tag, user=user_id).first()
                if not get_tag:
                    new_tag = Tag(text=tag, user=user_id)
                    new_tag.count = 1
                    db.session.add(new_tag)
                else:
                    get_tag.count += 1
        edit_bookmark.tags = ls2
    else:
        removed_tags = set(edit_bookmark.tags)
        edit_bookmark.tags = []
    if removed_tags:
        for tag in removed_tags:
            get_tag = Tag.query.filter_by(text=tag, user=user_id).first()
            if not get_tag:
                pass
            else:
                get_tag.count -= 1
    db.session.commit()
