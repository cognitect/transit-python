from transit.transit_types import Set, Dict, Vector



def test_set_equality():
    assert Set([]) == set()
    assert not Set([Set([])]) == set()
    assert not Set([{}]) == set()
    assert Set([{}]) == Set([{}])
    assert set() == Set([])

def test_dict_equality():
    assert Dict([]) == dict()
    assert dict() == Dict([])
    assert {"f":2} == Dict(f = 2)

    assert hash(Dict(f = 2))

def test_list_equality():
    assert Vector([]) == []
    assert [] == Vector([])

    assert hash(Vector([]))
