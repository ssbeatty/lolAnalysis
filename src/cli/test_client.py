import unittest

from src.cli.client import ClientSync
from src.config import get_configs


class TestClientCase(unittest.TestCase):
    def test_login(self):
        client = ClientSync(qq=get_configs().qq, password=get_configs().password)
        client.login()
        print(client.get_cookies())

    def test_get_config(self):
        print(get_configs())


if __name__ == '__main__':
    unittest.main()
