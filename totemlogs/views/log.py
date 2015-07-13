import datetime
import logging
from threading import Thread
from time import sleep
import arrow
from flask import request
import sys
from conf.appconfig import LOG_REQUEST_DEFAULTS
from totemlogs.server import socketio
from totemlogs.services.log import fetch_logs
from totemlogs.util import dict_merge
from totemlogs.views.util import program_name_for

LOGS_NAMESPACE = '/logs'
LOG_EVENT_NAME = 'logs'
STATUS_EVENT_NAME = 'status'
DEFAULT_INTERVAL_SECONDS = 5

logger = logging.getLogger(__name__)


def emit_status(event_type, socket_id=None, description=None, details=None):
    """
    Emits status
    :param event_type: Type of event
    :type event_type: str
    :param description: Description corresponding to event
    :type description: str
    :param details: Details corresponding to event
    :type details: dict
    :return: None
    """
    try:
        socket_id = socket_id or request.namespace.socket.sessid
        socket = socketio.server.sockets.get(socket_id)
        if socket and socket.active_ns.get(LOGS_NAMESPACE):
            socket[LOGS_NAMESPACE].base_emit(
                STATUS_EVENT_NAME, {
                    'type': event_type,
                    'details': details,
                    'description': description,
                    'date': arrow.utcnow().isoformat(),
                    'component': 'totem-logs'
                })
    except:
        logger.exception(sys.exc_info()[1])


def _emit_logs(socket_id, log_request):
    """
    Fetches and emits logs for given socket
    """
    after_date_str = log_request['after-date']
    page_size = log_request['page-size']
    interval = log_request['interval']
    if after_date_str:
        after_date = arrow.get(after_date_str)
    else:
        after_date = arrow.utcnow()

    program_name = log_request['program-name']

    while socket_id in socketio.server.sockets:
        # Default: Send logs for last 5 minutes
        log_msg = 'Fetching logs for: {} after: {} for socket: {} at ' \
                  'interval of: {}s'.format(program_name,
                                            after_date.isoformat(), socket_id,
                                            interval)
        logger.info(log_msg)
        emit_status(
            'FETCH_LOG',
            description=log_msg,
            details={
                'after-date': after_date.isoformat(),
                'socket-id': socket_id
            },
            socket_id=socket_id
        )
        to_date = arrow.utcnow() - datetime.timedelta(0, 5*60)
        socket = socketio.server.sockets[socket_id]
        if socket.active_ns.get(LOGS_NAMESPACE):

            def fetch(from_):
                try:
                    return fetch_logs(
                        after_date,
                        to_date,
                        program_name=program_name,
                        lines=page_size,
                        from_=from_
                    )
                except:
                    logger.exception('Failed to fetch logs')
                    emit_status('FAILED',
                                description='Failed to fetch logs. Reason: {}'
                                .format(str(sys.exc_info()[1])),
                                socket_id=socket_id)
                    sleep(10)
                    log_stop(socket_id)
                    return

            start_rec = 0
            logs = fetch(start_rec)

            while logs['logs'] and socket_id in socketio.server.sockets and \
                    socket.active_ns.get(LOGS_NAMESPACE):
                socket[LOGS_NAMESPACE].base_emit(LOG_EVENT_NAME, logs['logs'])
                start_rec += page_size
                if start_rec >= logs['meta-info']['count']:
                    break
                else:
                    sleep(interval)
                    logs = fetch(start_rec)
        else:
            # Namespace is not active. return
            return
        after_date = to_date
        sleep(interval)


@socketio.on('connect', namespace=LOGS_NAMESPACE)
def log_connect():
    """
    Handle Websocket connection
    """
    emit_status('WS_CONNECTED', description='Websocket Connected...')


@socketio.on('disconnect', namespace=LOGS_NAMESPACE)
def log_disconnect(socket_id=None):
    """
    Handle websocket disconnect
    """
    socket_id = socket_id or request.namespace.socket.sessid
    logger.info('closed: {}'.format(socket_id))


@socketio.on('stop', namespace=LOGS_NAMESPACE)
def log_stop(socket_id=None):
    socket_id = socket_id or request.namespace.socket.sessid
    socket = socketio.server.sockets.get(socket_id)
    log_msg = 'Logs stopped({})'.format(socket_id)
    emit_status('WS_STOPPED', description=log_msg, socket_id=socket_id)
    logger.info(log_msg)
    if socket and socket.active_ns.get(LOGS_NAMESPACE):
        socket[LOGS_NAMESPACE].disconnect()


@socketio.on('fetch', namespace=LOGS_NAMESPACE)
def log_fetch(log_request):
    log_request = dict_merge(log_request, LOG_REQUEST_DEFAULTS)
    log_request['program-name'] = program_name_for(log_request)
    socket_id = request.namespace.socket.sessid
    Thread(target=_emit_logs, args=(socket_id, log_request)).start()
