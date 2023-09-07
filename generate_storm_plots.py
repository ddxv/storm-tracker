import datetime
import pathlib

from tropycal import realtime

from config.config import IMAGES_DIR
from plot import plot_storm


def main() -> None:
    realtime_obj = realtime.Realtime(jtwc=True, jtwc_source="ucar")

    active_storms = realtime_obj.list_active_storms()

    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    print(f"Found {active_storms=}")

    my_dir = f"{IMAGES_DIR}/{date_str}"

    for storm_id in active_storms:
        print(f"start {storm_id}")
        storm = realtime_obj.get_storm(storm_id)
        storm_forecast = storm.get_forecast_realtime(ssl_certificate=False)
        storm_forecast["already_forcasted"] = [
            (datetime.timedelta(hours=x) + storm_forecast["init"]) <= storm.time.max()
            for x in storm_forecast["fhr"]
        ]
        pathlib.Path(f"{my_dir}/{storm_id}").mkdir(parents=True, exist_ok=True)
        try:
            storm.plot_forecast_realtime(
                save_path=f"{my_dir}/{storm_id}/tropycal_forecast_realtime.jpg"
            )
            fig = plot_storm(storm, storm_forecast)
            fig.savefig(f"{my_dir}/{storm_id}/my_plot.jpg")
        except Exception as e:
            print(f"JPG Caught exception {e}")


if __name__ == "__main__":
    main()
