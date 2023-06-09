from requests import Response
import pathlib
import unittest
import sys
import json
sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))
import game_info
from unittest.mock import patch, Mock

class TestIsRemake(unittest.TestCase):
    def test_remake_game(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertTrue(gi._is_remake(raw_game_info_data_dict={"category": 8}))

    def test_not_remake_game(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertFalse(gi._is_remake(raw_game_info_data_dict={"category": 0}))

class TestIsParent(unittest.TestCase):
    def test_parent_game(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertTrue(gi._is_parent(raw_game_info_data_dict={"id": "1", "parent_game": "1"}))

    def test_not_parent_game(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertFalse(gi._is_parent(raw_game_info_data_dict={"id": "1", "parent_game": "2"}))

class TestIsSports(unittest.TestCase):
    def test_sports_game(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertTrue(gi._is_sports(raw_game_info_data_dict={"genres": [{"name": "Sport"}]}))

    def test_not_sports_game(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertFalse(gi._is_sports(raw_game_info_data_dict={"genres": [{"name": "Not Sport"}]}))

class TestGetImageDictFromDataDict(unittest.TestCase):
    def test_nonexistent_key(self):
        gi = game_info.GameInfo(data_dict={})
        assert len(gi._get_image_dicts_from_data_dict(key="...", number_of_imgs=2)) == 0

class TestExtractImageURLsFromDataDict(unittest.TestCase):
    def test_bad_image_dicts(self):
        gi = game_info.GameInfo(data_dict={})   # empty data dict
        assert len(gi._extract_image_urls_from_data_dict()) == 0
        gi.data_dict = {"cover": {}}    # empty image dict
        assert len(gi._extract_image_urls_from_data_dict()) == 0

    def test_good_image_dicts(self):
        gi = game_info.GameInfo(data_dict={})
        gi.data_dict = {"cover": {"url": "..."}}
        self.assertEqual(gi._extract_image_urls_from_data_dict(), ["https://..."])

class TestDLGameImageEncodeB64(unittest.TestCase):
    def test_bad_image_url(self):
        gi = game_info.GameInfo(data_dict={})
        self.assertRaises((ValueError, TypeError), gi._dl_game_image_encode_b64, "...")

class TestCleanGenresList(unittest.TestCase):
    def test_add_themes_triggered(self):
        gi = game_info.GameInfo(data_dict={})
        res = gi._clean_genres_list(genres=["Genre 1", "Genre 2"], themes=["Stealth"])
        self.assertListEqual(res, ["Genre 1", "Genre 2", "Stealth"])

    def test_add_themes_not_triggered(self):
        gi = game_info.GameInfo(data_dict={})
        res = gi._clean_genres_list(genres=["Genre 1", "Genre 2"], themes=[])
        self.assertListEqual(res, ["Genre 1", "Genre 2"])

    def test_special_cases(self):
        """ Only a portion """
        gi = game_info.GameInfo(data_dict={})
        res = gi._clean_genres_list(genres=["Platform", "Hack and slash/Beat 'em up", "Action"], themes=[])
        self.assertListEqual(res, ["Hack and slash/Beat 'em up", "Platform"])
        res = gi._clean_genres_list(genres=["Action"], themes=[])
        self.assertListEqual(res, ["Action"])
        res = gi._clean_genres_list(genres=["Action", "Fighting"], themes=[])
        self.assertListEqual(res, ["Fighting"])

class TestCleanDataDict(unittest.TestCase):
    """ 
    Note: these tests assume the constructor calls the clean_data_dict method.
    """

    def test_relevant_key_exists_in_raw_dict(self):
        gi = game_info.GameInfo(data_dict={"name": "val"})  
        # we want to see the value unchanged
        self.assertEqual(gi.data_dict["name"], "val")

    def test_irrelevant_key_exists_in_raw_dict(self):
        gi = game_info.GameInfo(data_dict={"bogus_key": "val"})  
        assert "bogus_key" not in gi.data_dict

    def test_good_raw_dict(self):
        d = {"name": "some_name",
        "genres": [{"name": "some_genre"}],
        "involved_companies": [{"developer": True, "publisher": False, "company": {"name": "some_dev"}},
        {"developer": False, "publisher": True, "company": {"name": "some_pub"}}],
        "platforms": [{"name": "p1"}, {"name": "p2"}], "themes": [],
        }
        gi = game_info.GameInfo(data_dict=d)
        expected_cleaned_d = {"name": "some_name", 
        "genres": ["some_genre"], 
        "developers": ["some_dev"], 
        "publisher": "some_pub", 
        "platforms": ["p1", "p2"]}
        self.assertDictEqual(expected_cleaned_d, gi.data_dict)

if __name__ == "__main__":
    unittest.main()
