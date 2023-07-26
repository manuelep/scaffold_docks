import uuid
from pydal.validators import (
    IS_DATETIME,
    IS_INT_IN_RANGE,
    IS_IN_SET,
)
from py4web import Field
from . import settings
from ..common import db, logger
from .tools import now


db.define_table('scheduler_task',
    # Field('application_name', requires=IS_NOT_EMPTY(),
    #       default=None, writable=False),
    Field('task_name', default=None),
    # Field('group_name', default='main'),
    Field('status', requires=IS_IN_SET(settings.TASK_STATUS),
          default=settings.QUEUED, writable=False),
    # Field('broadcast', 'boolean', default=False),
    Field('function_name', required=True, notnull=True),
    Field('uuid', length=255,
        #   requires=IS_NOT_IN_DB(db, 'scheduler_task.uuid'),
          unique=True, default=lambda : str(uuid.uuid4())),
    # Field('args', 'json', readable=False),
    Field('vars', 'json', readable=False),
    Field('enabled', 'boolean', default=True),
    Field('start_time', 'datetime', default=now, requires=IS_DATETIME()),
    # Field('next_run_time', 'datetime', default=now),
    Field('stop_time', 'datetime'),
    # Field('repeats', 'integer', default=1, comment="0=unlimited",
    #       requires=IS_INT_IN_RANGE(0, None)),
    Field('retry_failed', 'integer', default=0, comment="-1=unlimited",
          requires=IS_INT_IN_RANGE(-1, None)),
    # Field('period', 'integer', default=60, comment='seconds',
    #       requires=IS_INT_IN_RANGE(0, None)),
    # Field('prevent_drift', 'boolean', default=False,
    #       comment='Exact start_times between runs'),
    # Field('cronline', default=None,
    #       comment='Discard "period", use this cron expr instead',
    #       requires=IS_EMPTY_OR(IS_CRONLINE())),
    Field('timeout', 'integer', default=60, comment='seconds',
          requires=IS_INT_IN_RANGE(1, None)),
    # Field('sync_output', 'integer', default=0,
    #       comment="update output every n sec: 0=never",
    #       requires=IS_INT_IN_RANGE(0, None)),
    Field('times_run', 'integer', default=0, writable=False),
    Field('times_failed', 'integer', default=0, writable=False),
    # Field('last_run_time', 'datetime', writable=False, readable=False),
    # Field('assigned_worker_name', default='', writable=False),
    Field('is_active', 'boolean',
        writable=False, readable=False, default=True),
    Field('auth_user_id', 'integer'),
    common_filter = lambda query: (db.scheduler_task.enabled==True) & (db.scheduler_task.is_active==True),
    migrate=settings.DB_MIGRATE,
    format='(%(id)s) %(task_name)s'
)

db.define_table('scheduler_run',
    Field('task_id', 'reference scheduler_task'),
    Field('status', requires=IS_IN_SET(settings.RUN_STATUS)),
    Field('start_time', 'datetime', default=now),
    Field('stop_time', 'datetime'),
    Field('run_output', 'text'),
    Field('run_result', 'json'),
    Field('traceback', 'text'),
    # Field('worker_name', default=self.worker_name),
    migrate=settings.DB_MIGRATE
)


def after_insert_run(rec, run_id):
    """ """
    task = db.scheduler_task[rec['task_id']]
    task.update_record(start_time=rec['start_time'])

def after_update_run(dbset, rec):
    """ """

    assert dbset.count()==1
    run = dbset.select(db.scheduler_run.task_id, limitby=(0,1,)).first()

    task = db.scheduler_task[run.task_id]

    updates ={'status': rec['status']}
    if rec['status'] in (settings.COMPLETED, settings.FAILED, settings.TIMEOUT, settings.STOPPED,):
        updates['stop_time'] = rec['stop_time']
        updates['times_run'] = task['times_run']+1
    # WARNING! Is TIMEOUT a real fail??
    if rec['status'] in (settings.FAILED, settings.TIMEOUT,):
        updates['times_failed'] = task['times_failed']+1

        if task['retry_failed']<0 or updates['times_failed']<task['retry_failed']:
            updates['status'] = settings.QUEUED

    task.update_record(**updates)


db.scheduler_task._enable_record_versioning()
db.scheduler_run._after_insert.append(after_insert_run)
db.scheduler_run._after_update.append(after_update_run)