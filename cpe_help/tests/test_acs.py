"""
Module for testing the ACS class
"""

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
