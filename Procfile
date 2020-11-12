wsgi: gunicorn -w 4 --log-file=- main:app -t 1000 --log-level=info -b 0.0.0.0:8000
celery: celery -A crestify.tasks.celery worker -n worker1 --loglevel=info
celery2: celery -A crestify.tasks.celery worker -n worker2 --loglevel=info
