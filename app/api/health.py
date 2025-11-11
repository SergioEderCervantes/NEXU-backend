from flask import Blueprint

routes_health = Blueprint("health", __name__)


@routes_health.route('/')
def health_check():
    return "Api Funcionando en Flask!!"