import unittest

from src.cli.client import ClientSync
from src.config import get_configs


class TestClientCase(unittest.TestCase):
    def test_login(self):
        client = ClientSync(qq=get_configs().qq, password=get_configs().password)
        client.login()

    def test_get_config(self):
        print(get_configs())

    def test_query_by_nick(self):
        client = ClientSync(qq=get_configs().qq, password=get_configs().password)
        client.login()
        print(client.query_by_nick("夜夜夜夜夜神月灬"))

    def test_get_battle_list(self):
        client = ClientSync(qq=get_configs().qq, password=get_configs().password)
        client.login()
        for i in client.get_battle_list(client.query_by_nick("夜夜夜夜夜神月灬")[0]):
            print(i)


if __name__ == '__main__':
    unittest.main()
