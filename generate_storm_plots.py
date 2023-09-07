import datetime
import pathlib

from tropycal import realtime

from config.config import IMAGES_DIR
from plot import plot_storm


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
                print(f"Get forecast caught exception {e}")
                continue

            pathlib.Path(f"{my_dir}/{storm_id}").mkdir(parents=True, exist_ok=True)
            try:
                storm.plot_forecast_realtime(
                    save_path=f"{my_dir}/{storm_id}/{data_source}_tropycal_forecast_realtime.jpg"
                )
                fig = plot_storm(storm, storm_forecast)
                fig.savefig(f"{my_dir}/{storm_id}/{data_source}_myimage.jpg")
            except Exception as e:
                print(f"JPG Caught exception {e}")


if __name__ == "__main__":
    main()
