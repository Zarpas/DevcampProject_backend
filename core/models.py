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
    registered = db.Column(db.DateTime, default=datetime.utcnow)
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
    file = db.relationship(
        "File", foreign_keys="File.sender_id", backref="user", lazy="dynamic"
    )
    notifications = db.relationship(
        "Notification",
        foreign_keys="Notification.user_id",
        backref="user",
        lazy="dynamic",
    )
    task = db.relationship(
        "Task", foreign_keys="Task.user_id", backref="user", lazy="dynamic"
    )
    picture = db.relationship(
        "Picture", foreign_keys="Picture.sender_id", backref="user", lazy="dynamic"
    )
    note = db.relationship(
        "Note", foreign_keys="Note.sender_id", backref="user", lazy="dynamic"
    )

    def hash_password(self, password):
        self.password_hash = myctx.hash(password)

    def check_password(self, password):
        return myctx.verify(password, self.password_hash)

    def __repr__(self):
        return "<User {}>".format(self.id)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(
            "core.task_manager.tasks." + name, self.id, *args, **kwargs
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
            "_links": {"self": url_for("auth_manager.get_user", id=self.id)},
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
        if new_user:
            for field in ["id", "username", "surnames", "email"]:
                print("{} - {}".format(field, data[field]))
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

    def __repr__(self):
        return "<File {}>".format(self.id)

    def to_dict(self):
        data = {
            "id": self.id,
            "filename": self.filename,
            "sended": self.sended.isoformat() + "Z",
            "processed": self.processed,
            "_links": {
                "self": url_for("file_manager.get_file", id=self.id),
                "sender_id": url_for("auth_manager.get_user", id=self.sender_id),
                "delete": url_for("file_manager.delete_file", id=self.id),
            },
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
    __tablename__ = "task"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Task {}>".format(self.id)

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
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "complete": self.complete,
            "_links": {
                "self": url_for("task_manager.get_task", id=self.id),
                "user": url_for("auth_manager.get_user", id=self.user_id),
            },
        }
        return data


class Message(PaginatedAPIMixin, db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    readed = db.Column(db.Boolean)

    def __repr__(self):
        return "<Message {}>".format(self.body)

    def to_dict(self):
        data = {
            "id": self.id,
            "body": self.body,
            "timestamp": self.timestamp.isoformat() + "Z",
            "readed": self.readed,
            "_links": {
                "self": url_for("message.get_message", id=self.id),
                "sender": url_for("auth_manager.get_user", id=self.sender_id),
                "recipient": url_for("auth_manager.get_user", id=self.recipient_id),
            },
        }
        return data

    def from_dict(self, data):
        for field in ["sender_id", "recipient_id", "body"]:
            if field in data:
                setattr(self, field, data[field])


class Notification(PaginatedAPIMixin, db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)
    readed = db.Column(db.Boolean)

    def __repr__(self):
        return "<Notification {}>".format(self.id)

    def get_data(self):
        return json.loads(str(self.payload_json))

    def set_data(self, data):
        return json.dumps(data)

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp.isoformat() + "Z",
            "payload_json": self.payload_json,
            "readed": self.readed,
            "_links": {
                "self": url_for("notification_manager.get_notification", id=self.id),
                "user": url_for("auth_manager.get_user", id=self.user_id),
            },
        }
        return data


class CodeList(PaginatedAPIMixin, db.Model):
    __tablename__ = "codelist"
    id = db.Column(db.Integer, primary_key=True)
    list_code = db.Column(db.String(20), index=True, nullable=False)
    description = db.Column(db.String(70), nullable=False)
    edition = db.Column(db.String(6), nullable=False)
    revision = db.Column(db.Integer, nullable=True)
    project = db.Column(db.String(50), nullable=False)
    wirelist_owner = db.relationship(
        "WireList", foreign_keys="WireList.owner_id", backref="owner", lazy="dynamic"
    )

    def __repr__(self):
        return "<List {}>".format(self.id)

    def to_dict(self):
        data = {
            "id": self.id,
            "list_code": self.list_code,
            "description": self.description,
            "edition": self.edition,
            "revision": self.revision,
            "project": self.project,
            "_links": {"self": url_for("codelist.get_codelist", id=self.id)},
        }
        return data

    def from_dict(self, data):
        for field in ["list_code", "description", "edition", "revision", "project"]:
            if field in data:
                setattr(self, field, data[field])


class WireList(PaginatedAPIMixin, db.Model):
    __tablename__ = "wirelist"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("codelist.id"))
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
    note = db.relationship(
        "Note", foreign_keys="Note.reference_id", backref="wire", lazy="dynamic"
    )

    def __repr__(self):
        return "<WireList {}>".format(self.id)

    def to_dict(self):
        data = {
            "id": self.id,
            "order": self.order,
            "edicion": self.edicion,
            "zona1": self.zona1,
            "zona2": self.zona2,
            "zona3": self.zona3,
            "zona4": self.zona4,
            "zona5": self.zona5,
            "zona6": self.zona6,
            "zona7": self.zona7,
            "zona8": self.zona8,
            "zona9": self.zona9,
            "zona10": self.zona10,
            "zona11": self.zona11,
            "zona12": self.zona12,
            "cable_num": self.cable_num,
            "codig_pant": self.codig_pant,
            "senal_pant": self.senal_pant,
            "sub_pant": self.sub_pant,
            "clase": self.clase,
            "lugarpro": self.lugarpro,
            "aparatopro": self.aparatopro,
            "bornapro": self.bornapro,
            "esquemapro": self.esquemapro,
            "lugardes": self.lugardes,
            "aparatodes": self.aparatodes,
            "bornades": self.bornades,
            "esquemades": self.esquemades,
            "seccion": self.seccion,
            "longitud": self.longitud,
            "codigocabl": self.codigocabl,
            "terminalor": self.terminalor,
            "terminalde": self.terminalde,
            "observacion": self.observacion,
            "num_mazo": self.num_mazo,
            "codigo": self.codigo,
            "potencial": self.potencial,
            "peso": self.peso,
            "codrefcabl": self.codrefcabl,
            "codreftori": self.codreftori,
            "codreftdes": self.codreftdes,
            "num_solucion": self.num_solucion,
            "seguridad": self.seguridad,
            "etiqueta": self.etiqueta,
            "etiqueta_pant": self.etiqueta_pant,
            "_links": {"self": url_for("wirelist_manager.get_wire", id=self.id)},
        }
        return data

    def from_dict(self, data):
        for field in [
            "order",
            "edicion",
            "zona1",
            "zona2",
            "zona3",
            "zona4",
            "zona5",
            "zona6",
            "zona7",
            "zona8",
            "zona9",
            "zona10",
            "zona11",
            "zona12",
            "cable_num",
            "codig_pant",
            "senal_pant",
            "sub_pant",
            "clase",
            "lugarpro",
            "aparatopro",
            "bornapro",
            "esquemapro",
            "lugardes",
            "aparatodes",
            "bornades",
            "esquemades",
            "seccion",
            "longitud",
            "codigocabl",
            "terminalor",
            "terminalde",
            "observacion",
            "num_mazo",
            "codigo",
            "potencial",
            "peso",
            "codrefcabl",
            "codreftori",
            "codreftdes",
            "num_solucion",
            "seguridad",
            "etiqueta",
            "etiqueta_pant",
        ]:
            if field in data:
                setattr(self, field, data[field])


class Picture(PaginatedAPIMixin, db.Model):
    __tablename__ = "picture"
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String(255), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sended = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(140), nullable=False)

    def __repr__(self):
        return "<Picture {}>".format(self.id)

    def to_dict(self):
        data = {
            "id": self.id,
            "picture": self.picture,
            "description": self.description,
            "sended": self.sended,
            "_links": {
                "self": url_for("picture_manager.get_picture", id=self.id),
                "sender_id": url_for("auth_manager.get_user", id=self.sender_id),
            },
        }
        return data

    def from_dict(self, data):
        for field in ["picture", "sender_id", "description"]:
            if field in data:
                setattr(self, field, data[field])


class Note(PaginatedAPIMixin, db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(40), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    reference_id = db.Column(db.Integer, db.ForeignKey("wirelist.id"))
    private = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<Note {}>".format(self.id)

    def to_dict(self):
        pass

    def from_dict(self, data):
        pass
