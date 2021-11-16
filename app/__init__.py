import flask
from app.config import app_config

app = flask.Flask(__name__)

from app import index, gate_io, ftexchange
