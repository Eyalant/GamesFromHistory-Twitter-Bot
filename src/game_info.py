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
    MAX_TWITTER_URL_LENGTH: int = 23

    def __init__(self, data_dict: typing.Dict[str, typing.Any]):
        try:
            self.data_dict: typing.Dict[str, typing.Any] = GameInfo._clean_data_dict(
                data_dict)
            self.images: typing.List[str] = self._dl_game_images_to_ram()
            self.heb_game_genres_themes: typing.Dict[str, str] = {
                "Fighting": "לחימה",
                "Stealth": "התגנבות",
                "Horror": "אימה",
                "Action": "אקשן",
                "Fantasy": "פנטזיה",
                "Shooter": "ירי",
                "Music": "קצב",
                "Platform": "פלטפורמה",
                "Puzzle": "פאזלים",
                "Racing": "מירוצים",
                "Real Time Strategy (RTS)": "אסטרטגיה בזמן-אמת",
                "Role-playing (RPG)": "תפקידים",
                "Simulator": "סימולציה",
                "Strategy": "אסטרטגיה",
                "Turn-based strategy (TBS)": "אסטרטגיה בתורים",
                "Tactical": "טקטיקה",
                "Quiz/Trivia": "טריוויה",
                "Hack and slash/Beat 'em up": "האק-אנד-סלאש",
                "Adventure": "הרפתקה",
                "Arcade": "ארקייד",
                "Visual Novel": "ויז'ואל נובל",
                "Indie": "אינדי",
                "Card & Board Game": "קלפים ולוח",
                "MOBA": "מובה",
                "Point-and-click": "פוינט-אנד-קליק"
            }
            self.heb_platforms: typing.Dict[str, str] = {
                "PlayStation": "פס1",
                "PlayStation 2": "פס2",
                "PlayStation 3": "פס3",
                "PlayStation 4": "פס4",
                "PlayStation 5": "פס5",
                "PlayStation Portable": "PSP",
                "PlayStation Vita": "ויטה",
                "PlayStation VR": "PSVR",
                "PlayStation VR2": "PSVR2",
                "PC (Microsoft Windows)": "פיסי",
                "Sega Game Gear": "גיימגיר",
                "Sega CD": "סגה סידי",
                "Sega Master System/Mark III": "מאסטר סיסטם",
                "Sega Saturn": "סגה סאטורן",
                "Sega Mega Drive/Genesis": "מגה דרייב",
                "3DO Interactive Multiplayer": "3DO",
                "Dreamcast": "דרימקאסט",
                "Atari 8-bit": "אטארי 8-ביט",
                "Atari 2600": "אטארי 2600",
                "Arcade": "ארקייד",
                "Xbox": "אקסבוקס",
                "Xbox Series X|S": "סירייס S|X",
                "Xbox 360": "אקסבוקס 360",
                "Xbox One": "אקסבוקס וואן",
                "Nintendo Switch": "סוויץ'",
                "Nintendo 64": "נינטנדו 64",
                "Nintendo Entertainment System": "NES",
                "Super Nintendo Entertainment System": "SNES",
                "Nintendo 3DS": "3DS",
                "Nintendo DS": "DS",
                "Nintendo GameCube": "גיימקיוב",
                "Wii": "ווי",
                "Wii U": "ווי יו",
                "Super Famicom": "סופר פאמיקום",
                "Game Boy": "גיימבוי",
                "Game Boy Color": "גיימבוי קולור",
                "Game Boy Advance": "GBA",
                "iOS": "אייפון",
                "Android": "אנדרואיד",
                "Google Stadia": "", "Linux": "", "Mac": "",
                "Legacy Mobile Device": "",
            }
        except Exception as e:
            raise Exception("Could not create a GameInfo object") from e

    def __str__(self) -> str:
        """
        A string representation of a GameInfo instance. This is the text to be tweeted.
        """
        try:
            devs: typing.List[str] = self.data_dict.get("developers", None)
            genres: typing.List[str] = self.data_dict.get("genres", None)
            wiki_url: str = self.data_dict.get("wiki_url", None)
            test_img: str = self.data_dict.get("cover", None)
            pub: str = self.data_dict.get("publisher", None)
            devs_text: str = f"""מפתחת: {", ".join(devs[:2])}""" if devs else ""
            pub_text: str = f"""מפיצה: {pub}""" if pub else ""
            heb_genres: typing.List[str] = [
                self.heb_game_genres_themes.get(g, "") for g in genres[:3]]
            heb_genres = [g for g in heb_genres if g]
            intro_text: str = "משחק ה{}".format(
                "/".join(heb_genres)) if heb_genres else "המשחק"
            wiki_text: str = f"""בוויקיפדיה: {wiki_url}""" + \
                "\n" if wiki_url else "\n"
            release_text: str = "".join([
                                " {} חוגג {} שנים לשחרורו!".format(
                                    self.data_dict["name"], datetime.now().year - self.data_dict["year"]),
                " הוא יצא היום בשנת {}.".format(
                                    self.data_dict["year"])])
            heb_platforms: typing.List[str] = [self.heb_platforms.get(
                p, p) for p in self.data_dict["platforms"]]
            info_text: str = "\n".join([
                devs_text,
                pub_text,
                "פלטפורמות: {}".format(
                    ", ".join(sorted([p for p in heb_platforms if p])) if len(heb_platforms) < 8 else "יותר מדי")
            ]).replace("\n"*2, "\n")
            tweet: str = intro_text + release_text + "\n"*2 + info_text + "\n"
            if len(tweet) + GameInfo.MAX_TWITTER_URL_LENGTH <= 180:
                tweet += wiki_text
            return tweet
        except Exception as e:
            raise Exception(
                "Could not create a string repr. of a GameInfo") from e

    @staticmethod
    def _is_remake(raw_game_info_data_dict: typing.Dict[str, typing.Any]) -> bool:
        """
        Checks if the game is a remake of another game using the raw dict.
        """
        if (cat := raw_game_info_data_dict.get("category", None)):
            if cat == 8:
                return True
        return False

    @staticmethod
    def _is_parent(raw_game_info_data_dict: typing.Dict[str, typing.Any]) -> bool:
        """
        Checks if the game is a first-release or a DLC / Expansion Pack using the raw dict.
        """
        if (parent_game := raw_game_info_data_dict.get("parent_game", None)) and (id := raw_game_info_data_dict.get("id", None)):
            if parent_game != id:
                return False
        return True

    @staticmethod
    def _is_sports(raw_game_info_data_dict: typing.Dict[str, typing.Any]) -> bool:
        """
        Checks if the game is a sports title using the raw dict.
        """
        try:
            if (genres := raw_game_info_data_dict.get("genres", None)):
                for g in genres:
                    if g.get("name", "") == "Sport":
                        return True
            return False
        except (IndexError, KeyError):
            raise

    def _get_image_dicts_from_data_dict(self, key: str, number_of_imgs: int) -> typing.List[typing.Dict[str, str]]:
        """
        Gets the first X single-image dictionaries with the given name from the data dict. 
        """
        if dictlist := self.data_dict.get(key, None):
            # grab first screenshot or artwork dict.
            return dictlist[:number_of_imgs]
        return []

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
            screens_dicts: typing.List[typing.Dict[str, str]] = [
                d for d in self._get_image_dicts_from_data_dict(key="screenshots", number_of_imgs=2)]
            art_dicts: typing.List[typing.Dict[str, str]] = [
                d for d in self._get_image_dicts_from_data_dict(key="artworks", number_of_imgs=2)]
            all_image_dicts: typing.List[typing.Dict[str, str]] = [
                self.data_dict.get("cover")] + screens_dicts + art_dicts  # type: ignore
            return [_get_image_url_from_image_dict(d) for d in all_image_dicts if d]
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
    def _clean_genres_list(genres: typing.List[str], themes: typing.List[str]) -> typing.List[str]:
        """
        IGDB genres don't always reflect the game's nature. This function cleans the genre list
        and specifically handles special cases.
        """
        try:
            if genres:  # add genres using the themes list, if there's room
                for t in ("Action", "Horror", "Stealth"):
                    if len(genres) < 3:
                        if t in themes:
                            genres.append(t)
                    else:
                        break

            # specific genre combinations and their "genres" list to be returned
            special_cases: typing.Dict[typing.Tuple, typing.List[str]] = {
                ("Racing", "Arcade"): ["Racing", "Arcade"],
                ("Platform", "Hack and slash/Beat 'em up", "Action"): ["Hack and slash/Beat 'em up", "Platform"],
                ("Strategy", "Hack and slash/Beat 'em up", "Adventure"): ["Hack and slash/Beat 'em up"],
                ("Shooter", "Hack and slash/Beat 'em up", "Action"): ["Shooter", "Action", "Hack and slash/Beat 'em up"],
                ("Fighting", "Action"): ["Fighting"],
                ("Puzzle", "Action"): ["Action", "Puzzle"],
                ("Puzzle", "Shooter"): ["Shooter", "Puzzle"],
            }

            for k in special_cases.keys():
                if all(g in genres for g in k):
                    genres = special_cases[k]

            return genres
        except (IndexError, KeyError, ValueError) as e:
            raise ValueError("Could not clean the genres list.") from e

    @staticmethod
    def _clean_data_dict(game_info_data_dict: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        Cleans and parses the given game data dict.
        """
        try:
            ret: typing.Dict[str, typing.Any] = {"developers": []}

            for key in ("name", "summary", "year", "cover", "artworks", "screenshots"):
                if val := game_info_data_dict.get(key, None):
                    ret[key] = val
            for key in ("platforms", "themes", "genres"):
                if val_dict := game_info_data_dict.get(key, None):
                    ret[key] = [v.get("name", "") for v in val_dict]

            ret["genres"] = GameInfo._clean_genres_list(
                genres=ret.get("genres", []), themes=ret.get("themes", []))

            if companies := game_info_data_dict.get("involved_companies", None):
                for d in companies:
                    if d["developer"]:
                        ret["developers"].append(d["company"]["name"])
                    if d["publisher"]:
                        ret["publisher"] = d["company"]["name"]

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
