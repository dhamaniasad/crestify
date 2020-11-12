# -*- coding: utf-8 -*-
from flask import Flask
from flask_assets import Environment
from flask_script import Manager
import flask_restful as restful
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
import os
import errno
from raven.contrib.flask import Sentry
import redis
import mixpanel
import hashids


# Setup Application
app = Flask(__name__)
app.config.from_object('defaults')
app.config.from_envvar('CRESTIFY_CONFIG_FILE')
manager = Manager(app)
api = restful.Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["X-Requested-With", "Content-Type"])
sentry = Sentry(app)
redis = redis.StrictRedis.from_url(app.config['REDIS_URI'])
mixpanel = mixpanel.Mixpanel(app.config['MIXPANEL_PROJECT_TOKEN'])
hashids = hashids.Hashids(app.config['HASHIDS_SALT'])

# Create the upload directory and catch OSError if it already exists
try:
    os.makedirs(app.config['CRESTIFY_UPLOAD_DIRECTORY'])
    app.logger.info("Created upload directory:" + app.config['CRESTIFY_UPLOAD_DIRECTORY'])
except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(app.config['CRESTIFY_UPLOAD_DIRECTORY']):
        pass
    else:
        raise


# Setup assets
assets = Environment(app)
assets_output_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'gen')

if app.config['DEBUG']:
    toolbar = DebugToolbarExtension(app)
