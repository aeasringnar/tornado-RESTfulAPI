from apscheduler.schedulers.tornado import TornadoScheduler
from .test_job import test_job


scheduler = TornadoScheduler()
scheduler.add_job(test_job, 'interval', seconds=3)