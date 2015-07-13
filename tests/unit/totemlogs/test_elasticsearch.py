from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from mock import patch
from nose.tools import eq_

from totemlogs.elasticsearch import using_search


SEARCH_SETTINGS = {
    'host': 'mockhost',
    'port': 10001,
    'default-index': 'mock-index'
}


@using_search
def mock_fn(mock_input, ret_value=None, es=None, idx=None):
    return ret_value


@using_search
def mock_fn_no_positional_args(es=None, idx=None, ret_value=None):
    return ret_value


@patch('totemlogs.elasticsearch.Elasticsearch')
@patch.dict('totemlogs.elasticsearch.SEARCH_SETTINGS',
            SEARCH_SETTINGS)
def test_using_search(m_es):
    """
    Should invoke function when search is enabled
    :return:
    """

    # When: I invoke function wrapped with using_search
    ret_value = mock_fn('mock-input', ret_value='mock-output')

    # Then: Function gets called as expected
    m_es.assert_called_once_with(hosts='mockhost', port=10001)
    eq_(ret_value, 'mock-output')
