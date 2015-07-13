from __future__ import absolute_import
from future.builtins import (  # noqa
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)
from functools import wraps
import logging
from elasticsearch import Elasticsearch
from conf.appconfig import SEARCH_SETTINGS

MAPPING_LOCATION = './conf/index-mapping.json'
logger = logging.getLogger(__name__)


def using_search(fun):
    """
    Function wrapper that automatically passes elastic search instance to
    wrapped function.

    :param fun: Function to be wrapped
    :return: Wrapped function.
    """
    @wraps(fun)
    def outer(*args, **kwargs):
        kwargs.setdefault('es', get_search_client())
        kwargs.setdefault('idx', SEARCH_SETTINGS['default-index'])
        return fun(*args, **kwargs)
    return outer


def get_search_client():
    """
    Creates the elasticsearch client instance using SEARCH_SETTINGS

    :return: Instance of Elasticsearch
    :rtype: elasticsearch.Elasticsearch
    """
    return Elasticsearch(hosts=SEARCH_SETTINGS['host'],
                         port=SEARCH_SETTINGS['port'])
