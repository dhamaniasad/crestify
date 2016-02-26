DEBUG = False

SECRET_KEY = 'insecure'

SQLALCHEMY_DATABASE_URI = 'postgresql://crestify:crestify@localhost/crestify'

SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_EMAIL_SENDER = 'noreply@example.com'
SECURITY_CONFIRMABLE = False
SECURITY_CHANGEABLE = True
SECURITY_CHANGE_URL = '/manager/settings/changepassword'
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'insecure'

MAIL_SERVER = 'smtp.mailserver.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USERNAME = 'admin@example.com'
MAIL_PASSWORD = 'insecure'

CELERY_BROKER_URL = 'amqp://'
CELERY_IMPORTS = (["crestify.tasks.bookmark_tasks"])
CELERY_ACCEPT_CONTENT = ['pickle']

CRESTIFY_UPLOAD_DIRECTORY = '/tmp/crestify/uploads'

WEB_SERVER_IP = '127.0.0.1'

MIXPANEL_PROJECT_TOKEN = ''

HASHIDS_SALT = "&*6j3ji]/~B o38#y!a>X$$~x@8^n>v(*FJhjJ8*ok234"
