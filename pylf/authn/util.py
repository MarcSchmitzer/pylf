
import hashlib
import random

from base64 import b64decode, b64encode


SALT_LEN = 8
HASH_TYPE = "sha512"


def check_password(hashdict, password):
    digest = hashlib.new(hashdict["type"])
    digest.update(b64decode(hashdict["salt"]))
    digest.update(password.encode("utf8"))
    return digest.digest() == b64decode(hashdict["hash"])


def make_hashdict(password, salt_len=SALT_LEN, hash_type=HASH_TYPE):
    salt = random.getrandbits(salt_len * 8)
    salt = salt.to_bytes(salt_len, "little")
    digest = hashlib.new(hash_type)
    digest.update(salt)
    digest.update(password.encode("utf8"))
    return {
        "type": hash_type,
        "salt": b64encode(salt),
        "hash": b64encode(digest.digest()),
    }
