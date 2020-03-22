import os

base_dir = os.path.dirname(os.path.realpath(__file__)) 


class BaseConfig(object):
    DEBUG = True
    TESTING = False
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(base_dir,'media/')    
    # Tracks types
    TRACKS_TYPES = ['enduro', 'XC', 'DH']
    # Allowed extensions to load traces (only gpx supported)
    ALLOWED_EXTENSIONS = ['gpx', ]
    # Number of traces showed in on page in index.html
    PER_PAGE = 5


def configure_app(app):
    app.config.from_object('traceVtt.config.BaseConfig')
    app.config.from_pyfile('local.cfg', silent=True)
