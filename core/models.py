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
    file = db.relationship("File", backref="users", lazy="dynamic")
    task = db.relationship("Task", backref="users", lazy="dynamic")

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

    def __repr__(self):
        return "{} - {}, {}".format(self.id, self.surnames, self.name)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(
            "core.tasks.tasks." + name, self.id, *args, **kwargs
        )
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
    sender = db.Column(db.Integer, db.ForeignKey("users.id"))
    sended = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

    def __init__(self, filename, sender):
        self.filename = filename
        self.sender = sender

    def __repr__(self):
        return "{} - {}".format(self.filename, self.sender)


class FileSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "filename",
            "sender",
            "sended",
            "processed",
        )


file_schema = FileSchema()
files_schema = FileSchema(many=True)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.Fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100


class TaskSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "description",
            "complete",
        )


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


class List(db.Model):
    __tablename__ = "lists"
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
        return "{} - {}".format(self.list_code, self.description)


class ListSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "list_code",
            "description",
            "edition",
            "revision",
            "project",
        )


list_schema = ListSchema()
lists_schema = ListSchema(many=True)


class WireList(db.Model):
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


class WireListSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'order',
            'edicion',
            'zona1',
            'zona2',
            'zona3',
            'zona4',
            'zona5',
            'zona6',
            'zona7',
            'zona8',
            'zona9',
            'zona10',
            'zona11',
            'zona12',
            'cable_num',
            'codig_pant',
            'senal_pant',
            'sub_pant',
            'clase',
            'lugarpro',
            'aparatopro',
            'bornapro',
            'esquemapro',
            'lugardes',
            'aparatodes',
            'bornades',
            'esquemades',
            'seccion',
            'longitud',
            'codigocabl',
            'terminalor',
            'terminalde',
            'observacion',
            'num_mazo',
            'codigo',
            'potencial',
            'peso',
            'codrefcabl',
            'codreftori',
            'codreftdes',
            'num_solucion',
            'seguridad',
            'etiqueta',
            'etiqueta_pant',
        )


wirelist_schema = WireListSchema()
wirelists_schema = WireListSchema(many=True)
