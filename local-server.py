from gevent import monkey
from conf.appconfig import API_PORT

monkey.patch_all()

from totemlogs.server import socketio, app

if __name__ == '__main__':
    app.debug = False
    socketio.run(app, port=API_PORT, use_reloader=False)
