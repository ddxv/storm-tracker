import pathlib
from datetime import datetime

from tropycal import realtime


def main() -> None:
    realtime_obj = realtime.Realtime(jtwc=True, jtwc_source="ucar")

    active_storms = realtime_obj.list_active_storms()

    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    print(f"Found {active_storms=}")

    my_dir = f"{MODULE_DIR}/exported-images/{date_str}/tropycal_forecast_realtime"

    for storm_id in active_storms:
        print(f"start {storm_id}")
        storm = realtime_obj.get_storm(storm_id)
        pathlib.Path(f"{my_dir}/").mkdir(parents=True, exist_ok=True)
        try:
            storm.plot_forecast_realtime(save_path=f"{my_dir}/storm_id_{storm_id}.jpg")
        except Exception as e:
            print(f"JPG Caught exception {e}")


MODULE_DIR = pathlib.Path(__file__).resolve().parent


if __name__ == "__main__":
    main()
