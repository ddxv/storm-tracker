import datetime
import pathlib

import pandas as pd
from tropycal import realtime

from config.config import IMAGES_DIR
from plot import plot_all_forecasts, plot_storm


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
    jtwc_data_sources = ["ucar"]

    for data_source in jtwc_data_sources:
        realtime_obj = realtime.Realtime(jtwc=True, jtwc_source=data_source)

        active_storms = realtime_obj.list_active_storms()

        date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

        print(f"Found {active_storms=}")

        my_dir = f"{IMAGES_DIR}/{date_str}"

        for storm_id in active_storms:
            print(f"start {storm_id}")
            storm = realtime_obj.get_storm(storm_id)
            try:
                storm_forecast = storm.get_forecast_realtime(ssl_certificate=False)
            except Exception as e:
                print(f"Tropycal get storm forecast caught exception {e}")
                continue

            pathlib.Path(f"{my_dir}/{storm_id}").mkdir(parents=True, exist_ok=True)
            try:
                storm.plot_forecast_realtime(
                    save_path=f"{my_dir}/{storm_id}/{data_source}_tropycal_forecast_realtime.jpg"
                )
            except Exception as e:
                print(f"Plot Tropycal JPG get forecast caught exception {e}")
            storm_df = get_df(storm)
            try:
                fig = plot_storm(storm_df, storm_forecast)
                fig.savefig(f"{my_dir}/{storm_id}/{data_source}_myimage.jpg")
            except Exception as e:
                print(f"Plot MyImage JPG Caught exception {e}")
            try:
                forecasts = storm.get_operational_forecasts()
                fig = plot_all_forecasts(storm_df, forecasts)
                fig.savefig(f"{my_dir}/{storm_id}/compare.jpg")
            except Exception as e:
                print(f"Plot Compare JPG Caught exception {e}")


if __name__ == "__main__":
    main()
