from fabric.api import run, sudo, settings, execute, cd, prefix, local, env, get, put
from StringIO import StringIO
import re


def _get_vagrant_connection():
    local('vagrant up')
    result = local('vagrant ssh-config', capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")


def vagrant_init():
    _get_vagrant_connection()
    execute(install_python_reqs)
    execute(install_rabbitmq)
    execute(install_postgres)
    execute(install_redis)
    execute(install_phantomjs)
    execute(create_database)
    execute(config_environment)
    execute(setup_crestify_config)
    execute(run_migrations)
    execute(setup_nginx)
    execute(setup_supervisor)


def install_python_reqs():
    sudo('apt-get update --fix-missing')
    # We need the Python headers (python-dev) for compiling some libraries
    sudo('apt-get -y install python-virtualenv python-dev python-pip')
    # Readability dependencies for lxml
    sudo('apt-get -y install libxslt1-dev libxml2-dev libz-dev')


def install_rabbitmq():
    # RabbitMQ is our message queue
    sudo('echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list')
    sudo('apt-get -y install wget sudo')
    sudo('apt-get -y install ca-certificates')
    sudo('wget --quiet -O - https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -')
    sudo('apt-get update --fix-missing')
    sudo('apt-get -y install rabbitmq-server')


def install_postgres():
    sudo('echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list.d/pgdg.list')
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
  sudo apt-key add -')
    sudo('apt-get update')
    sudo('apt-get -y install postgresql-9.4 postgresql-server-dev-9.4 postgresql-contrib-9.4')


def install_redis():
    # Used for temporarily saving incoming tab saves
    sudo('apt-get -y install redis-server')


def install_phantomjs():
    # The PhantomJS headless browser
    sudo('apt-get -y install fontconfig')
    run('wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2')
    run('tar xjf phantomjs-2.1.1-linux-x86_64.tar.bz2')
    sudo('mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs')


def setup_nginx():
    sudo('apt-get -y install nginx')
    sudo('service nginx stop')
    sudo('mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak')
    put('nginx.conf', "/etc/nginx/nginx.conf", use_sudo=True)
    sudo('service nginx start')


def create_database():
    # Create the user and database for Crestify. User and db name can be changed given you change
    # SQLALCHEMY_DATABASE_URI in the config
    create_user_command = "CREATE ROLE crestify WITH PASSWORD 'crestify' LOGIN;"
    create_db_cmd = "CREATE DATABASE crestify OWNER postgres ENCODING 'UTF8' TEMPLATE template0 LC_CTYPE 'en_US.UTF8' LC_COLLATE 'en_US.UTF8'"
    with cd('/var/lib/postgresql'):
        with settings(sudo_user="postgres"):
            sudo('psql -c "{}"'.format(create_user_command))
            sudo('psql -c "{}"'.format(create_db_cmd))


def config_environment():
    sudo('apt-get -y install git screen')
    sudo('adduser crestify --disabled-password --gecos GECOS')
    sudo('locale-gen en_US.UTF-8')
    with settings(sudo_user='crestify', shell='/bin/bash -c'):
        with cd('/home/crestify'):
            sudo('git clone https://github.com/crestify/crestify.git crestify')
            sudo('virtualenv crestifyenv')
            with prefix('source crestifyenv/bin/activate'):
                sudo('pip install -r crestify/requirements.txt')


def run_migrations():
    with settings(sudo_user='crestify', shell='/bin/bash -c'):
        with cd('/home/crestify/crestify'):
            with prefix('source ../crestifyenv/bin/activate'):
                sudo('honcho run python main.py db upgrade')  # Run initial migrations


def setup_crestify_config():
    with settings(sudo_user="crestify", shell='/bin/bash -c'):
        with cd('/home/crestify'):
            with cd('crestify'):
                sudo('cp sample.env .env')
                sudo('echo \'CRESTIFY_CONFIG_FILE="/home/crestify/override.py"\' > .env')
                sudo('cp sample_override.py ../override.py')
            sudo('sed -i.bak \'s/# DEBUG = True/DEBUG = False/\' override.py')
            sudo(
                'sed -i.bak "s/SECRET_KEY = \'insecure\'/SECRET_KEY = \'gGT343S8PUUXgNIKl2vsEXsMZpNV4p0T8kpEh\'/" override.py')
            sudo(
                "sed -i.bak \"s/SECURITY_PASSWORD_SALT = 'insecure'/SECURITY_PASSWORD_SALT = 'EDoCC8D14S8X3uIWDu69t1LC8OkbUuDwqQwaJpnk'/\" override.py")
            sudo("sed -i.bak \"s/# C/C/g\" override.py")


def setup_supervisor():
    # We use supervisord to keep Crestify running in the background
    # Recover from crashes, and to start automatically on bootup
    # Also, using more than 1 gunicorn worker resulted in socket not being released, so only 1 worker will be used
    sudo('apt-get -y install supervisor')
    sudo('mkdir /var/log/crestify/')
    sudo(
        'cd /home/crestify/crestify && ../crestifyenv/bin/honcho export -s /bin/sh -a crestify supervisord /etc/supervisor/conf.d')
    fd = StringIO()
    get('/etc/supervisor/conf.d/crestify.conf', fd)
    content = fd.getvalue().splitlines()
    for n, i in enumerate(content):
        if i.startswith("environment="):
            content[n] = i + ",PATH=/home/crestify/crestifyenv/bin:%(ENV_PATH)s"
        if i.startswith("user="):
            content[n] = "user=crestify"
        if i.startswith("stopsignal="):
            content[n] = "stopsignal=TERM"  # Both Gunicorn and Celery use SIGTERM for graceful shutdown
    content = StringIO("\n".join(content))
    put(content, "/etc/supervisor/conf.d/crestify.conf", use_sudo=True)
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


def update():
    _get_vagrant_connection()
    execute(_git_update)
    execute(_restart_supervisor)


def _git_update():
    with settings(sudo_user="crestify", shell='/bin/bash -c'):
        with cd('/home/crestify/crestify'):
            with prefix('source ../crestifyenv/bin/activate'):
                with settings(sudo_user='crestify', shell='/bin/bash -c'):
                    sudo('git pull')
                    sudo('pip install -r requirements.txt')
                    sudo('honcho run python main.py db upgrade')


def _restart_supervisor():
    sudo('supervisorctl reread all')
    sudo('supervisorctl update all')
    sudo('supervisorctl restart all')
