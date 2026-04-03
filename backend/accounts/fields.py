from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import hashlib

def _fernet():
    # Derive a 32-byte urlsafe key from SECRET_KEY
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))

class EncryptedTextField(models.TextField):
    description = "TextField stored encrypted using Fernet"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
        except Exception:
            return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")
