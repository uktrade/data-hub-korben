import binascii
import functools
import os
import pickle
from unittest import mock
from unittest import TestCase
from cryptography.fernet import Fernet

from korben import config, services
from korben.cdms_api.cookie_storage import CookieStorage


class BaseCookieStorageTestCase(TestCase):
    def setUp(self):
        config.cdms_cookie_key = Fernet.generate_key()
        self.fernet = Fernet(config.cdms_cookie_key)
        if services.redis.get(config.cdms_cookie_path):
            services.redis.delete(config.cdms_cookie_path)

    def write_cookie(self, cookie={}):
        ciphertext = self.fernet.encrypt(pickle.dumps(cookie))
        services.redis.set(config.cdms_cookie_path, ciphertext)

    def assertCookieDoesNotExist(self):
        self.assertFalse(os.path.exists(config.cdms_cookie_path))


class SetupStorageTestCase(BaseCookieStorageTestCase):
    def test_non_valid_key(self):
        with config.temporarily(cdms_cookie_key='something'):
            cls_closed = functools.partial(
                CookieStorage, config.cdms_cookie_path
            )
            self.assertRaises(config.ConfigError, cls_closed)


class ReadCookieStorageTestCase(BaseCookieStorageTestCase):
    def test_returns_None_if_cookie_doesnt_exist(self):
        storage = CookieStorage(config.cdms_cookie_path)
        self.assertEqual(storage.read(), None)

    def test_returns_None_if_cookie_invalid(self):
        """
        If the cookie is invalid (e.g. not encrypted) => return None and delete cookie.
        """
        self.write_cookie()

        with mock.patch(
            'korben.cdms_api.cookie_storage.services.redis_bytes.get',
            mock.mock_open(read_data='something')
        ):
            storage = CookieStorage(config.cdms_cookie_path)
            self.assertEqual(storage.read(), None)

        self.assertCookieDoesNotExist()

    def test_returns_None_if_encrypted_with_different_key(self):
        """
        If the cookie was encrypted with different secret key => return None and delete cookie.
        """
        self.write_cookie()
        encrypted_cookie = Fernet(Fernet.generate_key()).encrypt(pickle.dumps('something'))
        services.redis_bytes.set(config.cdms_cookie_path, encrypted_cookie)
        storage = CookieStorage(config.cdms_cookie_path)
        self.assertEqual(storage.read(), None)

        self.assertCookieDoesNotExist()

    def test_read(self):
        cookie = {'key': 'value'}
        self.write_cookie(cookie)
        storage = CookieStorage(config.cdms_cookie_path)
        self.assertEqual(storage.read(), cookie)


class WriteCookieStorageTestCase(BaseCookieStorageTestCase):
    def test_write(self):
        cookie = {'key': 'value'}
        storage = CookieStorage(config.cdms_cookie_path)
        storage.write(cookie)
        ciphertext = self.fernet.decrypt(
            services.redis_bytes.get(config.cdms_cookie_path)
        )
        cookie_in_redis = pickle.loads(ciphertext)
        self.assertEqual(cookie_in_redis, cookie)


class ExistsCookieStorageTestCase(BaseCookieStorageTestCase):
    def test_doesnt_exists(self):
        self.assertFalse(services.redis.get(config.cdms_cookie_path))

    def test_exists(self):
        self.write_cookie()
        self.assertTrue(services.redis.get(config.cdms_cookie_path))


class ResetCookieStorageTestCase(BaseCookieStorageTestCase):
    def test_reset(self):
        self.write_cookie()
        storage = CookieStorage(config.cdms_cookie_path)
        storage.reset()
        self.assertFalse(services.redis.get(config.cdms_cookie_path))
