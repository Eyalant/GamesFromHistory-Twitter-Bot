from requests import Response
import pathlib
import unittest
import sys
import json
sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))
import conn_twitter
from unittest.mock import patch, Mock

class TestUploadImages(unittest.TestCase):
    def test_empty_image_binaries(self):
        twtr = conn_twitter.Twitter()
        assert len(twtr.upload_images(image_binaries=[])) == 0

if __name__ == "__main__":
    unittest.main()