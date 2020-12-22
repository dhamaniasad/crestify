from crestify.models import Bookmark
from collections import OrderedDict
import datetime
import json


exports = OrderedDict(bookmarks=[], recommendations=[])

userid = 1

query = Bookmark.query.filter_by(user=userid, deleted=False).order_by(
    Bookmark.added_on.desc()
)

for bookmark in query:
    data = OrderedDict(
        article__excerpt=bookmark.description,
        favorite=False,
        date_archived=None,
        article__url=bookmark.main_url,
        date_added=bookmark.added_on.strftime("%Y-%m-%dT%H:%M:%S"),
        date_favorited=None,
        article__title=bookmark.title,
        archive=False,
    )
    exports["bookmarks"].append(data)
