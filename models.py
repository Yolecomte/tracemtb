from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()

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
    geom = db.Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=True)

    def __init__(self, name, comment):
        self.name = name
        self.comment = comment
        