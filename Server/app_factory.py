# app_factory.py
from flask import Flask
from camera.timelapse import load_saved_config
from database.models import db
from routes.home import home_bp
from routes.camera_routes import camera_bp
from routes.i2c_routes import i2c_bp
from routes.smartplug_routes import smartplug_bp
from routes.auth_routes import auth_bp
from database.models import db
from auth.oauth2_server import config_oauth
from sensors.bluetooth.bluetooth import init_ble

import os

def create_app():
    app = Flask(__name__)

    # Database config
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Register routes
    app.register_blueprint(home_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(i2c_bp)
    app.register_blueprint(smartplug_bp)
    app.register_blueprint(auth_bp)

    # Secret key for session management
    app.secret_key = 'REPLACE_WITH_RANDOM_SECRET_KEY'  # use os.urandom(24) in production

    # Initialize database
    with app.app_context():
        db.create_all()
        load_saved_config()
        config_oauth(app)
        #init_ble(app)

    return app
