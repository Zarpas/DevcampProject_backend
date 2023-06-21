from core import create_app, db
from core.models import User, File, Task, Message, Notification, List, WireList

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "File": File,
        "Task": Task,
        "Message": Message,
        "Notification": Notification,
        "List": List,
        "WireList": WireList,
    }
