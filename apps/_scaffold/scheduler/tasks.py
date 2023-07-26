"""
To use celery tasks:
1) pip install -U "celery[redis]"
2) In settings.py:
   USE_CELERY = True
   CELERY_BROKER = "redis://localhost:6379/0"
3) Start "redis-server"
4) Start "celery -A apps.{appname}.tasks beat"
5) Start "celery -A apps.{appname}.tasks worker --loglevel=info" for each worker

"""
from . import settings as scheduler_settings
from ..common import settings, scheduler, db
from .scheduler import run_next

# example of task that needs db access
@scheduler.task(
    retry_backoff=5,
    max_retries=10,
    retry_jitter=False,
)
def my_task():
    try:
        # this task will be executed in its own thread, connect to db
        db._adapter.reconnect()
        # do something here
        run_next()
        db.commit()
    except:
        # rollback on failure
        db.rollback()


# run my_task periodically
scheduler.conf.beat_schedule = {
    "my_first_task": {
        "task": "apps.%s.tasks.my_task" % settings.APP_NAME,
        "schedule": scheduler_settings.HEARTBEAT,
        "args": (),
    },
}
