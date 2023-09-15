import datetime
import logging
import re

import pandas as pd
import requests

from models import StormForecast, StormForecasts

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# # create console handler and set level to debug
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# # create formatter
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# # add formatter to ch
# ch.setFormatter(formatter)
# # add ch to logger
# logger.addHandler(ch)


hafs_endpoint = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/hafs/prod"


HOURS = ["00", "06", "12", "18"]

MODELS = ["hfsa", "hfsb"]


def get_recent_for_dates(model: str, dates: list[datetime.date]) -> StormForecasts:
    model_stormforecasts = StormForecasts()
    for mydate in sorted(dates, reverse=True):
        date_str = mydate.strftime("%Y%m%d")
        for hour in sorted(HOURS, reverse=True):
            is_future_time = (
                datetime.datetime.combine(mydate, datetime.time(int(hour)))
                > datetime.datetime.utcnow()
            )
            if is_future_time:
                continue
            date_str = mydate.strftime("%Y%m%d")
            logger.info(f"{model=}, {date_str=}, {hour=}")
            try:
                model_stormforecasts = get_forecast(model, date_str, hour)
            except Exception as e:
                logger.exception(f"caught error: {e}")
                continue
            if len(model_stormforecasts.forecasts) == 0:
                logger.info(f"{model=}, {date_str=}, {hour=} no storms yet")
                continue
            return model_stormforecasts
    return model_stormforecasts


def get_most_recent_forecasts() -> StormForecasts:
    today = datetime.datetime.utcnow().date()
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).date()
    dates = [today, yesterday]
    forecasts = []
    for model in MODELS:
        model_storms = get_recent_for_dates(model, dates)
        forecasts.extend(model_storms.forecasts)
    storms = StormForecasts(forecasts=forecasts)
    return storms


def parse_response_to_df(response: requests.Response) -> pd.DataFrame:
    short_stats = response.content.decode("utf-8")
    rows = []
    for line in short_stats.splitlines():
        fhour = line[0:11]
        long = line[12:26]
        lat = line[27:39]
        press = line[40:65]
        wind = line[66:]
        keys = [
            fhour,
            long,
            lat,
            press,
            wind,
        ]
        mydict = {}
        for chunk in keys:
            key = chunk.split(":")[0].strip().lower().replace(" ", "_")
            val = float(chunk.split(":")[1].strip())
            mydict[key] = val
        rows.append(mydict)
    stats_df = pd.DataFrame(rows)
    stats_df = stats_df.rename(
        columns={"hour": "fhr", "long": "lon", "max_surf_wind_(knots)": "wind_kt"}
    )
    return stats_df


def get_forecast(model: str, date_str: str, hour: str) -> StormForecasts:
    response = requests.get(hafs_endpoint + f"/{model}.{date_str}/{hour}/")
    all_urls = re.findall('\<a href="([^"]+)"\>', str(response.content))
    short_urls = [x for x in all_urls if "stats.short" in x]

    if len(short_urls) == 0:
        return StormForecasts()

    logger.info(f"{model=} {date_str=} {hour=} Found storms: {len(short_urls)}")
    forecasts = []
    for short_url in short_urls:
        response = requests.get(
            hafs_endpoint + f"/{model}.{date_str}/{hour}/{short_url}"
        )
        storm_id = short_url.split(".")[0]
        stats_df = parse_response_to_df(response)
        hafs_forecast = StormForecast(
            storm_id=storm_id,
            dataframe=stats_df,
            forecast_date=datetime.datetime.strptime(date_str, "%Y%m%d").date(),
            forecast_hour=int(hour),
            model_id=model,
        )
        forecasts.append(hafs_forecast)
    return StormForecasts(forecasts=forecasts)
