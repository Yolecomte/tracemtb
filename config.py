import os
from local import *

SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(password)s@%(host)s:%(port)s/%(database)s' % POSTGRES

SQLALCHEMY_TRACK_MODIFICATIONS = False 

UPLOAD_FOLDER = 'media/'

# Tracks types
TRACKS_TYPES = ['enduro', 'XC', 'DH']

# Allowed extensions to load traces (only gpx supported)
ALLOWED_EXTENSIONS = ['gpx',]

# Number of traces showed in on page in index.html
PER_PAGE = 5