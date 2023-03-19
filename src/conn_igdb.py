import requests
import typing
import base64
import json
import logging
from pprint import pformat
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass(init=False)
class IGDB_Date():
    """ 
    A game release date to query. Contains the start and end years
    in both datetime and unix timestamp formats.
    """

    def __init__(self, lower_bound: datetime, upper_bound: datetime) -> None:
        self.lower_bound: typing.Dict[str, typing.Union[datetime, int]] = {"dt": lower_bound,
                                                                           "ts": int(lower_bound.timestamp())}
        self.upper_bound: typing.Dict[str, typing.Union[datetime, int]] = {"dt": upper_bound,
                                                                           "ts": int(upper_bound.timestamp())}

    def __repr__(self) -> str:
        return "IGDB Date:\n" + "from: " + pformat(self.lower_bound) + "\n" + "to: " + pformat(self.upper_bound)


class IGDB:
    """
    Contains tokens and methods to access the IGDB API.
    """
    API_URL: str = "https://api.igdb.com/v4/"
    TOKEN_URL: str = "https://id.twitch.tv/oauth2/token"

    def __init__(self, client_id: str, client_secret: str, bearer: typing.Optional[str] = ""):
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        try:
            bearer_token: str = bearer if bearer else self.get_token()
        except Exception as e:
            raise ValueError("Could not retrieve IGDB bearer token.") from e
        self.auth_header: str = "Bearer " + bearer_token

    def get_token(self) -> str:
        r: requests.Response = requests.post(url=IGDB.TOKEN_URL,
                                             params={"client_id": self.client_id,
                                                     "client_secret": self.client_secret,
                                                     "grant_type": "client_credentials"})
        try:
            r_dict: typing.Dict[str, typing.Any] = r.json()
            return r_dict["access_token"]
        except (json.JSONDecodeError, KeyError):
            raise

    def get_games_endpoint(self, raw_body: str = ""):
        """ 
        Query the 'games' endpoint from the IGDB API using the given request body.
        """
        r: typing.List[typing.Dict[str, typing.Any]] = requests.post(url=IGDB.API_URL + "games",
                                                                     headers={"Client-ID": self.client_id,
                                                                              "Authorization": self.auth_header},
                                                                     data=raw_body).json()
        try:
            if r[0].get("status", None) == 500:
                raise ValueError(
                    "IGDB Internal Server Error; best to try again in a while.")
        except IndexError:
            return r
        return r


if __name__ == "__main__":
    pass
