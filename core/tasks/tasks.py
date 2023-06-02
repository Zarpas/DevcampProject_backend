import time
from rq import get_current_job

from .. import app


app.push()

def example(seconds):
    job = get_current_job()
    print("Starting task")
    for i in range(seconds):
        job.meta["progress"] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta["progress"] = 100
    job.save_meta()
    print("Task completed")


def import_list(filename, importer):
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


