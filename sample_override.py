"""
Copy and rename this file, then
override these config vars as per your needs

You can create multiple version of this file and
switch between them in the .env file

"""

DEBUG = True

SECRET_KEY = "insecure"

SQLALCHEMY_DATABASE_URI = "postgresql://crestify@localhost/crestify_db"

SECURITY_PASSWORD_SALT = "insecure"

MAIL_SERVER = "smtp.mandrillapp.com"
MAIL_USERNAME = "admin@example.com"
MAIL_PASSWORD = "insecure"

RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""

# CELERY_ACCEPT_CONTENT = ['pickle']
# CELERY_BROKER_URL = 'amqp://'

# DEBUG_TB_PROFILER_ENABLED = True
# DEBUG_TB_INTERCEPT_REDIRECTS = False

# SENTRY_DSN = ''

REDIS_URI = "redis://localhost"
