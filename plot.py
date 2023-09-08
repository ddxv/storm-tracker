import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
from cartopy.mpl.ticker import LatitudeFormatter, LatitudeLocator, LongitudeFormatter
from matplotlib.pyplot import Axes
from tropycal.realtime import RealtimeStorm


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
    plot_height = max(
        [storm_height + padding_vertical, storm_width + padding_horizontal]
    )
    plot_width = max(
        [storm_height + padding_vertical, storm_width + padding_horizontal]
    )

    plot_n = central_lat + plot_height / 2
    plot_s = central_lat - plot_height / 2
    plot_e = central_lon + plot_width / 2
    plot_w = central_lon - plot_width / 2
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


def plot_storm(storm: RealtimeStorm, storm_forecast: dict) -> plt.figure:
    by_hour = 12
    storm["should_plot_step"] = [x.hour / by_hour == 0 for x in storm["time"]]
    storm_forecast["already_forcasted"] = [
        (datetime.timedelta(hours=x) + storm_forecast["init"]) <= storm.time.max()
        for x in storm_forecast["fhr"]
    ]

    fig, ax = plot_base(storm, storm_forecast)

    ax.set_title(
        "DEVELOPING HURRICANE " + storm["name"],
        loc="left",
        # fontsize=25,
        fontweight="bold",
    )
    ax.legend(handles=[td, ts, c1, c2, c3, c4, c5], prop={"size": 7.5})

    # Plot historical (already happened) Dots
    storm_line_x = []
    storm_line_y = []
    for i in range(0, len(storm["lat"])):
        if not storm["should_plot_step"][i]:
            continue
        ax.plot(
            storm["lon"][i],
            storm["lat"][i],
            transform=ccrs.PlateCarree(),
            linewidth=2,
            marker="o",
            markersize=marker_size,
            color=get_colors_sshws(np.nan_to_num(storm["vmax"][i])),
            zorder=2,
        )
        storm_line_x.append(storm["lon"][i])
        storm_line_y.append(storm["lat"][i])

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
    for i in range(0, len(storm_forecast["lat"])):
        if storm_forecast["already_forcasted"][i]:
            continue

        fhr = storm_forecast["fhr"][i]
        x = storm_forecast["lon"][i]
        y = storm_forecast["lat"][i]

        ax.plot(
            x,
            y,
            transform=ccrs.PlateCarree(),
            marker="o",
            color=get_colors_sshws(np.nan_to_num(storm_forecast["vmax"][i])),
            markersize=marker_size,
            zorder=2,
        )
        # Lables for hrs after forecast
        if not fhr % 24 == 0:
            continue
        add_annotation_pointers(ax, fhr=fhr, xy=(x, y))

    return fig


def plot_base(storm: RealtimeStorm, storm_forecast: dict) -> tuple[plt.figure, Axes]:
    lats = storm["lat"].tolist() + storm_forecast["lat"]
    lons = storm["lon"].tolist() + storm_forecast["lon"]

    plot_box, central_lat, central_lon = get_plot_box(lats, lons)

    fig = plt.figure(figsize=(5, 5), dpi=400)

    ax = plt.axes(
        projection=ccrs.Orthographic(
            central_longitude=central_lon, central_latitude=central_lat
        )
    )

    add_background_maps(ax)

    add_grid_lines(ax)
    ax.set_extent(plot_box, crs=ccrs.PlateCarree())
    fig.tight_layout()
    ax.set_aspect("auto")

    add_background_maps(ax)

    return fig, ax


def plot_all_forecasts(storm: RealtimeStorm, forecasts: dict) -> plt.figure:
    fig, ax = plot_base(storm, forecasts["HWRF"][max(forecasts["HWRF"].keys())])

    ax.set_title(
        "DEVELOPING HURRICANE " + storm["name"],
        loc="left",
        # fontsize=25,
        fontweight="bold",
    )
    # ax.legend(handles=[td, ts, c1, c2, c3, c4, c5], prop={"size": 7.5})

    # Plot historical (already happened) Dots
    storm_line_x = []
    storm_line_y = []
    for i in range(0, len(storm["lat"])):
        if not storm["should_plot_step"][i]:
            continue
        ax.plot(
            storm["lon"][i],
            storm["lat"][i],
            transform=ccrs.PlateCarree(),
            linewidth=2,
            marker="o",
            markersize=marker_size,
            color=get_colors_sshws(np.nan_to_num(storm["vmax"][i])),
            zorder=2,
        )
        storm_line_x.append(storm["lon"][i])
        storm_line_y.append(storm["lat"][i])

    # Plot Already happened Line
    ax.plot(
        storm_line_x,
        storm_line_y,
        transform=ccrs.PlateCarree(),
        linewidth=1,
        color="gray",
        zorder=1,
    )

    # Forecast Lines
    for model in forecasts.keys():
        if model in my_models.keys():
            continue
        storm_forecast = forecasts[model][max(forecasts[model].keys())]
        by_hour = 12
        storm["should_plot_step"] = [x.hour / by_hour == 0 for x in storm["time"]]
        storm_forecast["already_forcasted"] = [
            (datetime.timedelta(hours=x) + storm_forecast["init"]) < storm.time.max()
            for x in storm_forecast["fhr"]
        ]

        plot_x = []
        plot_y = []
        for i in range(0, len(storm_forecast["lat"])):
            if storm_forecast["already_forcasted"][i]:
                continue
            else:
                plot_x.append(storm_forecast["lon"][i])
                plot_y.append(storm_forecast["lat"][i])

        ax.plot(
            plot_x,
            plot_y,
            transform=ccrs.PlateCarree(),
            linewidth=0.5,
            color="blue",
            zorder=1,
        )

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

my_models = models_dict = {
    # "GFSO": "Global Forecast System Operational",
    "HWRF": "Hurricane Weather Research and Forecasting Model",
    "UKX": "UK Met Office Model",
    # "NAM": "North American Mesoscale Forecast System",
    "CMC": "Canadian Meteorological Centre",
    "HMON": "Hurricanes in a Multi-scale Ocean-coupled Non-hydrostatic Model",
    "ICON": "Icosahedral Nonhydrostatic Model",
}

# fig = plot_storm(storm, storm_forecast)
# fig.show()

# fig = plot_all_forecasts(storm, forecasts)
# fig.show()
