from crestify import app
from crestify.services import user_service
from flask_security.signals import user_confirmed


@user_confirmed.connect_via(app)
def on_confirmed(obj, user, **extra):
    user_service.regenerate_api_key(user.id)
