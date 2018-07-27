# -*- coding: utf-8 -*-
from flask import request
from crestify import api, redis, hashids
from flask_restful import Resource, reqparse
from crestify.models import Bookmark, User, Tag, db
from crestify.services import bookmark
from crestify.tasks import bookmark_tasks
from functools import wraps
import shortuuid
import urllib
import urlparse
import arrow
from flask_security import utils as security_utils

parser = reqparse.RequestParser()
parser.add_argument('url', type=str)
parser.add_argument('email', type=str)
parser.add_argument('apikey', type=str)
parser.add_argument('title', type=str)
parser.add_argument('addedon', type=int)  # Send in milliseconds since epoch only
parser.add_argument('tags', type=str)  # Send comma separated string
parser.add_argument('id', type=str)
parser.add_argument('tabs', location='json')
parser.add_argument('password', type=str)


def require_auth(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        args = parser.parse_args()
        query = User.query.filter_by(email=urllib.unquote(args['email']),
                                     api_key=urllib.unquote(args['apikey'])).first()
        if query is not None:
            userid = query.id
            return view_function(userid, args)
        else:
            return {'message': 'Authentication failed'}, 401

    return decorated_function


def require_json(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        print request.json
        print "request data", request.data
        if not request.get_json():
            return {'message': 'JSON Expected.'}, 500
        else:
            return view_function()

    return decorated_function


class CheckURL(Resource):
    method_decorators = [require_auth]

    def post(self, userid, args):
        if args['url'] is not None:
            parsed_url = urlparse.urlparse(urllib.unquote(args['url']))
            url_scheme = "{}://".format(parsed_url.scheme)
            parsed_url = parsed_url.geturl().replace(url_scheme, '', 1)
            query = Bookmark.query.filter(Bookmark.main_url.endswith(parsed_url), Bookmark.user == userid,
                                          Bookmark.deleted == False).order_by(Bookmark.added_on.desc()).first()
            if query:
                return {'message': 'You have this URL bookmarked', 'added': arrow.get(query.added_on).humanize(),
                        'timestamp': arrow.get(query.added_on).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'id': hashids.encode(query.id)}, 200
            else:
                return {'message': 'You do not have this URL bookmarked'}, 404


class CheckURLInfo(Resource):
    method_decorators = [require_auth]

    def post(self, userid, args):
        if args['url'] is not None:
            parsed_url = urlparse.urlparse(args['url'])
            url_scheme = "{}://".format(parsed_url.scheme)
            parsed_url = parsed_url.geturl().replace(url_scheme, '', 1)
            query = Bookmark.query.filter(Bookmark.main_url.endswith(parsed_url), Bookmark.user == userid,
                                          Bookmark.deleted == False).order_by(Bookmark.added_on.desc()).first()
            if query:
                current_tags = None
                if query.tags:
                    current_tags = ','.join(query.tags)
                user_tags = Tag.query.filter(Tag.user == userid, Tag.count > 0).all()
                user_tags.sort(key=lambda k: k.text.lower())
                [user_tags.remove(tag) for tag in user_tags if tag.text == '']
                if user_tags:
                    user_tags = ','.join([tag.text for tag in user_tags])
                return {'message': 'You have this URL bookmarked', 'tags': current_tags, 'tagopts': user_tags,
                        'id': hashids.encode(query.id)}, 200
            else:
                return {'message': 'You do not have this URL bookmarked'}, 404


class AddURL(Resource):
    method_decorators = [require_auth]

    def post(self, userid, args):
        if args['addedon']:
            added = args[
                        'addedon'] / 1000  # Convert timestamp from milliseconds since epoch to seconds(Chrome sends millisecs)
            new_bookmark = bookmark.new(title=urllib.unquote(args['title']), url=urllib.unquote(args['url']),
                                        user_id=userid, tags=args['tags'])
        else:
            new_bookmark = bookmark.new(title=urllib.unquote(args['title']), url=urllib.unquote(args['url']),
                                        user_id=userid)
        bookmark_tasks.readable_extract.delay(new_bookmark)
        bookmark_tasks.fulltext_extract.delay(new_bookmark)
        bookmark_tasks.fetch_description.delay(new_bookmark)
        return {'message': 'URL bookmarked', 'id': hashids.encode(new_bookmark.id)}, 200


class EditBookmark(Resource):
    method_decorators = [require_auth]

    def post(self, userid, args):
        if args['id']:
            id = hashids.decode(args['id'])[0]
            tags = urllib.unquote(args['tags'])
            tags = tags.split(',')
            edit_bookmark = bookmark.api_edit(id=id,
                                              tags=tags,
                                              user_id=userid)
        else:
            return {'message': 'No ID Supplied'}, 404
        return {'message': 'Bookmark Modified'}, 200


class CheckAuth(Resource):
    def post(self):
        args = parser.parse_args()
        user = User.query.filter_by(email=urllib.unquote(args['email']), api_key=urllib.unquote(args['apikey'])).first()
        if user is not None:
            return {'message': 'Authenticated Successfully'}, 200
        else:
            return {'message': 'Authentication Failed'}, 401


class CheckPassword(Resource):
    def post(self):
        args = parser.parse_args()
        email = args['email']
        password = args['password']
        if email is None or password is None:
            return {'message': "Email or password empty"}, 401
        user = User.query.filter_by(email=args["email"]).first()
        if security_utils.verify_password(password, user.password):
            return {'message': 'Login Successful', 'apikey': user.api_key}, 200
        return {'message': 'Login Failed'}, 401


class DeleteBookmark(Resource):
    method_decorators = [require_auth]

    def post(self, userid, args):
        if args['id']:
            id = hashids.decode(args['id'])[0]
            delete_bookmark = bookmark.delete(id=id, user_id=userid)
        else:
            return {'message': 'No ID Supplied'}, 404
        return {'message': 'Bookmark Deleted'}, 200


class AddTabs(Resource):
    method_decorators = [require_auth]

    def post(self, userid, args):
        if args['tabs']:
            print type(args['tabs'])
            uuid = shortuuid.uuid()
            r = redis.set(uuid, urllib.unquote(args['tabs']))
            #  Expire Redis key in 10 minutes
            redis.expire(uuid, 600)
            return {'id': uuid}


api.add_resource(CheckURL, '/api/check')
api.add_resource(AddURL, '/api/add')
api.add_resource(CheckAuth, '/api/authenticate')
api.add_resource(CheckURLInfo, '/api/checkinfo')
api.add_resource(EditBookmark, '/api/edit')
api.add_resource(DeleteBookmark, '/api/delete')
api.add_resource(AddTabs, '/api/tabs/add')
api.add_resource(CheckPassword, '/api/login')
