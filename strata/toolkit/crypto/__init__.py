from .hashes import *
from .symmetric import *
import hashlib
import hmac


def digest(key, data):
    return hmac.new(key, data, hashlib.sha256).digest()