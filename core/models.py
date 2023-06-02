from passlib.context import CryptContext
from datetime import datetime
import redis
import rq
from flask import current_app

from core import db, ma

myctx = CryptContext(["sha256_crypt"])


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surnames = db.Column(db.String(40))
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80))
    registered = db.Column(db.DateTime, default=datetime.now())
    can_admin = db.Column(db.Boolean(), default=False)
    can_fileupload = db.Column(db.Boolean(), default=False)
    can_listoperate = db.Column(db.Boolean(), default=False)
    can_writenote = db.Column(db.Boolean(), default=True)
    can_takepicture = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=True)
    files = db.relationship('File', backref='user', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')


    def hash_password(self, password):
        return myctx.hash(password)

    def check_password(self, password):
        return myctx.verify(password, self.password_hash)
    
    def __init__(self, id, name, surnames, email, password):
        self.id = id
        self.name = name
        self.surnames = surnames
        self.email = email
        self.password_hash = self.hash_password(password)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('core.tasks.tasks.' + name, self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)
        return task
    
    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()
    
    def get_tasks_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self, complete=False).first()


class UserSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "surnames",
            "email",
            "password_hash",
            "registered",
            "active",
            "can_admin",
            "can_fileupload",
            "can_listoperate",
            "can_writenote",
            "can_takepicture",
        )


user_schema = UserSchema()
users_schema = UserSchema(many=True)

class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    sended = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

    def __init__(self, filename, sender):
        self.filename = filename
        self.sender = sender

class FileSchema(ma.Schema):
    class Meta:
        fields = ('id', 'filename', 'sender', 'sended', 'processed',)

file_schema = FileSchema()
files_schema = FileSchema(many=True)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.Fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'complete',)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
