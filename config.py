import os
import local.py

SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(password)s@%(host)s:%(port)s/%(database)s' % POSTGRES

SQLALCHEMY_TRACK_MODIFICATIONS = False 

UPLOAD_FOLDER = 'media/'

TRACKS_TYPES = ['enduro', 'XC', 'DH']

ALLOWED_EXTENSIONS = ['gpx',]
