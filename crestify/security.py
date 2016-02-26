# -*- coding: utf-8 -*-
from flask_security import Security, SQLAlchemyUserDatastore
from crestify import app
from models import db, User, Role
from forms import ExtendedRegisterForm

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
