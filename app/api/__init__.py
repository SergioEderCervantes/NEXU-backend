from .health import routes_health
from .users import users_bp
from .chats import chats_bp
from flask import Flask

def register_blueprints(app: Flask):
    app.register_blueprint(routes_health, url_prefix='/health')
    app.register_blueprint(users_bp)
    app.register_blueprint(chats_bp)