from passlib.context import CryptContext
from datetime import datetime

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
