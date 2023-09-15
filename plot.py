import datetime
from typing import Any

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.mpl.ticker import LatitudeFormatter, LatitudeLocator, LongitudeFormatter
from matplotlib.pyplot import Axes
from tropycal import realtime

from models import StormForecast, StormForecasts


def get_my_recent_forecasts(
    storm_id: str, tropycal_forecasts: realtime.Realtime, hafs_storms: StormForecasts
) -> StormForecasts:
    my_storm_forecasts = StormForecasts()

    lower_storm_id = storm_id[2:4] + storm_id[1:2].lower()
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

    hafs_forecasts = [
        x for x in hafs_storms.forecasts if x["storm_id"] == lower_storm_id
    ]
    my_storm_forecasts.forecasts.extend(hafs_forecasts)
    my_storm_forecasts.forecasts.extend(tropycal_most_recent_forecasts)
    return my_storm_forecasts


def tropycal_to_df(storm: realtime.storm) -> pd.DataFrame:
    storm_df = storm.to_dataframe()
    by_hour = 12
    days_ago = 5
    past_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)
    storm_df["should_plot_step"] = (storm_df["time"] >= past_date) & (
        storm_df["time"].dt.hour / by_hour == 0
    )
    storm_df["name"] = storm["name"]
    return storm_df


def get_colors_sshws(wind_speed: int) -> str:
    r"""
    Retrieve the default colors for the Saffir-Simpson Hurricane Wind Scale (SSHWS).

    Parameters
    ----------
    wind_speed : int or list
        Sustained wind speed in knots.

    Returns
    -------
    str
        Hex string for the corresponding color.
    """

    # # If category string passed, convert to wind
    # if isinstance(wind_speed, str):
    #     wind_speed = category_label_to_wind(wind_speed)

    # Return default SSHWS category color scale
    if wind_speed < 5:
        return "#FFFFFF"
    elif wind_speed < 34:
        return "#8FC2F2"  # '#7DB7ED'
    elif wind_speed < 64:
        return "#3185D3"
    elif wind_speed < 83:
        return "#FFFF00"
    elif wind_speed < 96:
        return "#FF9E00"
    elif wind_speed < 113:
        return "#DD0000"
    elif wind_speed < 137:
        return "#FF00FC"
    else:
        return "#8B0088"


def get_plot_box(
    lats: list[float], lons: list[float]
) -> tuple[tuple[float, float, float, float], float, float]:
    storm_s = min(lats)
    storm_n = max(lats)
    storm_w = max(lons)
    storm_e = min(lons)
    # storm_box = (storm_w, storm_e, storm_s, storm_n)
    storm_width = abs(storm_e - storm_w)
    storm_height = abs(storm_s - storm_n)

    central_lon = (storm_w + storm_e) / 2
    central_lat = (storm_n + storm_s) / 2

    padding_vertical = storm_height / 4
    padding_horizontal = storm_width / 4

    # If same then it is a box
    plot_height = storm_height
    plot_width = storm_height * 2

    plot_n = (central_lat + plot_height / 2) + padding_vertical
    plot_s = (central_lat - plot_height / 2) - padding_vertical
    plot_e = (central_lon + plot_width / 2) + padding_horizontal
    plot_w = (central_lon - plot_width / 2) - padding_horizontal
    plot_box = (plot_w, plot_e, plot_s, plot_n)
    return plot_box, central_lat, central_lon


def add_annotation_pointers(ax: Axes, fhr: float, xy: tuple[float, float]) -> None:
    ax.annotate(
        text=str(fhr),
        xy=xy,
        xycoords="data",
        xytext=(20, 20),
        textcoords="offset points",
        fontweight="bold",
        ha="center",
        va="center",
        arrowprops=dict(
            arrowstyle="-",
            shrinkA=0,
            shrinkB=0,
            connectionstyle="arc3",
            color="k",
        ),
        transform=ccrs.PlateCarree(),
        clip_on=True,
        zorder=1,
    )


def add_background_maps(ax: Axes) -> None:
    # Plot coastlines and political boundaries
    ax.add_feature(
        cfeature.STATES.with_scale("50m"),
        linewidths=0.1,
        linestyle="solid",
        edgecolor="k",
    )
    ax.add_feature(
        cfeature.BORDERS.with_scale("50m"),
        linewidths=0.3,
        linestyle="solid",
        edgecolor="k",
    )
    ax.add_feature(
        cfeature.COASTLINE.with_scale("50m"),
        linewidths=0.3,
        linestyle="solid",
        edgecolor="k",
    )

    # Fill in continents in light gray
    ax.add_feature(
        cfeature.LAND.with_scale("50m"), facecolor=land_color, edgecolor="face"
    )
    ax.add_feature(
        cfeature.OCEAN.with_scale("50m"), facecolor=water_color, edgecolor="face"
    )


def add_grid_lines(ax: Axes) -> None:
    axes_label_style = {"size": 12, "color": "black"}
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False
    gl.left_labels = False
    gl.ylocator = LatitudeLocator()
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    gl.ylabel_style = axes_label_style
    gl.xlabel_style = axes_label_style


def plot_storm(
    tropycal_hist: realtime.storm,
    tropycal_forecast: dict,
    my_dir: str,
    storm_id: str,
    **kwargs: Any,
) -> plt.figure:
    tropycal_storm_df = tropycal_to_df(tropycal_hist)
    tropycal_forecast["already_forcasted"] = [
        (datetime.timedelta(hours=x) + tropycal_forecast["init"])
        <= tropycal_storm_df.time.max()
        for x in tropycal_forecast["fhr"]
    ]

    lons = (
        tropycal_storm_df[tropycal_storm_df["should_plot_step"]]["lon"].tolist()
        + tropycal_forecast["lon"]
    )
    lats = (
        tropycal_storm_df[tropycal_storm_df["should_plot_step"]]["lat"].tolist()
        + tropycal_forecast["lat"]
    )
    fig, ax = plot_base(lons=lons, lats=lats)

    ax.set_title(
        "DEVELOPING STORM: " + tropycal_storm_df["name"].values[0],
        loc="left",
        # fontsize=25,
        fontweight="bold",
    )
    ax.legend(handles=[td, ts, c1, c2, c3, c4, c5], prop={"size": 7.5})

    # Plot historical (already happened) Dots
    storm_line_x = []
    storm_line_y = []
    for i in range(0, len(tropycal_storm_df["lat"])):
        if not tropycal_storm_df["should_plot_step"][i]:
            continue
        ax.plot(
            tropycal_storm_df["lon"][i],
            tropycal_storm_df["lat"][i],
            transform=ccrs.PlateCarree(),
            linewidth=2,
            marker="o",
            markersize=marker_size,
            color=get_colors_sshws(np.nan_to_num(tropycal_storm_df["vmax"][i])),
            zorder=2,
        )
        storm_line_x.append(tropycal_storm_df["lon"][i])
        storm_line_y.append(tropycal_storm_df["lat"][i])

    # Plot Already happened Line
    ax.plot(
        storm_line_x,
        storm_line_y,
        transform=ccrs.PlateCarree(),
        linewidth=1,
        color="gray",
        zorder=1,
    )

    # Forecast Dots
    for i in range(0, len(tropycal_forecast["lat"])):
        if tropycal_forecast["already_forcasted"][i]:
            continue

        fhr = tropycal_forecast["fhr"][i]
        x = tropycal_forecast["lon"][i]
        y = tropycal_forecast["lat"][i]

        ax.plot(
            x,
            y,
            transform=ccrs.PlateCarree(),
            marker="o",
            color=get_colors_sshws(np.nan_to_num(tropycal_forecast["vmax"][i])),
            markersize=marker_size,
            zorder=2,
        )
        # Lables for hrs after forecast
        if not fhr % 24 == 0:
            continue
        add_annotation_pointers(ax, fhr=fhr, xy=(x, y))

    fig.tight_layout()
    ax.set_aspect("auto")

    fig.savefig(f"{my_dir}/{storm_id}/ucar_myimage.jpg")
    return fig


def plot_base(lats: list[float], lons: list[float]) -> tuple[plt.figure, Axes]:
    plot_box, central_lat, central_lon = get_plot_box(lats, lons)

    fig = plt.figure(dpi=400)

    ax = plt.axes(
        projection=ccrs.Orthographic(
            central_longitude=central_lon, central_latitude=central_lat
        )
    )

    add_background_maps(ax)

    add_grid_lines(ax)
    ax.set_extent(plot_box, crs=ccrs.PlateCarree())

    add_background_maps(ax)

    return fig, ax


def plot_my_spaghetti(
    storm_id: str,
    tropycal_forecasts: realtime.storm,
    my_dir: str,
    **kwargs: Any,
) -> plt.figure:
    mycast = tropycal_forecasts["HWRF"].copy()
    lons = []
    lats = []
    for mydt in mycast.keys():
        lons.extend(mycast[mydt]["lons"])
        lats.extend(mycast[mydt]["lat"])
    lons = list(set(lons))
    lats = list(set(lats))

    fig, ax = plot_base(lons=lons, lats=lats)

    ax.set_title(
        "STORM: " + storm_id,
        loc="left",
        # fontsize=25,
        fontweight="bold",
    )

    for mydt in mycast.keys():
        ax.plot(
            mycast[mydt]["lon"][i],
            mycast[mydt]["lat"][i],
            transform=ccrs.PlateCarree(),
            linewidth=1,
            marker="-",
            # color=get_colors_sshws(np.nan_to_num(mycast[key]["vmax"][i])),
            color="blue",
            zorder=2,
        )

    ax.legend(loc="upper right", prop={"size": 15})
    fig.tight_layout()
    ax.set_aspect("auto")
    fig.savefig(f"{my_dir}/{storm_id}/spaghet.jpg")
    return fig


def plot_compare_forecasts(
    storm_id: str,
    tropycal_hist: realtime.storm,
    hafs_storms: StormForecasts,
    tropycal_forecasts: realtime.Realtime,
    my_dir: str,
    **kwargs: Any,
) -> plt.figure:
    tropycal_storm_df = tropycal_to_df(tropycal_hist)
    my_storm_forecasts = get_my_recent_forecasts(
        storm_id, tropycal_forecasts=tropycal_forecasts, hafs_storms=hafs_storms
    )

    example_forecast = [
        x for x in my_storm_forecasts.forecasts if x.model_id == "HWRF"
    ][0].dataframe

    forecast_lons = example_forecast["lon"].tolist()
    forecast_lats = example_forecast["lat"].tolist()

    lons = (
        tropycal_storm_df[tropycal_storm_df["should_plot_step"]]["lon"].tolist()
        + forecast_lons
    )
    lats = (
        tropycal_storm_df[tropycal_storm_df["should_plot_step"]]["lat"].tolist()
        + forecast_lats
    )

    fig, ax = plot_base(lons=lons, lats=lats)

    ax.set_title(
        "DEVELOPING STORM: " + tropycal_storm_df["name"].values[0],
        loc="left",
        # fontsize=25,
        fontweight="bold",
    )

    # Plot historical (already happened) Dots
    for i in range(0, len(tropycal_storm_df["lat"])):
        if not tropycal_storm_df["should_plot_step"][i]:
            continue
        ax.plot(
            tropycal_storm_df["lon"][i],
            tropycal_storm_df["lat"][i],
            transform=ccrs.PlateCarree(),
            linewidth=2,
            marker="o",
            markersize=marker_size,
            color=get_colors_sshws(np.nan_to_num(tropycal_storm_df["vmax"][i])),
            zorder=2,
        )

    # Plot Already happened Line
    ax.plot(
        tropycal_storm_df["lon"].tolist(),
        tropycal_storm_df["lat"].tolist(),
        transform=ccrs.PlateCarree(),
        linewidth=1,
        color="gray",
        zorder=1,
    )

    # Forecast Lines
    models_to_plot = [
        x for x in my_storm_forecasts.forecasts if x.model_id in my_models.keys()
    ]
    for mycast in models_to_plot:
        model = mycast.model_id
        storm_forecast = mycast.dataframe

        if storm_forecast.empty:
            continue

        mydt = datetime.datetime.combine(
            mycast.forecast_date, datetime.time(hour=int(mycast.forecast_hour))
        )

        storm_forecast["already_forecasted"] = [
            (datetime.timedelta(hours=x) + mydt) < tropycal_storm_df.time.max()
            for x in storm_forecast["fhr"].tolist()
        ]

        storm_forecast = storm_forecast[~storm_forecast["already_forecasted"]]

        ax.plot(
            storm_forecast["lon"],
            storm_forecast["lat"],
            transform=ccrs.PlateCarree(),
            linewidth=1,
            color=my_models[model][
                "color"
            ],  # use the color from the dictionary, default to black if not found
            zorder=1,
            label=model,
        )
    ax.legend(loc="upper right", prop={"size": 15})
    fig.tight_layout()
    ax.set_aspect("auto")
    fig.savefig(f"{my_dir}/{storm_id}/compare.jpg")
    return fig


cone_color = "#fffde6"
cone_color = "#e6f2ff"
cone_color = "#fff8d5"
water_color = "#d5f0ff"
land_color = "#fcf3e8"
land_scale = "50m"
marker_size = 10


legend_size = 7

ex = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Non-Tropical",
    marker="^",
    color="w",
)
sb = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Subtropical",
    marker="s",
    color="w",
)
uk = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Unknown",
    marker="o",
    color="w",
)
td = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Tropical Depression",
    marker="o",
    color=get_colors_sshws(33),
)
ts = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Tropical Storm",
    marker="o",
    color=get_colors_sshws(34),
)
c1 = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Category 1",
    marker="o",
    color=get_colors_sshws(64),
)
c2 = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Category 2",
    marker="o",
    color=get_colors_sshws(83),
)
c3 = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Category 3",
    marker="o",
    color=get_colors_sshws(96),
)
c4 = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Category 4",
    marker="o",
    color=get_colors_sshws(113),
)
c5 = mlines.Line2D(
    [],
    [],
    linestyle="None",
    ms=legend_size,
    mec="k",
    mew=0.5,
    label="Category 5",
    marker="o",
    color=get_colors_sshws(137),
)

my_cone = {
    0: 0,
    12: 16,
    24: 26,
    36: 39,
    48: 53,
    60: 67,
    72: 81,
    96: 99,
    108: 145,
    120: 205,
}

my_models = {
    "HWRF": {
        "name": "Hurricane Weather Research and Forecasting Model",
        "color": "#1f77b4",  # muted blue
    },
    "AVNO": {"name": "GFS", "color": "#ff7f0e"},  # safety orange
    "CMC": {
        "name": "Canadian Meteorological Centre",
        "color": "#2ca02c",  # cooked asparagus green
    },
    "NVGM": {
        "name": "NVGM",
        "color": "#d62728",  # brick red
    },
    "ICON": {
        "name": "Icosahedral Nonhydrostatic Model",
        "color": "#9467bd",  # muted purple
    },
    "hfsa": {
        "name": "HAFS 1a",
        "color": "#e377c2",  # pink
    },
    "hfsb": {
        "name": "HAFS 1b",
        "color": "#bcbd22",  # yellowish-green
    },
}
