from benny_bean_utils.test import ping

def test_ping():
    assert ping() == "pong"