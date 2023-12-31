from litestar import Litestar
from litestar.logging import LoggingConfig
from litestar.openapi import OpenAPIConfig, OpenAPIController

from api_app.controllers.storm import StormController


class MyOpenAPIController(OpenAPIController):
    path = "/api/docs"


app = Litestar(
    route_handlers=[StormController],
    openapi_config=OpenAPIConfig(
        title="HackerNews API", version="1.0.0", openapi_controller=MyOpenAPIController
    ),
    logging_config=LoggingConfig(
        loggers={
            "my_app": {
                "level": "INFO",
                "handlers": ["queue_listener"],
            }
        }
    ),
    debug=True,
)
