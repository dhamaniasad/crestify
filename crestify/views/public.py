from crestify import app, hashids
from crestify.models import Bookmark
from flask import render_template


@app.route('/public/<string:bookmark_id>', methods=['GET'])
def bookmark_public(bookmark_id):
    bookmark_id = hashids.decode(bookmark_id)[0]
    query = Bookmark.query.get(bookmark_id)
    return render_template("public/bookmark_share.html", bookmark=query)
