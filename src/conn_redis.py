import redis
import typing
import json


def connect(redis_url: str) -> redis.Redis:
    """
    Connect to a redis instance.
    """
    try:
        return redis.Redis.from_url(redis_url, decode_responses=True)
    except Exception as e:
        raise ConnectionError("Could not connect to redis") from e


def store_raw_game_data_dicts(redis_client: redis.Redis, data_dicts: typing.List[typing.Dict[str, typing.Any]]):
    """
    Set the given data dicts as redis keys.
    """
    try:
        pl = redis_client.pipeline()
        for dd in data_dicts:
            pl.set(name=dd["name"], value=json.dumps(dd))
        return pl.execute()
    except Exception as e:
        raise Exception("Failed to store game info dicts in redis") from e


def getdel_single_game_data_dict(redis_client: redis.Redis) -> typing.Optional[typing.Dict[str, typing.Any]]:
    """
    Get a random game data dict from redis, then delete the key.
    """
    try:
        key = redis_client.randomkey()
        if key:
            return json.loads(str(redis_client.getdel(name=key)))
        return None
    except Exception as e:
        raise ConnectionError("Could not getdel a single game info dict from redis") from e


if __name__ == "__main__":
    pass