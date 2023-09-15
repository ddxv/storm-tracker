import argparse
import datetime
import logging
import pathlib
from typing import Any, Callable

from tropycal import realtime

import hafs
from config.config import IMAGES_DIR
from models import StormForecasts
from plot import plot_compare_forecasts, plot_storm, plot_my_spaghetti

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
    parser.add_argument(
        "-p",
        "--plot",
        help="Which plot to generate, default all",
        choices=["all"] + list(PLOT_FUNCTIONS.keys()),
        default="all",
    )
    parser.add_argument(
        "-s",
        "--storm-id",
        help="Which currently active storm to plot",
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
        except Exception:
            logger.error("Failed")
            data = download_current_data(data_type)
            # Pickling the object to a file
            with open(f"data_{data_type}.pkl", "wb") as file_w:
                pickle.dump(data, file_w)

    return data


def plot_tropycal(
    my_dir: str, storm_id: str, tropycal_hist: realtime.storm, **kwargs: Any
) -> None:
    tropycal_hist.plot_forecast_realtime(
        save_path=f"{my_dir}/{storm_id}/ucar_tropycal_forecast_realtime.jpg"
    )


def main(args: argparse.Namespace) -> None:
    logger.info(f"main start {args=}")
    only_plot_storm = args.storm_id
    realtime_obj: realtime.Realtime = get_data("ucar")
    active_storms = realtime_obj.list_active_storms()
    if only_plot_storm:
        active_storms = [x for x in active_storms if x == only_plot_storm]
    logger.info(f"Found {active_storms=}")

    if len(active_storms) == 0:
        logger.warning("No active storms")
        exit()

    hafs_storms: realtime.Realtime | StormForecasts = get_data("hafs")

    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    my_dir = f"{IMAGES_DIR}/{date_str}"
    for storm_id in active_storms:
        logger.info(f"{storm_id} start")
        try:
            logger.info(f"{storm_id} get_storm_hist")
            tropycal_hist = realtime_obj.get_storm(storm_id)
            logger.info(f"{storm_id} get_storm_forecast")
            tropycal_forecast = tropycal_hist.get_forecast_realtime(
                ssl_certificate=False
            )
            logger.info(f"{storm_id} get_storm_forecasts (all)")
            tropycal_forecasts = tropycal_hist.get_operational_forecasts()
        except Exception:
            logger.warning(f"{storm_id} Tropycal get storm forecast caught exception")
            continue

        pathlib.Path(f"{my_dir}/{storm_id}").mkdir(parents=True, exist_ok=True)

        if PLOTS == "all":
            for func in PLOT_FUNCTIONS.values():
                logger.info(f"{storm_id} plot {func.__name__}")
                try:
                    func(
                        my_dir=my_dir,
                        storm_id=storm_id,
                        tropycal_hist=tropycal_hist,
                        tropycal_forecasts=tropycal_forecasts,
                        tropycal_forecast=tropycal_forecast,
                        hafs_storms=hafs_storms,
                    )
                except Exception:
                    logger.exception(
                        f"{storm_id} plot {func.__name__} failed with exception"
                    )
        else:
            PLOT_FUNCTIONS[PLOTS](
                my_dir=my_dir,
                storm_id=storm_id,
                tropycal_hist=tropycal_hist,
                tropycal_forecast=tropycal_forecast,
                tropycal_forecasts=tropycal_forecasts,
                hafs_storms=hafs_storms,
            )
        logger.info(f"{storm_id} done")
    logger.info("main done")


PLOT_FUNCTIONS: dict[str, Callable] = {
    "tropycal": plot_tropycal,
    "regular": plot_storm,
    "compare": plot_compare_forecasts,
    "spaghetti": plot_my_spaghetti,
}


if __name__ == "__main__":
    args = manage_cli_args()
    TEST = args.test
    PLOTS = args.plot if TEST else "all"
    main(args)
