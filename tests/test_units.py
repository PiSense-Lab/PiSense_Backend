from pisense.backend.tests import plus

def test_plus(): # Temporary testing for pytest, should be removed once we have real code
    ret = plus(1, 1)
    assert ret == 2

