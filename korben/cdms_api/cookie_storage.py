import os
import pickle

from cryptography.fernet import Fernet, InvalidToken
from korben import config


class CookieStorage(object):
    """
    Stores a cookie encrypting before writing it and decrypting it after reading it.
    """

    def __init__(self):
        try:
            self.crypto = Fernet(config.cdms_cookie_key)
        except Exception:
            raise config.ConfigError("""
`cdms_cookie_key` has to be a valid Fernet key, generate one with:

>>> from cryptography.fernet import Fernet
>>> Fernet.generate_key()
""")

    def read(self):
        """
        Returns the cookie if valid and exists, None otherwise.
        """
        if self.exists():
            with open(config.cookie_file, 'rb') as f:
                try:
                    ciphertext = self.crypto.decrypt(f.read())
                    return pickle.loads(ciphertext)
                except (InvalidToken, TypeError):
                    self.reset()
        return None

    def write(self, cookie):
        """
        Writes a cookie overriding any existing ones.
        """
        ciphertext = self.crypto.encrypt(pickle.dumps(cookie))
        with open(config.cookie_file, 'wb') as f:
            f.write(ciphertext)

    def exists(self):
        """
        Returns True if the cookie exists, False otherwise.
        """
        return os.path.exists(config.cookie_file)

    def reset(self):
        """
        Deletes the cookie.
        """
        if self.exists():
            os.remove(config.cookie_file)
