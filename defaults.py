DEBUG = False

SECRET_KEY = "insecure"

SQLALCHEMY_DATABASE_URI = "postgresql://crestify@localhost/crestify_db"

SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_EMAIL_SENDER = "noreply@crestify.com"
SECURITY_CONFIRMABLE = True
SECURITY_CHANGEABLE = True
SECURITY_CHANGE_URL = "/manager/settings/changepassword"
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = "insecure"

MAIL_SERVER = "smtp.mailserver.com"
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USERNAME = "admin@example.com"
MAIL_PASSWORD = "insecure"

CELERY_BROKER_URL = "redis://"
CELERY_IMPORTS = ["crestify.tasks.bookmark_tasks", "crestify.tasks.tracker"]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = {"pickle"}

CRESTIFY_UPLOAD_DIRECTORY = "/tmp/crestify/uploads"

WEB_SERVER_IP = "127.0.0.1"

MIXPANEL_PROJECT_TOKEN = ""

HASHIDS_SALT = "6:Vh3-N4]/~B o38#y!a>X$$~x@'>v(*FJhj43khk234"

SQLALCHEMY_TRACK_MODIFICATIONS = (
    True  # TODO: Remove and switch to SQLAlchemy native event system
)

# Elasticsearch
ELASTICSEARCH_URL = "http://localhost:9200"
