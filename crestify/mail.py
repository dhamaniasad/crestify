# -*- coding: utf-8 -*-
from flask_mail import Mail
from crestify import app

# Setup mail config
mail = Mail(app)
