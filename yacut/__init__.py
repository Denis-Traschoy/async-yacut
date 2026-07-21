from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import api_views, views

app.register_blueprint(api_views.api_bp)
app.register_blueprint(views.views_bp)

with app.app_context():
    db.create_all()