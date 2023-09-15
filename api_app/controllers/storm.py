import datetime
import os

from litestar import Controller, Response, get

from api_app.models import Storm, Storms
from config.config import IMAGES_DIR

"""
/storms/{storm_id} a specific article
/storms/ all storms?
"""


def get_string_date_from_days_ago(days: int) -> str:
    mydate = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    mydate_str = mydate.strftime("%Y-%m-%d")
    return mydate_str


def get_most_recent_storm_dirs() -> tuple[str, list[str]]:
    storm_dirs: list = []
    i = 0
    while len(storm_dirs) == 0 and i <= 5:
        date_str = get_string_date_from_days_ago(i)
        if date_str in os.listdir(IMAGES_DIR):
            storm_dirs = os.listdir(f"{IMAGES_DIR}/{date_str}")
            print(f"{date_str=} found {len(storm_dirs)} directories")
        else:
            print(f"{date_str=} found no directories")
        i += 1
    return date_str, storm_dirs


def get_storm_images(date_str: str, storm_id: str) -> tuple[str, list[str]]:
    storm_dirs = os.listdir(f"{IMAGES_DIR}/{date_str}")
    return date_str, storm_dirs


class StormController(Controller):
    path = "/api/storms"

    @get(path="/")
    async def get_storms_list(self) -> Storms:
        """
        Handles a GET request for a list of storms of a certain type.

        Args:

        Returns:
            Storms: A dictionary representation of the list of articles.
        """
        date_str, storm_dirs = get_most_recent_storm_dirs()

        mydict = Storms([Storm(id=mystorm, date=date_str) for mystorm in storm_dirs])

        return mydict

    @get(path="/{date_str:str}/{storm_id:str}/ucar/image", cache=3600)
    async def get_storm_image(self, date_str: str, storm_id: str) -> Response[bytes]:
        """
        Handles a GET request for a specific storm image.

        Args:
            date_str (str): The date str in format YYYY-mm-dd
            storm_id (str): The id of the storm to retrieve.

        Returns:
            Bytes media type image/jpeg.
        """

        with open(
            f"{IMAGES_DIR}/{date_str}/{storm_id}/ucar_tropycal_forecast_realtime.jpg",
            "rb",
        ) as image_file:
            image_data = image_file.read()

        return Response(image_data, media_type="image/jpeg")

    @get(path="/{date_str:str}/{storm_id:str}/ucar/myimage", cache=3600)
    async def get_mystorm_image(self, date_str: str, storm_id: str) -> Response[bytes]:
        """
        Handles a GET request for a specific storm image.

        Args:
            date_str (str): The date str in format YYYY-mm-dd
            storm_id (str): The id of the storm to retrieve.

        Returns:
            Bytes media type image/jpeg.
        """

        with open(
            f"{IMAGES_DIR}/{date_str}/{storm_id}/ucar_myimage.jpg", "rb"
        ) as image_file:
            image_data = image_file.read()

        return Response(image_data, media_type="image/jpeg")

    @get(path="/{date_str:str}/{storm_id:str}/compare", cache=3600)
    async def get_compare_image(self, date_str: str, storm_id: str) -> Response[bytes]:
        """
        Handles a GET request for a specific storm image.

        Args:
            date_str (str): The date str in format YYYY-mm-dd
            storm_id (str): The id of the storm to retrieve.

        Returns:
            Bytes media type image/jpeg.
        """

        with open(
            f"{IMAGES_DIR}/{date_str}/{storm_id}/compare.jpg", "rb"
        ) as image_file:
            image_data = image_file.read()

        return Response(image_data, media_type="image/jpeg")

    @get(path="/{date_str:str}/{storm_id:str}/spaghetti", cache=3600)
    async def get_spaghetti_image(
        self, date_str: str, storm_id: str
    ) -> Response[bytes]:
        """
        Handles a GET request for a specific storm image.

        Args:
            date_str (str): The date str in format YYYY-mm-dd
            storm_id (str): The id of the storm to retrieve.

        Returns:
            Bytes media type image/jpeg.
        """

        with open(
            f"{IMAGES_DIR}/{date_str}/{storm_id}/spaghetti.jpg", "rb"
        ) as image_file:
            image_data = image_file.read()

        return Response(image_data, media_type="image/jpeg")
