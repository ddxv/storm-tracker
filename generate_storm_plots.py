import argparse
import datetime
import logging
import pathlib

from tropycal import realtime

import hafs
from config.config import IMAGES_DIR
from models import StormForecasts
from plot import plot_compare_forecasts, plot_storm

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


def manage_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--test",
        help="If included try using previously pickled data",
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


def plot_images(
    active_storms: list[str],
    realtime_obj: realtime.Realtime,
    hafs_storms: StormForecasts,
) -> None:
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    my_dir = f"{IMAGES_DIR}/{date_str}"
    for storm_id in active_storms:
        logging.info(f"{storm_id} start")

        tropycal_hist = realtime_obj.get_storm(storm_id)
        logging.info(f"{storm_id} pulled tropycal hist")
        try:
            tropycal_forecast = tropycal_hist.get_forecast_realtime(
                ssl_certificate=False
            )
        except Exception as e:
            logging.warning(f"Tropycal get storm forecast caught exception {e}")
            continue

        pathlib.Path(f"{my_dir}/{storm_id}").mkdir(parents=True, exist_ok=True)
        logging.info(f"{storm_id} plot tropycal")
        try:
            tropycal_hist.plot_forecast_realtime(
                save_path=f"{my_dir}/{storm_id}/ucar_tropycal_forecast_realtime.jpg"
            )
        except Exception as e:
            logging.exception(f"Plot Tropycal JPG get forecast caught exception {e}")
        logging.info(f"{storm_id} plot local plot")
        try:
            fig = plot_storm(tropycal_hist, tropycal_forecast)
            fig.savefig(f"{my_dir}/{storm_id}/ucar_myimage.jpg")
        except Exception as e:
            logging.exception(f"Plot MyImage JPG Caught exception {e}")
        logging.info(f"{storm_id} plot local compare")
        try:
            tropycal_forecasts = tropycal_hist.get_operational_forecasts()

            logging.info(f"{storm_id} plot local pulled forecasts")
            fig = plot_compare_forecasts(
                storm_id=storm_id,
                tropycal_hist=tropycal_hist,
                tropycal_forecasts=tropycal_forecasts,
                hafs_storms=hafs_storms,
            )

            fig.savefig(f"{my_dir}/{storm_id}/compare.jpg")
        except Exception as e:
            logging.exception(f"Plot Compare JPG Caught exception {e}")
        logging.info(f"{storm_id} done")


def main() -> None:
    realtime_obj: realtime.Realtime = get_data("ucar")
    active_storms = realtime_obj.list_active_storms()
    logging.info(f"Found {active_storms=}")

    hafs_storms: realtime.Realtime | StormForecasts = get_data("hafs")

    plot_images(
        active_storms=active_storms,
        realtime_obj=realtime_obj,
        hafs_storms=hafs_storms,
    )


if __name__ == "__main__":
    args = manage_cli_args()
    TEST = args.test
    if TEST:
        PLOTS = args.plot
    else:
        PLOTS = "all"
    main()
