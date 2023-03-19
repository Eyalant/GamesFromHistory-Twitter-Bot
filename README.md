[This is a twitter bot](https://twitter.com/DailyGameHeb)  which publishes a bit of info about major video games released on this day in history.

No API wrappers were used here; I felt they were too much of a black box and opted for direct HTTP requests. This project leverages the *Twitter* v1 and v2 APIs, *[IGDB](https://igdb.com)*'s  API v4 and *Redis*. 

## How it works

The *run_daily* script runs one per day, and triggers multiple requests to fetch the list of raw game data from IGDB. These are parsed and stored in Redis. 

Later, the *run_hourly* script runs multiple days a day and retrieves a single game's info from Redis. It then downloads it's attached images, uploads them to Twitter, and tweets the parsed info.

I used *Render.com* for my Redis instance and *AWS Lambda* and *EventTrigger* to trigger the scripts.