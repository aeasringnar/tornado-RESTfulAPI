from __future__ import absolute_import, unicode_literals
from celery_app.celery import app
import time


@app.task
def user_handle():
    time.sleep(2)
    return True