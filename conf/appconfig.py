import os

# Logging configuration
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s %(message)s'
LOG_DATE = '%Y-%m-%d %I:%M:%S %p'
LOG_ROOT_LEVEL = os.getenv('LOG_ROOT_LEVEL', 'INFO').upper()
LOG_IDENTIFIER = os.getenv('LOG_IDENTIFIER', 'totem-logs')

BOOLEAN_TRUE_VALUES = {"true", "yes", "y", "1", "on"}

API_PORT = int(os.getenv('API_PORT', '9500'))

TOTEM_ENV = os.getenv('TOTEM_ENV', 'local')
CLUSTER_NAME = os.getenv('CLUSTER_NAME', TOTEM_ENV)
SEARCH_INDEX = os.getenv('SEARCH_INDEX', 'logstash-%Y.%m.%d')

SEARCH_SETTINGS = {
    'host': os.getenv('ELASTICSEARCH_HOST', '172.17.42.1'),
    'port': os.getenv('ELASTICSEARCH_PORT', '9200'),
    'default-index': SEARCH_INDEX
}

MIME_JSON = 'application/json'
MIME_HTML = 'text/html'
MIME_HEALTH_V1 = 'application/vnd.orch.health.v1+json'

SCHEMA_ROOT_V1 = 'root-v1'
SCHEMA_HEALTH_V1 = 'health-v1'

HEALTH_OK = 'ok'
HEALTH_FAILED = 'failed'

LEVEL_FAILED = 1
LEVEL_FAILED_WARN = 2
LEVEL_SUCCESS = 3
LEVEL_STARTED = 4
LEVEL_PENDING = 5

# Doc types for elastic search
DOC_TYPE_JOBS = 'jobs'
DOC_TYPE_EVENTS = 'events'

LOG_REQUEST_DEFAULTS = {
    'interval': 5,
    'from-date': None,
    'meta-info': {
        'git': {
            'owner': '*',
            'repository': '*',
            'ref': '*'
        },
        'unit-no': '*',
        'version': '*',
        'unit-type': 'app'
    },
    'program-name': '',
    'page-size': 1000
}
