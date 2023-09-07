import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
from cartopy.mpl.ticker import LatitudeFormatter, LatitudeLocator, LongitudeFormatter
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


def plot_storm(storm: RealtimeStorm, storm_forecast: dict) -> plt.figure:
    lats = storm["lat"].tolist() + storm_forecast["lat"]
    lons = storm["lon"].tolist() + storm_forecast["lon"]

    storm_s = min(lats) - 5
    storm_n = max(lats) + 5
    storm_w = max(lons) + 5
    storm_e = min(lons) - 5
    storm_box = (storm_w, storm_e, storm_s, storm_n)

    # Create an instance of figure and axes
    fig = plt.figure(figsize=(9, 6), dpi=400)
    central_lon = (storm_box[0] + storm_box[1]) / 2
    central_lat = (storm_box[2] + storm_box[3]) / 2

    ax = plt.axes(
        projection=ccrs.Orthographic(
            central_longitude=central_lon, central_latitude=central_lat
        )
    )

    ax.set_title(
        "DEVELOPING HURRICANE " + storm["name"],
        loc="left",
        fontsize=25,
        fontweight="bold",
    )
    # ax.set_title(label=storm['name'], loc='left', fontsize=17, fontweight='bold')

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

    # Plot Line
    ax.plot(
        storm["lon"],
        storm["lat"],
        transform=ccrs.PlateCarree(),
        linewidth=1,
        color="gray",
    )

    # Plot Dots
    for i in range(0, len(storm["lat"])):
        ax.plot(
            storm["lon"][i],
            storm["lat"][i],
            transform=ccrs.PlateCarree(),
            linewidth=2,
            marker="o",
            color=get_colors_sshws(np.nan_to_num(storm["vmax"][i])),
        )

    for i in range(0, len(storm_forecast["lat"])):
        if storm_forecast["already_forcasted"][i]:
            continue

        ax.annotate(
            text=str(storm_forecast["fhr"][i]),
            xy=(storm_forecast["lon"][i], storm_forecast["lat"][i]),
            xycoords="data",
            xytext=(20, 20),
            textcoords="offset points",
            fontweight="bold",
            ha="center",
            va="center",
            arrowprops=dict(
                arrowstyle="-",  # ->
                shrinkA=0,
                shrinkB=0,
                connectionstyle="arc3",
                color="k",
            ),
            transform=ccrs.PlateCarree(),
            clip_on=True,
            zorder=1,
        )

        ax.plot(
            storm_forecast["lon"][i],
            storm_forecast["lat"][i],
            transform=ccrs.PlateCarree(),
            marker="o",
            color=get_colors_sshws(np.nan_to_num(storm_forecast["vmax"][i])),
            markersize=20,
            zorder=2,
        )

    ax.legend(handles=[ex, sb, uk, td, ts, c1, c2, c3, c4, c5], prop={"size": 7.5})

    label_style = {"size": 12, "color": "black"}

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
    # gl.xlines = False
    # gl.xlocator = mticker.FixedLocator([-180, -45, 0, 45, 180])
    gl.ylocator = LatitudeLocator()
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    gl.ylabel_style = label_style
    gl.xlabel_style = label_style

    # Zoom in over the Gulf Coast
    ax.set_extent(storm_box, crs=ccrs.PlateCarree())
    return fig


water_color = "#d5f0ff"
land_color = "#fcf3e8"
land_scale = "50m"


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
