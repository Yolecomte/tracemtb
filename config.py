POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres',
    'db': 'traceVtt',
    'host': 'localhost',
    'port': '5432',
}
SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
