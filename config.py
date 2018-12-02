import os

POSTGRES = {
    'user': 'postgres',
    'password': 'postgres',
    'database': 'traceVtt',
    'host': 'localhost',
    'port': '5432',
}
SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(password)s@%(host)s:%(port)s/%(database)s' % POSTGRES

SQLALCHEMY_TRACK_MODIFICATIONS = False 

UPLOAD_FOLDER = 'media/'

TRACKS_TYPES = ['enduro', 'XC', 'DH']

ALLOWED_EXTENSIONS = ['gpx',]

SECRET_KEY = 'soighiognfg'
