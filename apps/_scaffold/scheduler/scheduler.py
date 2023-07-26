import sys, traceback
import json
from . import settings
from ..common import db, logger
from .common import auth
from .tools import now

from . import actions

PARALLEL_TASK = 1 # 1 means no parallel task

do_action = lambda func, kwargs: getattr(actions, func)(**kwargs)

def run_next():

    logger.debug('Checking tasks in queue')

    # next_to_run = db.scheduler_task(status=settings.QUEUED)
    
    queued_and_running_tasks = db(db.scheduler_task.status.belongs([settings.QUEUED, settings.ASSIGNED, settings.RUNNING])).select(
        orderby = ~db.scheduler_task.start_time
    )
    
    running_tasks = queued_and_running_tasks.find(lambda row: (row.status in [settings.ASSIGNED, settings.RUNNING]))
    
    if len(running_tasks) < PARALLEL_TASK:
        next_to_run = queued_and_running_tasks.find(lambda row: (row.status==settings.QUEUED)).first()
    else:
        next_to_run = None
        
    if not next_to_run is None:

        logger.debug(f"Trovato il task: {next_to_run}")

        run_id = db.scheduler_run.insert(
            task_id = next_to_run.id,
            status = settings.ASSIGNED
        )

        run = db.scheduler_run[run_id]
        run.update_record(status = settings.RUNNING)
        db.commit()
        
        task_vars = next_to_run.get('vars') or {}
        
        recipient = auth.db.auth_user(id=next_to_run['auth_user_id'])
        
        try:
            # TODO: Gestire lo standard output in modo da loggare periodicamente in run_output
            # quello che viene stampato su stdout dal task
            # TODO: Introdurre la gestione del timeout, se impostato allo scadere
            # il processo deve essere ucciso.
            run_result = do_action(
                next_to_run['function_name'],
                dict(task_vars)
            )
        except Exception as err:
            # rollback on failure as first step
            db.rollback()
            logger.error(err)

            # Log failure informations
            type_, value_, traceback_ = sys.exc_info()
            ex = traceback.format_exception(type_, value_, traceback_)
            tb_text = ''.join(ex)
            logger.debug(tb_text)
            
            run.update_record(
                status = settings.FAILED,
                stop_time = now(),
                traceback = tb_text
            )
            
            if not recipient is None:
                try:
                    # Notify FAIL
                    auth.send('task_failed', recipient,
                        task_name = next_to_run.get('task_name'),
                        task_id = next_to_run.get('id'),
                        trace_back = tb_text
                    )
                except Exception as mailerr:
                    logger.error(mailerr)
        else:
            # Log success informations
            stop_time = now()
            run.update_record(
                status = settings.COMPLETED,
                stop_time = stop_time,
                run_result = run_result
            )
            if not recipient is None:
                # Notify FAIL
                try:
                    # Notify SUCCESS
                    auth.send('task_success', recipient,
                        task_name = next_to_run.get('task_name'),
                        task_id = next_to_run.get('id'),
                        start_time = run.get('start_time'),
                        end_time = stop_time
                    )
                except Exception as mailerr:
                    logger.error(mailerr)