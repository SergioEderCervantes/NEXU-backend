from .health import routes_health
from flask import Flask

def register_blueprints(app: Flask):
    app.register_blueprint(routes_health, url_prefix='/health')