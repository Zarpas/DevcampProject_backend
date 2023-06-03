import time
from rq import get_current_job

from .. import db, app
from ..models import Task


# app.push()

def _set_task_progress(progress):
    with app.app_context():
        job = get_current_job()
        if job:
            job.meta['progress'] = progress
            job.save_meta()
            task = Task.query.get(job.get_id())

            if progress >= 100:
                task.complete = True
            db.session.commit()

def example(user, seconds):
    _set_task_progress(0)
    job = get_current_job()
    print("Starting task")
    for i in range(seconds):
        print(i)
        _set_task_progress(100*i//seconds)
        time.sleep(1)
    _set_task_progress(100)
    print("Task completed")


def import_list(user, filename):
    print(user)
    job = get_current_job()
    print("Starting task")
    for i in range(100):
        job.meta["progress"] = 100.0 * i / 100
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta["progress"] = 100
    job.save_meta()
    print("Task completed")


