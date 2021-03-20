from __future__ import absolute_import, unicode_literals
from .celery import app
import time


@app.task
def add(x, y):
    time.sleep(2)
    return x + y


@app.task
def mul(x, y):
    time.sleep(5)
    return x * y


@app.task
def xsum(numbers):
    time.sleep(3)
    return sum(numbers)