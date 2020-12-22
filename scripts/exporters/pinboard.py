from crestify.models import Bookmark
from collections import OrderedDict
import datetime
import json


exports = []

userid = 1

query = Bookmark.query.filter_by(user=userid, deleted=False).order_by(
    Bookmark.added_on.desc()
)

for bookmark in query:
    data = OrderedDict(
        href=bookmark.main_url,
        description=bookmark.title,
        extended=bookmark.description,
        meta="",
        hash="",
        time=bookmark.added_on.strftime("%Y-%m-%dT%H:%M:%SZ"),
        shared="no",
        toread="no",
        tags=" ".join(bookmark.tags),
    )
    print(json.dumps(data))
    exports.append(data)
