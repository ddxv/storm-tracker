from litestar import Controller, get

from api_app.models import Storm, Storms

"""
/storms/{storm_id} a specific article
/storms/ all storms?
"""


class StormController(Controller):
    path = "/api/storms"

    @get(path="/{storm_id:str}")
    async def get_storm(self, storm_id: str) -> Storm:
        """
        Handles a GET request for a specific storm.

        Args:
            storm_id (storm): The id of the storm to retrieve.

        Returns:
            Storm: A dictionary representation of the storm.
        """
        # df = query_article(storm_id)
        mydict: Storm = Storm(storm_id, crawled_at="2021-10-10")
        return mydict

    @get(path="/")
    async def get_storms_list(self) -> Storms:
        """
        Handles a GET request for a list of storms of a certain type.

        Args:

        Returns:
            Storms: A dictionary representation of the list of articles.
        """
        mydict: Storms = Storms(
            [
                Storm(id="1", crawled_at="2021-10-10"),
                Storm(id="2", crawled_at="2022-10-10"),
            ]
        )
        return mydict
