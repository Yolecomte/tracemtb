from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from traceVtt import db


class BaseModel(db.Model):
    """
    Abstract class for common methods
    """
    __abstract__ = True

    def repr(self):
        return self.__class__.__name__


class Traces(BaseModel):
    """
    To Store the tracks load or draw by users
    """
    __tablename__ = 'traces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    comment = db.Column(db.String(200), nullable=True)
    type_trace = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    geom = db.Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=True)

    def __init__(self, name, comment, type_trace, geom=None):
        self.name = name
        self.comment = comment
        self.geom = geom
        self.type = type_trace
