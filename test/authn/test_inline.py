
import configparser
from io import StringIO

from pytest import fixture

from pylf.authn.inline import InlineAuthenticator

CFG = """
[authentication]
type = inline
users = {
    "marc": {
      "name": "Marc Schmitzer",
      "password": {
        "type": "sha512",
        "salt": "e3sXQn0V8nE=",
        "hash": "n/bK26hk3mXpF0qdLlTPQ3IXxRRmrWfdts/H7K1bqaj+uJjNC1CXZg2pAxfv7gOVUEU9YOQ6TlHvb5kuZfcXrQ=="	
      }
    }
  }
"""


@fixture
def config():
    cfg = configparser.ConfigParser()
    cfg.readfp(StringIO(CFG))
    return cfg["authentication"]


def test_from_config(config):
    authr = InlineAuthenticator.from_config(config)
    assert "marc" in authr


def test_authenticate_ok(config):
    authr = InlineAuthenticator.from_config(config)
    assert authr("marc", "test1234")


def test_authenticate_fail_password(config):
    authr = InlineAuthenticator.from_config(config)
    assert authr("marc", "test4321") is None


def test_authenticate_fail_account(config):
    authr = InlineAuthenticator.from_config(config)
    assert authr("noone", "test4321") is None
