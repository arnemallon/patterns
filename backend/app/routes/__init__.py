from flask import Blueprint

api = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from . import classification 