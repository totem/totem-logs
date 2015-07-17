import datetime
import json
import logging
from threading import Thread
from time import sleep
import arrow
import sys
from geventwebsocket import WebSocketError
from conf.appconfig import LOG_REQUEST_DEFAULTS
from totemlogs.server import sockets
from totemlogs.services.log import fetch_logs
from totemlogs.util import dict_merge
from totemlogs.views.util import program_name_for

LOGS_NAMESPACE = '/logs'
LOG_EVENT_NAME = 'logs'
STATUS_EVENT_NAME = 'status'
DEFAULT_INTERVAL_SECONDS = 5

logger = logging.getLogger(__name__)


@sockets.route('/logs')
def ws_logs(ws):
    log_request_str = ws.receive()
    if not log_request_str:
        return
    log_request = json.loads(log_request_str)
    log_request = dict_merge(log_request, LOG_REQUEST_DEFAULTS)
    log_request['program-name'] = program_name_for(log_request)
    Thread(target=_emit_log, args=(ws, log_request)).start()
    while not ws.closed:
        try:
            ws.receive()
        except WebSocketError:
            # Socket disconnected.
            break


def _emit_event(event_type, ws, description=None, details=None):
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
        if not ws.closed:
            ws.send(
                json.dumps({
                    'type': event_type,
                    'details': details,
                    'description': description,
                    'date': arrow.utcnow().isoformat()
                }))
    except:
        logger.exception(sys.exc_info()[1])


def _emit_log(ws, log_request):
    """
    Fetches and emits logs for given socket
    """
    after_date_str = log_request['after-date']
    page_size = log_request['page-size']
    interval = log_request['interval']
    to_date = arrow.utcnow()
    if after_date_str:
        after_date = arrow.get(after_date_str)
    else:
        after_date = to_date - datetime.timedelta(0, 5*60)

    program_name = log_request['program-name']

    while not ws.closed:
        log_msg = 'Fetching logs for: {} after: {} at ' \
                  'interval of: {}s'.format(program_name,
                                            after_date.isoformat(),
                                            interval)
        logger.info(log_msg)
        _emit_event(
            'FETCH_LOG', ws,
            description=log_msg,
            details={
                'after-date': after_date.isoformat()
            }
        )
        to_date = arrow.utcnow()

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
                _emit_event('FAILED', ws,
                            description='Failed to fetch logs. Reason: {}'
                            .format(str(sys.exc_info()[1])))
                sleep(10)
                return

        start_rec = 0
        logs = fetch(start_rec)

        while not ws.closed and logs and logs['meta-info']['count'] > 0:
            start_rec += page_size
            _emit_event(
                'LOGS', ws, description='Fetched logs', details=logs)
            if start_rec >= logs['meta-info']['count']:
                break
            else:
                sleep(interval)
                logs = fetch(start_rec)
        after_date = to_date
        sleep(interval)
