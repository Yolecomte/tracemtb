from flask import current_app as app

from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import datetime
from traceVtt import db

class BaseModel(db.Model):
    """
    """
    __abstract__ = True

    def repr(self):
        return self.__class__.__name__

class Traces(BaseModel):
    __tablename__ = 'traces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.String(200), nullable=True)
    type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    geom = db.Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=True)

    def __init__(self, name, comment, type, geom=None):
        self.name = name
        self.comment = comment
        self.geom = geom
        self.type = type
    

class Users(BaseModel):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(200), nullable=False)
    mail = db.Column(db.String)
    password = db.Column(db.String, nullable=False)

    def __init__(self, pseudo, mail, password):
        self.pseudo = pseudo
        self.mail = mail
        self.password = password

    def is_active(self):
        return True

    def get_id(self):
        return self.mail

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False