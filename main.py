from crestify import app
from crestify.models import db
from crestify.security import *
from crestify.views.manager import *
from crestify.views.settings import *
from crestify.views.site import *
from crestify.views.apiservice import *
from crestify.views.public import *
from crestify.views.admin import *
from crestify.tasks import *
from crestify.signal_handlers import *
from crestify.mail import Mail
from crestify import manager


if __name__ == "__main__":
    # db.create_all()
    manager.run()
