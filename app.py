from flask import Flask
from flask_cors import CORS
from models import *
from config import Config

def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app) 

    cors = CORS(app)
    
    from auth.routes import auth as auth_blueprint
    from connect.routes import connect as connect_blueprint
    from api.routes import api as api_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(connect_blueprint)
    app.register_blueprint(api_blueprint)

    return app
    



  
