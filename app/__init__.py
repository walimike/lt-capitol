import flask
from app.config import app_config

app = flask.Flask(__name__)
app.secret_key = 'super secret key'

from app import index, gate_io, ftexchange
