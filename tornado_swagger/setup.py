"""Setup"""
import os
import typing

import tornado.web

from tornado_swagger._builders import generate_doc_from_endpoints
from tornado_swagger._handlers import SwaggerSpecHandler, SwaggerUiHandler
from tornado_swagger.const import API_SWAGGER_2

STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "swagger_ui"))


def export_swagger(
    routes: typing.List[tornado.web.URLSpec],
    *,
    api_base_url: str = "/",
    description: str = "Swagger API definition",
    api_version: str = "1.0.0",
    title: str = "Swagger API",
    contact: str = "",
    schemes: list = None,
    security_definitions: dict = None,
    security: list = None,
    api_definition_version: str = API_SWAGGER_2
):
    """Export swagger schema as dict"""
    return generate_doc_from_endpoints(
        routes,
        api_base_url=api_base_url,
        description=description,
        api_version=api_version,
        title=title,
        contact=contact,
        schemes=schemes,
        security_definitions=security_definitions,
        security=security,
        api_definition_version=api_definition_version,
    )


def setup_swagger(
    routes: typing.List[tornado.web.URLSpec],
    *,
    swagger_url: str = "/api/doc",
    api_base_url: str = "/",
    description: str = "Swagger API definition",
    api_version: str = "1.0.0",
    title: str = "Swagger API",
    contact: str = "",
    schemes: list = None,
    security_definitions: dict = None,
    security: list = None,
    display_models: bool = True,
    api_definition_version: str = API_SWAGGER_2
):
    """Inject swagger ui to application routes"""
    swagger_schema = generate_doc_from_endpoints(
        routes,
        api_base_url=api_base_url,
        description=description,
        api_version=api_version,
        title=title,
        contact=contact,
        schemes=schemes,
        security_definitions=security_definitions,
        security=security,
        api_definition_version=api_definition_version,
    )

    _swagger_ui_url = "/{}".format(swagger_url) if not swagger_url.startswith("/") else swagger_url
    _base_swagger_ui_url = _swagger_ui_url.rstrip("/")
    _swagger_spec_url = "{}/swagger.json".format(_swagger_ui_url)

    routes[:0] = [
        tornado.web.url(_swagger_ui_url, SwaggerUiHandler),
        tornado.web.url("{}/".format(_base_swagger_ui_url), SwaggerUiHandler),
        tornado.web.url(_swagger_spec_url, SwaggerSpecHandler),
    ]

    SwaggerSpecHandler.SWAGGER_SPEC = swagger_schema

    with open(os.path.join(STATIC_PATH, "ui.html"), "r") as f:
        SwaggerUiHandler.SWAGGER_HOME_TEMPLATE = (
            f.read().replace("{{ SWAGGER_URL }}", _swagger_spec_url).replace("{{ DISPLAY_MODELS }}", str(-1 if not display_models else 1))
        )
