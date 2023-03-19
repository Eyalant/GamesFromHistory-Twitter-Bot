import src.conn_redis as conn_redis
import src.conn_twitter as conn_twitter
import src.conn_igdb as conn_igdb
import src.verify_env_vars as v_env
from src.game_info import GameInfo
from os import environ
from dotenv import load_dotenv
import typing
import logging
import sys

def run_hourly() -> None:
    """
    Run this via cron/eventtrigger on an hourly/bi-hourly basis. This fetches a single game
    data dict, makes a GameInfo object from it, then tweets it.
    """
    try:
        rc = conn_redis.connect(redis_url=str(environ.get("REDIS_URL")))
        game_data_dict: typing.Optional[typing.Dict[str, typing.Any]] = conn_redis.getdel_single_game_data_dict(redis_client=rc)
        if not game_data_dict:
            logging.info("There was no game to fetch from redis. Exiting")
            exit(0)
        igdb_client: conn_igdb.IGDB = conn_igdb.IGDB(client_id=str(environ.get("IGDB_CLIENT_ID")),
                                        client_secret=str(environ.get("IGDB_CLIENT_SECRET")),
                                        )
        twitter: conn_twitter.Twitter = conn_twitter.Twitter()
        game_info: GameInfo = GameInfo(game_data_dict, do_clean_dict=False) # was already cleaned before storing to Redis
        logging.info("Pulled game {} from Redis".format(game_info.data_dict["name"]))
        media_ids: typing.List[str] = twitter.upload_images(image_binaries=game_info.images)
        payload: typing.Dict[str, str] = twitter.make_tweet(tweet_text=str(game_info), media_ids=media_ids[:3])
        logging.info("Trying to tweet...")
        resp: typing.Dict[str, typing.Any] = twitter.tweet(payload)
        logging.info("Tweet response: " + str(resp))
    except Exception as e:
        logging.critical(
            "Completed an hourly / bi-hourly script: exiting following exception. Details to follow\n" + str(e), exc_info=True)
        exit(1)
    logging.info("Completed an hourly / bi-hourly script")

def handler(event, context):
    if len(logging.getLogger().handlers) > 0:   # running on AWS Lambda
        logging.getLogger().setLevel(logging.INFO)
    else:   # debug local run
        logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s: %(message)s",
                            datefmt="%d.%m.%Y %H:%M:%S",
                            handlers=[logging.StreamHandler(sys.stdout),
                                      logging.FileHandler("run_hourly.log", mode="w")])
    logging.info("Started an hourly/bi-hourly script")
    load_dotenv()
    v_env.verify_env_vars()
    run_hourly()

if __name__ == "__main__":
    handler(None, None)