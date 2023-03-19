from requests import Response
import pathlib
import unittest
import sys
import json
from os import environ
sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))
import conn_redis
import redis
from unittest.mock import patch, Mock
from dotenv import load_dotenv

class TestConnect(unittest.TestCase):
    def test_connection_error(self):
        self.assertRaises(ConnectionError, conn_redis.connect, "bad URL")

class TestGetdelSingleGameDataDict(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.redis_url = environ.get("REDIS_URL")

    @patch("redis.Redis.randomkey")
    def test_no_game_returned(self, mock_randomkey):
        mock_randomkey.return_value = None
        key = conn_redis.getdel_single_game_data_dict(redis_client=conn_redis.connect(environ.get("REDIS_URL")))
        self.assertIsNone(key)

    def test_bad_redis_client(self):
        self.assertRaises(ConnectionError, conn_redis.getdel_single_game_data_dict, None)

if __name__ == "__main__":
    unittest.main()