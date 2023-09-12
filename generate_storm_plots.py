import argparse
import datetime
import logging
import pathlib

import pandas as pd
from tropycal import realtime

import hafs
from config.config import IMAGES_DIR
from models import StormForecast, StormForecasts
from plot import plot_all_forecasts, plot_storm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def manage_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--test",
        help="If included only run a few records",
        default=False,
        action="store_true",
    )
    args, leftovers = parser.parse_known_args()
    return args


def get_data(
    data_type: str,
) -> realtime.Realtime | StormForecasts:
    import pickle

    def download_current_data(
        data_type: str,
    ) -> realtime.Realtime | StormForecasts:
        if data_type == "ucar":
            data = realtime.Realtime(jtwc=True, jtwc_source=data_type)
        if data_type == "hafs":
            data = hafs.get_most_recent_forecasts()
        return data

    if not TEST:
        data = download_current_data(data_type)
    else:
        try:
            # Unpickling the object from a file
            with open(f"data_{data_type}.pkl", "rb") as file_r:
                data = pickle.load(file_r)
        except Exception as e:
            logging.error(f"Failed {e}")
            data = download_current_data(data_type)
            # Pickling the object to a file
            with open(f"data_{data_type}.pkl", "wb") as file_w:
                pickle.dump(data, file_w)

    return data


def get_df(storm: realtime.storm) -> pd.DataFrame:
    storm_df = storm.to_dataframe()
    by_hour = 12
    days_ago = 5
    past_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)
    storm_df["should_plot_step"] = (storm_df["time"] >= past_date) & (
        storm_df["time"].dt.hour / by_hour == 0
    )
    storm_df["name"] = storm["name"]
    return storm_df


def main() -> None:
    realtime_obj: realtime.Realtime = get_data("ucar")

    hafs_storms: realtime.Realtime | StormForecasts = get_data("hafs")

    active_storms = realtime_obj.list_active_storms()

    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    logging.info(f"Found {active_storms=}")
    my_dir = f"{IMAGES_DIR}/{date_str}"
    for storm_id in active_storms:
        logging.info(f"start {storm_id}")

        tropycal_hist = realtime_obj.get_storm(storm_id)
        try:
            tropycal_forecast = tropycal_hist.get_forecast_realtime(
                ssl_certificate=False
            )
        except Exception as e:
            logging.warning(f"Tropycal get storm forecast caught exception {e}")
            continue

        pathlib.Path(f"{my_dir}/{storm_id}").mkdir(parents=True, exist_ok=True)
        try:
            tropycal_hist.plot_forecast_realtime(
                save_path=f"{my_dir}/{storm_id}/ucar_tropycal_forecast_realtime.jpg"
            )
        except Exception as e:
            logging.exception(f"Plot Tropycal JPG get forecast caught exception {e}")
        tropycal_storm_df = get_df(tropycal_hist)
        try:
            fig = plot_storm(tropycal_storm_df, tropycal_forecast)
            fig.savefig(f"{my_dir}/{storm_id}/ucar_myimage.jpg")
        except Exception as e:
            logging.exception(f"Plot MyImage JPG Caught exception {e}")
        try:
            lower_storm_id = storm_id[2:4] + storm_id[1:2].lower()
            hafs_forecasts = [
                x for x in hafs_storms.forecasts if x["storm_id"] == lower_storm_id
            ]
            tropycal_forecasts = tropycal_hist.get_operational_forecasts()

            tropycal_most_recent_forecasts = []
            for key in tropycal_forecasts.keys():
                my_dict = {}
                most_recent_time = max(tropycal_forecasts[key].keys())
                my_date = datetime.datetime.strptime(most_recent_time[0:8], "%Y%m%d")
                my_hour = most_recent_time[-2:]
                my_dict["fhr"] = tropycal_forecasts[key][most_recent_time]["fhr"]
                my_dict["lat"] = tropycal_forecasts[key][most_recent_time]["lat"]
                my_dict["lon"] = tropycal_forecasts[key][most_recent_time]["lon"]
                my_dict["wind_kt"] = tropycal_forecasts[key][most_recent_time]["vmax"]
                my_forecast = StormForecast(
                    storm_id=lower_storm_id,
                    model_id=key,
                    forecast_date=my_date,
                    forecast_hour=my_hour,
                    dataframe=pd.DataFrame(my_dict),
                )
                tropycal_most_recent_forecasts.append(my_forecast)

            my_storm_forecasts = StormForecasts()
            my_storm_forecasts.forecasts.extend(hafs_forecasts)
            my_storm_forecasts.forecasts.extend(tropycal_most_recent_forecasts)

            fig = plot_all_forecasts(
                tropycal_storm_df=tropycal_storm_df,
                my_storm_forecasts=my_storm_forecasts,
            )

            fig.savefig(f"{my_dir}/{storm_id}/compare.jpg")
        except Exception as e:
            logging.exception(f"Plot Compare JPG Caught exception {e}")


if __name__ == "__main__":
    args = manage_cli_args()
    TEST = args.test
    main()
