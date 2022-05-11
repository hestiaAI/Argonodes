import json


import pytest


from argonodes.nodes import PROTECTED_ATTRS, Root, Tree


@pytest.fixture
def tree_github():
    with open("./tests/inputs/pull_requests_000001.json", "r") as jsonfile:
        json_data = json.loads(jsonfile.read())
        return Tree(json_data)


@pytest.fixture
def tree_google():
    with open("./tests/inputs/2022_MARCH.json", "r") as jsonfile:
        json_data = json.loads(jsonfile.read())
        return Tree(json_data)


def test_tree_correct(tree_github):
    assert tree_github.fieldName == "$"
    assert tree_github.foundType == Root
    assert tree_github.path == "$"


@pytest.mark.parametrize("attr", PROTECTED_ATTRS)
def test_tree_immutable_set(tree_github, attr):
    with pytest.raises(AttributeError):
        tree_github.__setattr__(attr, "dumb")


@pytest.mark.parametrize("attr", PROTECTED_ATTRS)
def test_tree_immutable_del(tree_github, attr):
    with pytest.raises(AttributeError):
        tree_github.__delattr__(attr)


def test_set_of_paths(tree_github):
    pass
