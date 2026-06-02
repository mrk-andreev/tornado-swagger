"""Setup."""

from __future__ import annotations

import typing
from pathlib import Path

import tornado.web

from tornado_swagger._builders import generate_doc_from_endpoints
from tornado_swagger._handlers import SwaggerSpecHandler, SwaggerUiHandler
from tornado_swagger.const import API_SWAGGER_2

STATIC_PATH = Path(__file__).parent / "swagger_ui"


def export_swagger(
    routes: list[tornado.web.URLSpec],
    *,
    api_base_url: str = "/",
    description: str = "Swagger API definition",
    api_version: str = "1.0.0",
    title: str = "Swagger API",
    contact: str = "",
    schemes: list[typing.Any] | None = None,
    security_definitions: dict[str, typing.Any] | None = None,
    security_schemes: dict[str, typing.Any] | None = None,
    security: list[typing.Any] | None = None,
    api_definition_version: str = API_SWAGGER_2,
) -> dict[str, typing.Any]:
    """Export swagger schema as dict."""
    return generate_doc_from_endpoints(
        routes,
        api_base_url=api_base_url,
        description=description,
        api_version=api_version,
        title=title,
        contact=contact,
        schemes=schemes,
        security_definitions=security_definitions,
        security_schemes=security_schemes,
        security=security,
        api_definition_version=api_definition_version,
    )


def setup_swagger(
    routes: list[tornado.web.URLSpec],
    *,
    swagger_url: str = "/api/doc",
    api_base_url: str = "/",
    description: str = "Swagger API definition",
    api_version: str = "1.0.0",
    title: str = "Swagger API",
    contact: str = "",
    schemes: list[typing.Any] | None = None,
    security_definitions: dict[str, typing.Any] | None = None,
    security_schemes: dict[str, typing.Any] | None = None,
    security: list[typing.Any] | None = None,
    display_models: bool = True,
    api_definition_version: str = API_SWAGGER_2,
    allow_cors: bool = False,
    cors_origin: str = "*",
) -> None:
    """Inject swagger ui to application routes."""
    swagger_schema = generate_doc_from_endpoints(
        routes,
        api_base_url=api_base_url,
        description=description,
        api_version=api_version,
        title=title,
        contact=contact,
        schemes=schemes,
        security_definitions=security_definitions,
        security_schemes=security_schemes,
        security=security,
        api_definition_version=api_definition_version,
    )

    _swagger_ui_url = f"/{swagger_url}" if not swagger_url.startswith("/") else swagger_url
    _base_swagger_ui_url = _swagger_ui_url.rstrip("/")
    _swagger_spec_url = f"{_swagger_ui_url}/swagger.json"

    routes[:0] = [
        tornado.web.url(_swagger_ui_url, SwaggerUiHandler),
        tornado.web.url(f"{_base_swagger_ui_url}/", SwaggerUiHandler),
        tornado.web.url(_swagger_spec_url, SwaggerSpecHandler),
    ]

    SwaggerSpecHandler.SWAGGER_SPEC = swagger_schema
    SwaggerSpecHandler.allow_cors = allow_cors
    SwaggerSpecHandler.cors_origin = cors_origin
    SwaggerUiHandler.allow_cors = allow_cors
    SwaggerUiHandler.cors_origin = cors_origin

    with (STATIC_PATH / "ui.html").open(encoding="utf-8") as f:
        SwaggerUiHandler.SWAGGER_HOME_TEMPLATE = (
            f.read().replace("{{ SWAGGER_URL }}", _swagger_spec_url).replace("{{ DISPLAY_MODELS }}", str(-1 if not display_models else 1))
        )
