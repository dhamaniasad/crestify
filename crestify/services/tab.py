from crestify.models import Tab, db
import shortuuid
import json
import datetime


def new(user_id, tabs, title):
    tabs = json.loads(tabs)
    new_tabs = Tab()
    new_tabs.user = user_id
    new_tabs.id = shortuuid.uuid()
    new_tabs.title = title
    new_tabs.tabs = tabs
    new_tabs.added_on = datetime.datetime.utcnow()
    for tab in tabs:
        if "title" in tab and "url" in tab:  # Each tab MUST have a title and a URL
            pass
        else:
            del new_tabs
            return False
    db.session.add(new_tabs)
    db.session.commit()


def edit_title(id, user_id, title):
    try:
        edit_tab = Tab.query.get(id)
    except:
        return False
    if edit_tab:
        if edit_tab.user == user_id:
            edit_tab.title = title
            db.session.commit()
            return True
        else:
            return False
    else:
        return False


def delete(id, user_id):
    try:
        delete_tabs = Tab.query.get(id)
    except:
        print("exception")
        return False
    if delete_tabs:
        if delete_tabs.user == user_id:
            db.session.delete(delete_tabs)
            db.session.commit()
            print("deleted")
            return True
        else:
            return False
    else:
        return False
