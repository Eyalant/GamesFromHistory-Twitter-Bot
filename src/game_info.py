import typing
import json
import base64
import requests
from datetime import datetime
from pprint import pformat


class GameInfo:
    """
    Wrapper around the game data dict. Contains methods to parse, clean and download
    images listed in the data dict.
    """

    def __init__(self, data_dict: typing.Dict[str, typing.Any], do_clean_dict: typing.Optional[bool] = True):
        try:
            if (not self._is_parent(data_dict)) or (self._is_sports(data_dict)):
                raise Exception(
                    "Game isn't an ancestor, or it's a sports game")
            self.data_dict: typing.Dict[str, typing.Any] = GameInfo._clean_data_dict(
                data_dict) if do_clean_dict else data_dict
            self.images: typing.List[str] = self._dl_game_images_to_ram()
            self.heb_game_genres: typing.Dict[str, str] = {
                "Fighting": "משחק הלחימה",
                "Shooter": "השוטר",
                "Music": "משחק הקצב",
                "Platform": "הפלטפורמר",
                "Puzzle": "הפאזלר",
                "Racing": "משחק המירוצים",
                "Real Time Strategy (RTS)": "משחק האסטרטגיה בזמן-אמת",
                "Role-playing (RPG)": "משחק התפקידים",
                "Simulator": "משחק הסימולציה",
                "Strategy": "משחק האסטרטגיה",
                "Turn-based strategy (TBS)": "משחק האסטרטגיה בתורים",
                "Tactical": "משחק הטקטיקה",
                "Quiz/Trivia": "משחק הטריוויה",
                "Hack and slash/Beat 'em up": "משחק ההאק-אנד-סלאש",
                "Adventure": "משחק ההרפתקה",
                "Arcade": "משחק הארקייד",
                "Visual Novel": "הויז'ואל נובל",
                "Indie": "משחק האינדי",
                "Card & Board Game": "משחק הקלפים/לוח",
                "MOBA": "המובה",
                        "Point-and-click": "משחק הפוינט-אנד-קליק"
            }
        except Exception as e:
            raise Exception("Could not create a GameInfo object") from e

    def __str__(self) -> str:
        """
        A string representation of a GameInfo instance. This is the text to be tweeted.
        """
        try:
            pub: str = self.data_dict.get("publisher", None)
            pub_text: str = f"""מפיצה: {self.data_dict.get("publisher", None)}""" if pub else ""
            wiki_url: str = self.data_dict.get("wiki_url", None)
            wiki_text: str = f"""לערך הוויקי'): {wiki_url}""" + "\n" if wiki_url else "\n"
            test_img: str = self.data_dict.get("cover", None)
            intro_text: str = "".join([
                "{} {} חוגג {} שנים לשחרורו!".format(self._translate_game_genre(self.data_dict["genre"]),
                                                     self.data_dict["name"], datetime.now().year - self.data_dict["year"]),
                " הוא יצא היום בשנת {}.".format(self.data_dict["year"])
            ])
            info_text: str = "\n".join([
                "מפתחת: {}".format(", ".join(self.data_dict["developers"])),
                pub_text,
                "פלטפורמות: {}".format(", ".join(self.data_dict["platforms"]))
            ])
            tweet: str = intro_text + "\n"*2 + info_text + "\n"
            if len(tweet) + 23 <= 180:
                tweet += wiki_text
            return tweet
        except Exception as e:
            raise Exception(
                "Could not create a string repr. of a GameInfo") from e

    @staticmethod
    def _is_parent(game_info_data_dict: typing.Dict[str, typing.Any]) -> bool:
        """
        Checks if the game is a first-release or a DLC / Expansion Pack / Special Edition.
        """
        if (parent_game := game_info_data_dict.get("parent_game", None)) and (id := game_info_data_dict.get("id", None)):
            if parent_game != id:
                return False
        return True

    @staticmethod
    def _is_sports(game_info_data_dict: typing.Dict[str, typing.Any]) -> bool:
        """
        Checks if the game is a sports title.
        """
        try:
            if (genres := game_info_data_dict.get("genres", None)):
                if genres[0]["name"] == "Sport":
                    return True
            return False
        except (IndexError, KeyError):
            raise

    def _translate_game_genre(self, genre: str):
        """
        Translates the game genre from English to Hebrew.
        """
        try:
            return self.heb_game_genres[genre]
        except KeyError:
            return "המשחק"

    def _get_image_dict_from_data_dict(self, key: str) -> typing.Dict[str, str]:
        """
        Gets the first single-image dictionary with the given name from the data dict. 
        """
        if dictlist := self.data_dict.get(key, None):
            return dictlist[0]  # grab first screenshot or artwork
        return {}

    def _extract_image_urls_from_data_dict(self) -> typing.List[str]:
        """
        Extracts the image URLs from the game data dict.
        """

        def _get_image_url_from_image_dict(image_dict: typing.Dict[str, str]) -> str:
            """
            Extracts a single image URL the image dict, contained in the game data dict.
            """
            try:
                image_url: str = image_dict["url"].lstrip(
                    "//").replace("t_thumb", "t_original")
                if not image_url.startswith("http"):
                    image_url = "https://" + image_url
                return image_url
            except (AttributeError, KeyError) as e:
                raise Exception(
                    f"Could not extract image urls from this image dict: {pformat(image_dict)}") from e

        try:
            image_dicts: typing.List[typing.Dict[str, str]] = [
                self.data_dict.get("cover"),  # type: ignore
                self._get_image_dict_from_data_dict(key="screenshots"),
                self._get_image_dict_from_data_dict(key="artworks")]
            return [_get_image_url_from_image_dict(d) for d in image_dicts if d]
        except Exception as e:
            raise ValueError(
                "Could not extract image urls from GameInfo data dict") from e

    @staticmethod
    def _dl_game_image_encode_b64(image_url: str = "") -> str:
        """
        Downloads a single image from a URL as b64, then decodes it to a UTF-8 string.
        """
        try:
            return base64.b64encode(requests.get(url=image_url).content).decode('utf-8')
        except (ValueError, TypeError):
            raise

    def _dl_game_images_to_ram(self) -> typing.List[str]:
        """
        Downloads this GameInfo's images to RAM.
        """
        try:
            image_urls: typing.List[str] = self._extract_image_urls_from_data_dict(
            )
            utf8_images: typing.List[str] = [
                GameInfo._dl_game_image_encode_b64(url) for url in image_urls]
            return utf8_images
        except Exception as e:
            raise Exception("Could not download GameInfo images to RAM") from e

    @staticmethod
    def _clean_data_dict(game_info_data_dict: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        Cleans and parses the given game data dict.
        """
        try:
            ret: typing.Dict[str, typing.Any] = {"developers": []}
            for key in ("name", "summary", "aggregated_rating_count",
                        "aggregated_rating", "cover", "artworks", "screenshots"):
                if val := game_info_data_dict.get(key, None):
                    ret[key] = val

            if genres := game_info_data_dict.get("genres", None):
                ret["genre"] = genres[0]["name"]
            if companies := game_info_data_dict.get("involved_companies", None):
                for d in companies:
                    if d["developer"]:
                        ret["developers"].append(d["company"]["name"])
                    if d["publisher"]:
                        ret["publisher"] = d["company"]["name"]
            if platforms := game_info_data_dict.get("platforms", None):
                ret["platforms"] = [p["name"] for p in platforms]
            if websites := game_info_data_dict.get("websites", None):
                for site in websites:
                    if site["category"] == 3:
                        ret["wiki_url"] = site["url"]
                        break

            return ret
        except KeyError as e:
            raise Exception("Could not clean GameInfo data dict") from e


if __name__ == "__main__":
    pass
