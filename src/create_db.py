from web_server import db, app
import os

with app.app_context():
    db.create_all()
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance/models"))
