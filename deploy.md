# Deployment

## Python

* `python-pip`
* `python-virtualenv`
* `python-dev` or `python-devel`

## Readability-lxml

* `libxslt1-dev`
* `libxml2-dev`

## RabbitMQ

* `deb http://www.rabbitmq.com/debian/ testing main` to `/etc/apt/sources.list`
* Download `https://www.rabbitmq.com/rabbitmq-signing-key-public.asc` and `apt-key add`
* `rabbitmq-server`

## PostgreSQL

* `deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main` to `/etc/apt/sources.list`
* `wget` `ca-certificates`
* Download `https://www.postgresql.org/media/keys/ACCC4CF8.asc` and `apt-key add`
* `postgresql-9.4`
* `postgresql-server-dev-9.4`
* `postgresql-contrib-9.4`


## PhantomJS

The PhantomJS in the Ubuntu repositories has some issues, so it is required to compile it. 

### Install the following packages:
* `build-essential g++ flex bison gperf ruby perl \
  libsqlite3-dev libfontconfig1-dev libicu-dev libfreetype6 libssl-dev \
  libpng-dev libjpeg-dev python libx11-dev libxext-dev`

Follow instructions [here](http://phantomjs.org/build.html).


## Redis

Have to build Redis

* [Instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-redis)
* `tcl8.5`
* `wget http://download.redis.io/releases/redis-stable.tar.gz`
* `tar xzf redis-stable.tar.gz`
* `cd redis-stable`
* `make`
* `make test`
* `make install`
* `cd utils`
* `sudo ./install_server.sh`

## Nginx

* `apt-get -y install nginx`
* `/etc/nginx/nginx.conf` from `https://gist.githubusercontent.com/dhamaniasad/f3fa4edb705c62623814/raw/c4dcaa202eb660b0cfb3da819af18770a8b6970d/gistfile1.txt`
* `https://gist.github.com/dhamaniasad/f3fa4edb705c62623814`

### Commands
* `apt-get update`
* `apt-get -y upgrade`
* `apt-get -y install python-dev`
* `apt-get -y install python-pip`
* `apt-get -y install python-virtualenv`
* `apt-get -y install libxslt1-dev`
* `apt-get -y install libxml2-dev`
* `echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list`
* `apt-get -y install wget`
* `apt-get -y install sudo`
* `apt-get -y install ca-certificates`
* `wget --quiet -O - https://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -`
* `apt-get update`
* `apt-get -y install rabbitmq-server`
* `echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" >> /etc/apt/sources.list`
* `wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -`
* `apt-get update`
* `apt-get -y install postgresql-9.4`
* `apt-get -y install postgresql-server-dev-9.4`
* `apt-get -y install postgresql-contrib-9.4`
* `apt-get -y install nginx`
* `Add config`
* `service nginx restart`
* `su - postgres`
* `psql`
* `CREATE ROLE crestify;`
* `ALTER ROLE crestify WITH PASSWORD 'password';`
* `ALTER ROLE crestify LOGIN;`
* `CREATE DATABASE crestify_db OWNER postgres ENCODING 'UTF8' TEMPLATE template0 LC_CTYPE 'en_US.UTF8' LC_COLLATE 'en_US.UTF8';`
* `apt-get -y install git`
* `git clone repo`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r crestify/requirements.txt`
* `adduser crestify`
* `apt-get -y install screen`
* `sudo locale-gen en_US.UTF-8`
* `sudo dpkg-reconfigure locales`
* `echo "LC_ALL="en_US.UTF-8"" >> /etc/environment`
* `reboot`

# SCRATCH ALL OF THAT

fab -H asad@server deploy_restore
