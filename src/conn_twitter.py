import requests
from requests_oauthlib import OAuth1
from os import environ
import typing


class Twitter:
    """
    Contains tokens and methods to access the Twitter API (v1.1 for media, v2 for tweeting).
    """

    def __init__(self):
        self.dev_api_key = environ.get("TWITTER_DEV_API_KEY")
        self.dev_api_secret = environ.get("TWITTER_DEV_API_SECRET")
        self.dev_user_id = environ.get("TWITTER_DEV_USER_ID")
        self.user_access_token = environ.get("TWITTER_USER_ACCESS_TOKEN")
        self.user_access_token_secret = environ.get("TWITTER_USER_ACCESS_TOKEN_SECRET")
        try:
            self.auth: OAuth1 = OAuth1(client_key=self.dev_api_key, client_secret=self.dev_api_secret, resource_owner_key=self.user_access_token,
                                       resource_owner_secret=self.user_access_token_secret)
        except Exception as e:
            raise ValueError(
                "Could not create OAuth1 twitter handler, and thus couldn't create a Twitter instance") from e

    def upload_images(self, image_binaries: typing.List[str]) -> typing.List[str]:
        """
        Upload the given image binaries from RAM to Twitter and retieve their Twitter media ids.
        """
        media_ids: typing.List[str] = []
        try:
            for bin in image_binaries:
                r = requests.post(url="https://upload.twitter.com/1.1/media/upload.json",
                                  data={"media": bin, "media_category": "TWEET_IMAGE",
                                        "additional_owners": self.dev_user_id},
                                  auth=self.auth)
                media_ids.append(r.json().get("media_id_string", ""))
            return media_ids
        except Exception as e:
            raise Exception(
                "Could not upload images and retrieve twitter media_ids") from e

    def make_tweet(self, tweet_text: str, media_ids: typing.List[str]) -> typing.Dict[str, typing.Any]:
        """
        Create a payload that can be tweeted using the tweet text and Twitter media ids.
        """
        return {"text": tweet_text, "media": {"media_ids": media_ids}}

    def tweet(self, payload: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        Tweet the given payload using the Twitter API.
        """
        try:
            resp = requests.request(
                "POST",
                "https://api.twitter.com/2/tweets",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                },
                auth=self.auth,
            )
            return resp.json()
        except Exception as e:
            raise ValueError("Could not tweet the given payload") from e


if __name__ == "__main__":
    pass
