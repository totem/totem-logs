from totemlogs.elasticsearch import using_search

import datetime


def _generate_indexes(from_date, to_date, pattern):
    start_date = from_date.date()
    end_date = to_date.date()
    while start_date <= end_date:
        yield start_date.strftime(pattern)
        start_date += datetime.timedelta(1)


@using_search
def get_search_indexes(from_date, to_date, es=None, idx=None):
    check_indexes = ','.join(_generate_indexes(from_date, to_date, idx))
    return es.indices.get_aliases(index=check_indexes, params={
        'ignore_unavailable': 'true',
        'ignore_missing': 'true'
    }).keys()


@using_search
def fetch_logs(after_date, to_date, program_name='*', lines=1000, from_=0,
               es=None, idx=None):
    idxs = get_search_indexes(after_date, to_date)
    if not idxs:
        return {
            'meta-info': {
                'count': 0
            },
            'logs': []
        }
    result = es.search(index=idxs, size=lines, from_=from_, body={
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "@timestamp": {
                                "gt": after_date.isoformat(),
                                "lte":  to_date.isoformat()
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "program_name": program_name
                        }
                    }

                ]

            }
        },
        "_source": ["@timestamp", "program_name", "short_message"],
        "sort": [
            {"@timestamp": "asc"},
        ]
    })
    return {
        'meta-info': {
            'count': result['hits']['total']
        },
        'logs': [
            {
                'timestamp': record['_source']['@timestamp'],
                'message': record['_source']['short_message'],
                'program-name': record['_source']['program_name']
            } for record in result['hits']['hits']
        ]
    }
