import base64
import hashlib
import hmac
import pickle

from Crypto import Random
from Crypto.Cipher import AES

import config


def encrypt_tuple(t: tuple) -> str:
    data = pickle.dumps(t)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(config.encryption_key, AES.MODE_CFB, iv)
    return base64.b64encode(iv + cipher.encrypt(data)).decode()


def decrypt_tuple(s: str) -> tuple:
    enc = base64.b64decode(s.encode())
    iv = enc[:AES.block_size]
    cipher = AES.new(config.encryption_key, AES.MODE_CFB, iv)
    dec = cipher.decrypt(enc[AES.block_size:])
    return pickle.loads(dec)


def str_hmac(s: str) -> str:
    mac = hmac.new(config.hmac_key, s.encode(), hashlib.sha256).digest()
    return base64.b64encode(mac).decode()


def verify_hmac(s: str, h: str) -> bool:
    mac = str_hmac(s)
    return mac == h
