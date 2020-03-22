from flask import Flask
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from traceVtt.traces.utils import get_instance_folder_path
from traceVtt.config import configure_app


app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            instance_relative_config=True)
configure_app(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


from traceVtt import models 

from traceVtt.traces.views import main
app.register_blueprint(main, url_prefix='/main')
