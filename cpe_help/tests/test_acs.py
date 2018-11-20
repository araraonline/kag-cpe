"""
Module for testing the ACS class
"""

import pytest

from cpe_help.acs import get_acs


def test_simple_query():
    acs = get_acs()

    variables = ["NAME", "B01001_002E", "B01001_026E"]
    geography = 'county'
    inside = 'state:01'

    result = acs._query(variables, geography, inside)

    assert len(result) > 0
    assert len(result[0]) == 5


def test_big_query():
    acs = get_acs()

    variables = ["B01001_002E"] * 50
    geography = 'county'
    inside = 'state:01'
    result = acs._query(variables, geography, inside)

    assert len(result) > 0
    assert len(result[0]) == 52


def test_simple_data():
    acs = get_acs()

    variables = ["NAME", "B01001_002E", "B01001_026E"]
    geography = 'county'
    inside = 'state:01'
    result = acs.data(variables, geography, inside)

    result_cols = set(result.columns)
    expected_cols = {'B01001_002E', 'B01001_026E', 'NAME', 'county', 'state'}
    assert result.shape[1] == 5
    assert result_cols == expected_cols


def test_big_data():
    acs = get_acs()

    variables = ["B01001_002E"] * 50 + ['NAME']
    geography = 'county'
    inside = 'state:01'
    result = acs.data(variables, geography, inside)

    assert result.shape[1] == 4
    assert set(result.columns) == {'B01001_002E', 'NAME', 'county', 'state'}


def test_hierarchic_inside():
    acs = get_acs()

    variables = ["NAME", "B01001_002E", "B01001_026E"]
    geography = 'tract'
    inside = 'state:01 county:001'
    result = acs.data(variables, geography, inside)

    result_cols = set(result.columns)
    expected_cols = set(variables) | set(['tract', 'state', 'county'])
    assert result_cols == expected_cols


def test_simple_data_dictvariables():
    acs = get_acs()

    variables = {
        'NAME': 'Geography Name',
        'B01001_002E': 'Male Population',
        'B01001_026E': 'Female Population',
    }
    geography = 'county'
    inside = 'state:01'

    result = acs.data(variables, geography, inside)

    result_cols = set(result.columns)
    expected_cols = set(variables.values()) | {'state', 'county'}
    assert result_cols == expected_cols


def test_dtypes():
    acs = get_acs()

    variables = ["NAME", "B01001_002E", "B01001_026E"]
    geography = 'county'
    inside = 'state:01'
    df = acs.data(variables, geography, inside)

    # numeric columns
    result = set(c for c in df.select_dtypes('number').columns)
    expected = {'B01001_002E', 'B01001_026E'}
    assert result == expected

    # object columns (string)
    result = set(c for c in df.select_dtypes('object').columns)
    expected = {'NAME', 'county', 'state'}
    assert result == expected


def test_null_variables():
    # When we make a request with a variable not available at the
    # desired level, the Census returns nulls, and the ACS class should
    # generate a warning.

    acs = get_acs()

    variables = {
        'B01001_001E': 'VARIABLE_OKAY',
        'B06009_001E': 'VARIABLE_NULLS',
    }
    geography = 'block group'
    inside = 'state:01 county:001'

    with pytest.warns(UserWarning) as record:
        result = acs.data(variables, geography, inside)

    assert 'B06009_001E' in record[0].message.args[0]
    assert 'B01001_001E' not in record[0].message.args[0]
    assert set(result.columns) >= set(variables.values())
    # exactly one column with all nulls
    assert result.isnull().all(axis=0).sum() == 1
