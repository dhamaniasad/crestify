from crestify import app, hashids
from crestify.models import Bookmark
from flask import render_template, abort


@app.route('/pub/<int:bookmark_id>', methods=['GET'])
def bookmark_share(bookmark_id):
    if bookmark_id < 36000:  # When this was implemented, there were about those many bookmarks in the database
        query = Bookmark.query.get(bookmark_id)
        return render_template("public/bookmark_share.html", bookmark=query)
    else:
        return abort(403)


@app.route('/public/<string:bookmark_id>', methods=['GET'])
def bookmark_public(bookmark_id):
    bookmark_id = hashids.decode(str(bookmark_id))[0]
    query = Bookmark.query.get(bookmark_id)
    return render_template("public/bookmark_share.html", bookmark=query)
