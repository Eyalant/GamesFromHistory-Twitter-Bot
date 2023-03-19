import logging
from os import environ

def verify_env_vars():
    if not all([environ.get("IGDB_CLIENT_ID"),
                environ.get("IGDB_CLIENT_SECRET"),
                environ.get("REDIS_URL"),
                environ.get("TWITTER_DEV_API_KEY"),
                environ.get("TWITTER_DEV_API_SECRET"),
                environ.get("TWITTER_DEV_USER_ID"),
                environ.get("TWITTER_USER_ACCESS_TOKEN"),
                environ.get("TWITTER_USER_ACCESS_TOKEN_SECRET")]):
        logging.critical(
            "One or more essential env. variable is nonexistent or empty. Exiting.")
        exit(1)

if __name__ == "__main__":
    pass