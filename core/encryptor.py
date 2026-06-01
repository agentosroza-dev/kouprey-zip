import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_text(plaintext: str, password: str) -> str:
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(plaintext.encode("utf-8"))
    return base64.urlsafe_b64encode(salt + token).decode("utf-8")


def decrypt_text(ciphertext_b64: str, password: str) -> str:
    raw = base64.urlsafe_b64decode(ciphertext_b64.encode("utf-8"))
    salt = raw[:16]
    token = raw[16:]
    key = _derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token).decode("utf-8")


def encrypt_file(input_path: str, output_path: str, password: str) -> None:
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    f = Fernet(key)
    with open(input_path, "rb") as fin:
        data = fin.read()
    encrypted = f.encrypt(data)
    with open(output_path, "wb") as fout:
        fout.write(salt + encrypted)


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    with open(input_path, "rb") as fin:
        raw = fin.read()
    salt = raw[:16]
    token = raw[16:]
    key = _derive_key(password, salt)
    f = Fernet(key)
    decrypted = f.decrypt(token)
    with open(output_path, "wb") as fout:
        fout.write(decrypted)
