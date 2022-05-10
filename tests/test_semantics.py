import json


import pytest


from argonodes.nodes import Tree


@pytest.fixture
def tree_github():
    with open("./inputs/pull_requests_000001.json7", "r") as jsonfile:
        json_data = json.loads(jsonfile.read())
        return Tree(json_data)


@pytest.fixture
def tree_google():
    with open("./inputs/2022_MARCH.json", "r") as jsonfile:
        json_data = json.loads(jsonfile.read())
        return Tree(json_data)


def test_sample():
    assert True
