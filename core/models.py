from passlib.context import CryptContext
from datetime import datetime
import redis
import rq
from flask import current_app, url_for
import json
from time import time

from core import db

myctx = CryptContext(["sha256_crypt"])


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page=page, per_page=per_page, error_out=False)
        data = {
            "items": [item.to_dict() for item in resources.items],
            "_meta": {
                "page": page,
                "per_page": per_page,
                "total_items": resources.total,
            },
            "_links": {
                "self": url_for(endpoint, page=page, per_page=per_page, **kwargs),
                "next": url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next
                else None,
                "prev": url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev
                else None,
            },
        }
        return data


class User(PaginatedAPIMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    surnames = db.Column(db.String(40))
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80))
    registered = db.Column(db.DateTime, default=datetime.now())
    admin = db.Column(db.Boolean(), default=False)
    fileupload = db.Column(db.Boolean(), default=False)
    listoperate = db.Column(db.Boolean(), default=False)
    writenote = db.Column(db.Boolean(), default=True)
    takepicture = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean(), default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    messages_sent = db.relationship(
        "Message", foreign_keys="Message.sender_id", backref="author", lazy="dynamic"
    )
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        backref="recipient",
        lazy="dynamic",
    )
    last_message_read_time = db.Column(db.DateTime)
    file = db.relationship("File", backref="user", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")
    task = db.relationship("Task", backref="user", lazy="dynamic")

    def hash_password(self, password):
        self.password_hash = myctx.hash(password)

    def check_password(self, password):
        return myctx.verify(password, self.password_hash)

    # def __init__(self, id, username, surnames, email, password):
    #     self.id = id
    #     self.username = username
    #     self.surnames = surnames
    #     self.email = email
    #     self.password_hash = self.hash_password(password)

    def __repr__(self):
        return "<User {}>".format(self.id)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(
            "core.tasks.tasks." + name, self.id, *args, **kwargs
        )
        task = Task(
            id=rq_job.get_id(), name=name, description=description, user_id=self.id
        )
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user_id=self.id, complete=False).first()

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return (
            Message.query.filter_by(recipient=self)
            .filter(Message.timestamp > last_read_time)
            .count()
        )

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def to_dict(
        self,
        include_email=False,
        include_roles=False,
    ):
        data = {
            "id": self.id,
            "username": self.username,
            "surnames": self.surnames,
            "last_seen": self.last_seen.isoformat() + "Z",
            "_links": {"self": url_for("auth.get_user", id=self.id)},
        }
        if include_email:
            data["email"] = self.email
        if include_roles:
            for field in [
                "active",
                "admin",
                "fileupload",
                "listoperate",
                "writenote",
                "takepicture",
            ]:
                data[field] = getattr(self, field)
        return data

    def from_dict(self, data, new_user=False, change_admin=False):
        if new_user is False:
            for field in ["id", "username", "surnames", "email"]:
                if field in data:
                    setattr(self, field, data[field])
        if new_user and "password" in data:
            self.hash_password(data["password"])
        if change_admin:
            for field in [
                "active",
                "admin",
                "fileupload",
                "listoperate",
                "writenote",
                "takepicture",
            ]:
                if field in data:
                    print("{} {}".format(field, data[field]))
                    setattr(self, field, bool(data[field]))


class File(PaginatedAPIMixin, db.Model):
    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sended = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

    def __init__(self, filename, sender):
        self.filename = filename
        self.sender = sender

    def __repr__(self):
        return "<File {}".format(self.id)
    
    def to_dict(self):
        data = {
            "id": self.id,
            "filename": self.filename,
            "sended": self.sended.isoformat() + "Z",
            "processed": self.processed,
            "_links": {"self": url_for("file_manager.get_file", id=self.id),
                       "sender_id": url_for("aut.get_user", id=self.id)},
        }
        
        return data
    
    def from_dict(self, data, new_file=False, change_processed=False):
        if new_file:
            if "filename" in data:
                self.filename = data["filename"]
        if change_processed:
            if "processed" in data:
                self.processed = bool(data["processed"])


class Task(PaginatedAPIMixin, db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Task {}".format(self.id)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.Fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100
    
    def to_dict(self):
        # todo
        pass


class Message(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    readed = db.Column(db.Boolean)

    def __repr__(self):
        return "<Message {}>".format(self.body)
    
    def to_dict(self):
        # todo
        pass


class Notification(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)
    readed = db.Column(db.Boolean)

    def __repr__(self):
        return "<Notification []>".format(self.id)

    def get_data(self):
        return json.loads(str(self.payload_json))

    def set_data(self, data):
        return json.dumps(data)
    
    def to_dict(self):
        # todo
        pass


class List(PaginatedAPIMixin, db.Model):
    __tablename__ = "list"
    id = db.Column(db.Integer, primary_key=True)
    list_code = db.Column(db.String(20), index=True, nullable=False)
    description = db.Column(db.String(70), nullable=False)
    edition = db.Column(db.String(6), nullable=False)
    revision = db.Column(db.Integer, nullable=True)
    project = db.Column(db.String(50), nullable=False)

    def __init__(self, list_code, description, project, edition, revision):
        self.list_code = list_code
        self.description = description
        self.project = project
        self.edition = edition
        self.revision = revision

    def __repr__(self):
        return "<List {}>".format(self.id)
    
    def to_dict(self):
        # todo
        pass


class WireList(PaginatedAPIMixin, db.Model):
    __tablename__ = "wire_list"
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.String(6))
    edicion = db.Column(db.String(2))
    zona1 = db.Column(db.String(3))
    zona2 = db.Column(db.String(3))
    zona3 = db.Column(db.String(3))
    zona4 = db.Column(db.String(3))
    zona5 = db.Column(db.String(3))
    zona6 = db.Column(db.String(3))
    zona7 = db.Column(db.String(3))
    zona8 = db.Column(db.String(3))
    zona9 = db.Column(db.String(3))
    zona10 = db.Column(db.String(3))
    zona11 = db.Column(db.String(3))
    zona12 = db.Column(db.String(3))
    cable_num = db.Column(db.String(12))
    codig_pant = db.Column(db.String(10))
    senal_pant = db.Column(db.String(6))
    sub_pant = db.Column(db.String(5))
    clase = db.Column(db.String(4))
    lugarpro = db.Column(db.String(6))
    aparatopro = db.Column(db.String(18))
    bornapro = db.Column(db.String(7))
    esquemapro = db.Column(db.String(6))
    lugardes = db.Column(db.String(6))
    aparatodes = db.Column(db.String(18))
    bornades = db.Column(db.String(7))
    esquemades = db.Column(db.String(6))
    seccion = db.Column(db.String(5))
    longitud = db.Column(db.String(6))
    codigocabl = db.Column(db.String(15))
    terminalor = db.Column(db.String(15))
    terminalde = db.Column(db.String(15))
    observacion = db.Column(db.String(30))
    num_mazo = db.Column(db.String(5))
    codigo = db.Column(db.String(15))
    potencial = db.Column(db.String(10))
    peso = db.Column(db.String(7))
    codrefcabl = db.Column(db.String(15))
    codreftori = db.Column(db.String(15))
    codreftdes = db.Column(db.String(15))
    num_solucion = db.Column(db.String(16))
    seguridad = db.Column(db.String(3))
    etiqueta = db.Column(db.String(10))
    etiqueta_pant = db.Column(db.String(10))

    def __repr__(self):
        return "<WireList {}>".format(self.id)
    
    def to_dict(self):
        # todo
        pass
