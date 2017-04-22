If you want to install Crestify on your own, follow along!

#### Dependencies

##### Linux
(Do keep in mind that package names could differ based on your distro)

Python (& lib requirements): `python-virtualenv python-dev python-pip libxslt1-dev libxml2-dev`

RabbitMQ: `rabbitmq-server`

PostgreSQL: `postgresql-9.4 postgresql-server-dev-9.4 postgresql-contrib-9.4`

Redis: `redis-server`

PhantomJS: `phantomjs`

Supervisor: `supervisor`

##### Mac
With homebrew, these are the packages you need to install:

Python: `python libxml2`

RabbitMQ: `rabbitmq`

PostgreSQL: Use [Postgres.app](http://postgresapp.com/)

Redis: `redis`

PhantomJS: `phantomjs`

Supervisor: Install via pip

##### Windows
Please use the Vagrant image

#### Setup

1. Clone this repo and `cd` into it
2. Create a Python 2.7 virtualenv with `virtualenv-2.7 venv`
3. Activate the virtualenv with `source venv/bin/activate`
4. Install all the required Python dependencies with `pip install -r requirements.txt`
5. Rename `sample_override.py` to `override.py`
6. Rename the `sample.env` file to `.env` and change the value of `CRESTIFY_CONFIG_FILE` to the **absolute path** of your `override.py` file
7. Start RabbitMQ in another terminal window using `service rabbit-server start` or `rabbitmq-server`
8. To setup/upgrade the database do `honcho run python main.py db upgrade`
9. Finally start the application with `honcho start`. The application should be visible on [http://localhost:8000/](http://localhost:8000/)

For more info, please see `fabfile.py`.
