from flask import Flask
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

from totemlogs.views.log import *  # noqa
from totemlogs.views import *  # noqa
