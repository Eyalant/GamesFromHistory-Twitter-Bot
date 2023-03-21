import src.conn_redis as conn_redis
import src.conn_igdb as conn_igdb
import src.verify_env_vars as v_env
import typing
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from os import environ
from src.game_info import GameInfo


def run_daily() -> None:
    """
    Run this using cron/eventtrigger on a daily basis. This queries the IGDB API
    for all games released on this day from 1970 to (current year - 3), checks
    if the results are valid, then stores the game data dicts in redis. The game data dicts
    will be fetched later, one-by-one, using run_hourly().
    """
    todays_game_data_dicts: typing.List[typing.Any] = []
    try:
        igdb_client: conn_igdb.IGDB = conn_igdb.IGDB(client_id=environ.get("IGDB_CLIENT_ID"),
                                                     client_secret=environ.get("IGDB_CLIENT_SECRET"),)
        igdb_dates: typing.List[conn_igdb.IGDB_Date] = _prepare_dates_list()
        for d in igdb_dates:
            # logging.info(repr(d))
            game_data_dicts_in_year: typing.List[typing.Dict[str, typing.Any]] = igdb_client.get_games_endpoint(
                raw_body=_prepare_request_body(d))
            for data_dict in game_data_dicts_in_year:
                try:
                    clean_dict = GameInfo.clean_data_dict(data_dict)
                    clean_dict["year"] = d.lower_bound["dt"].year
                    todays_game_data_dicts.append(clean_dict)
                except Exception as e:
                    logging.exception(e)
                    continue
        rc = conn_redis.connect(
            redis_url=environ.get("REDIS_URL"))
        rc.flushdb()
        conn_redis.store_game_data_dicts(
            redis_client=rc, data_dicts=todays_game_data_dicts)
        logging.info("Stored games {} to Redis".format([g["name"] for g in todays_game_data_dicts]))
    except Exception as e:
        logging.critical(
            "Completed a daily script: exiting following exception. Details to follow\n" + str(e), exc_info=True)
        exit(1)
    logging.info("Completed a daily script")

def _prepare_dates_list(start_year: int = 1970) -> typing.List[conn_igdb.IGDB_Date]:
    """
    Returns IGDB game release dates from 1970 to (current year - 3).
    """
    try:
        dt_now: datetime = datetime.now(tz=timezone.utc)
        years_ints: typing.List[int] = list(range(start_year, dt_now.year - 2))
        dates_lower_bound: typing.List[datetime] = [
            datetime(year=y, month=dt_now.month, day=dt_now.day, tzinfo=timezone.utc) for y in years_ints]
        dates_upper_bound: typing.List[datetime] = [
            dt + timedelta(hours=23) for dt in dates_lower_bound]
        dates: typing.List[conn_igdb.IGDB_Date] = [conn_igdb.IGDB_Date(k, v)
                                                   for k, v in zip(dates_lower_bound, dates_upper_bound)]
        return dates
    except Exception as e:
        raise ValueError(
            "Could not prepare dates list for querying the IGDB games endpoint") from e


def _prepare_request_body(d: conn_igdb.IGDB_Date) -> str:
    """
    Returns the raw body of the request that'll be sent to IGDB's games endpoint.
    """
    try:
        return "fields name, parent_game, total_rating_count, total_rating, platforms.name,"\
            "summary, cover.url, involved_companies.company.name, involved_companies.developer,"\
            "involved_companies.publisher, genres.name, websites.category, websites.url, artworks.url,"\
            "screenshots.url, themes.name;"\
            f"where (first_release_date >= {d.lower_bound['ts']})"\
            f"& (first_release_date <= {d.upper_bound['ts']})"\
            "& (themes != (42))"\
            "& ((total_rating >= 78 & total_rating_count >= 15) | (total_rating_count >= 100));"
    except Exception as e:
        raise ValueError(
            "Had a problem preparing the raw request body for the IGDB games endpoint") from e

def handler(event, context):
    if len(logging.getLogger().handlers) > 0:   # running on AWS Lambda
        logging.getLogger().setLevel(logging.INFO)
    else:   # debug local run
        logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s: %(message)s",
                            datefmt="%d.%m.%Y %H:%M:%S",
                            handlers=[logging.StreamHandler(sys.stdout),
                                      logging.FileHandler("run_daily.log", mode="w")])
    logging.info("Started a daily script")
    load_dotenv()
    v_env.verify_env_vars()
    run_daily()

if __name__ == "__main__":
    handler(None, None)