# -*- coding: utf-8 -*-

from celery import Celery
from crestify import app


def make_celery(appObj):
    celery = Celery(appObj.import_name, broker=appObj.config["CELERY_BROKER_URL"])
    celery.conf.update(appObj.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
