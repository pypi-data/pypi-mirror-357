from cryptography.fernet import Fernet
import base64
import os
import hashlib

# Chave derivada de um segredo fixo (exemplo didático, veja nota abaixo)
SECRET_KEY = b"sparkflint-secret-key"
FERNET_KEY = base64.urlsafe_b64encode(hashlib.sha256(SECRET_KEY).digest())
fernet = Fernet(FERNET_KEY)


def encrypt_password(password: str) -> str:
    """
    Criptografa a senha em formato seguro.
    """
    if not password:
        return password
    token = fernet.encrypt(password.encode())
    return token.decode()


def decrypt_password(token: str) -> str:
    """
    Descriptografa a senha criptografada.
    """
    decrypted = fernet.decrypt(token.encode())
    return decrypted.decode()
