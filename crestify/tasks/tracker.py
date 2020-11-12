from crestify.tasks import celery
from crestify import mixpanel
from crestify.models import User, Bookmark
from datetime import datetime


@celery.task(name="track_mixpanel")
def track_mixpanel(userid, event):
    user = User.query.get(userid)
    bookmarks = Bookmark.query.filter_by(user=user.id, deleted=False).count()
    mixpanel.people_set(user.id, {
        "$first_name": user.first_name,
        "$last_name": user.last_name,
        "$email": user.email,
        "$created": user.confirmed_at,
        "bookmarks": bookmarks,
        "last_activity": datetime.utcnow()
    })
    mixpanel.track(userid, event)
