from flask import Flask
from flask.ext.socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


from totemlogs.views.log import *  # noqa
from totemlogs.views import *  # noqa
