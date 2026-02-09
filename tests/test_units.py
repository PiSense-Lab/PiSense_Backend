from pisense.backend.tests import plus

def test_plus():
    ret = plus(1, 1)
    assert ret == 2
