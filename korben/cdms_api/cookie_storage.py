import pickle

from cryptography.fernet import Fernet, InvalidToken

from korben import config
from korben import services


class CookieStorage(object):
    """
    Stores a cookie encrypting before writing it and decrypting it after
    reading it.
    """

    def __init__(self, cookie_path):
        self.cookie_path = cookie_path
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
        cookie_bytes = services.redis_bytes.get(self.cookie_path)
        if cookie_bytes:
            try:
                ciphertext = self.crypto.decrypt(cookie_bytes)
                return pickle.loads(ciphertext)
            except (InvalidToken, TypeError):
                self.reset()
        return None

    def write(self, cookie):
        """
        Writes a cookie overriding any existing ones.
        """
        ciphertext = self.crypto.encrypt(pickle.dumps(cookie))
        services.redis.set(self.cookie_path, ciphertext, ex=7200)  # 2 hours

    def reset(self):
        """
        Deletes the cookie.
        """
        services.redis.delete(self.cookie_path)
