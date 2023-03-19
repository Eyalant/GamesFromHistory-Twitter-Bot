from requests import Response
import pathlib
import unittest
import sys
import json
from os import environ
sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))
from conn_igdb import IGDB
from unittest.mock import patch, Mock
from dotenv import load_dotenv

class TestInit(unittest.TestCase):
    def test_bearer_arg(self):
        igdb = IGDB(client_id="",
                    client_secret="",
                    bearer="some_token")
        self.assertEqual(igdb.auth_header, "Bearer some_token")


class TestGetToken(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.client_id = environ.get("IGDB_CLIENT_ID")
        self.client_secret = environ.get("IGDB_CLIENT_SECRET")

    @patch("requests.post")
    def test_successful_request(self, mock_post):
        expected_r = Response()
        expected_r.json = lambda : {"access_token": "something"}
        mock_post.configure_mock(return_value=expected_r)
        igdb = IGDB(client_id=self.client_id,
                        client_secret=self.client_secret,
                        bearer="...")
        resp = igdb.get_token()
        self.assertEqual(resp, "something")

    def test_unsuccessful_request(self):
        igdb = IGDB(client_id="", client_secret="", bearer="...")
        self.assertRaises((json.JSONDecodeError, KeyError), igdb.get_token)

class TestGetGamesEndpoint(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.client_id = environ.get("IGDB_CLIENT_ID")
        self.client_secret = environ.get("IGDB_CLIENT_SECRET")

    @patch("requests.post")
    def test_no_received_games(self, mock_post):
        igdb = IGDB(client_id=self.client_id,
                client_secret=self.client_secret,)
        expected_r = Response()
        expected_r.json = lambda : []
        mock_post.configure_mock(return_value=expected_r)
        ret = igdb.get_games_endpoint(raw_body="fields *")
        assert len(ret) == 0

    @patch("requests.post")
    def test_internal_server_error(self, mock_post):
        igdb = IGDB(client_id=self.client_id,
                client_secret=self.client_secret,)
        expected_r = Response()
        expected_r.json = lambda : [{"status": 500}]
        mock_post.configure_mock(return_value=expected_r)
        self.assertRaises(ValueError, igdb.get_games_endpoint, raw_body="fields *")

if __name__ == "__main__":
    unittest.main()
