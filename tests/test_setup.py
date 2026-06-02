"""Test setup"""

import typing

import pytest
import tornado.web

from tornado_swagger._handlers import SwaggerSpecHandler, SwaggerUiHandler, TornadoBaseHandler
from tornado_swagger.const import API_OPENAPI_3
from tornado_swagger.setup import export_swagger, setup_swagger

SWAGGER_URL = "/api/doc"


class ExampleHandler(tornado.web.RequestHandler):
    def get(self):
        """Description end-point

        ---
        tags:
        - Example
        summary: Create user
        description: This can only be done by the logged in user.
        operationId: examples.api.api.createUser
        produces:
        - application/json
        """
        self.write({})


class Application(tornado.web.Application):
    routes: typing.ClassVar = [tornado.web.url(r"/api/example", ExampleHandler)]

    def __init__(self):
        setup_swagger(
            self.routes,
            swagger_url=SWAGGER_URL,
        )
        super().__init__(self.routes)


def test_export_swagger():
    assert export_swagger(Application.routes)


def test_export_swagger_accepts_openapi_security_schemes():
    docs = export_swagger(
        [],
        api_definition_version=API_OPENAPI_3,
        security_schemes={"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
        security=[{"BearerAuth": []}],
    )

    assert docs["components"]["securitySchemes"] == {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
    assert docs["security"] == [{"BearerAuth": []}]


def test_swagger_setup_configures_ui_handler_template():
    Application()

    handler = StubHandler(allow_cors=False)
    handler.SWAGGER_HOME_TEMPLATE = SwaggerUiHandler.SWAGGER_HOME_TEMPLATE
    SwaggerUiHandler.get(handler)

    assert "Swagger UI" in handler.body
    assert f"{SWAGGER_URL}/swagger.json" in handler.body


def test_swagger_spec_handler_writes_configured_spec():
    handler = StubHandler(allow_cors=False)
    handler.SWAGGER_SPEC = {"swagger": "2.0"}

    SwaggerSpecHandler.get(handler)

    assert handler.body == {"swagger": "2.0"}


def test_setup_swagger_accepts_relative_url_and_configures_handlers():
    class RelativeUrlHandler(tornado.web.RequestHandler):
        def get(self):
            """---
            tags:
            - Example
            """
            self.write({})

    routes = [tornado.web.url(r"/api/relative", RelativeUrlHandler)]

    setup_swagger(
        routes,
        swagger_url="docs",
        display_models=False,
        allow_cors=True,
        cors_origin="https://example.com",
        title="Configured API",
    )

    assert routes[0].regex.pattern == "/docs$"
    assert routes[1].regex.pattern == "/docs/$"
    assert routes[2].regex.pattern == "/docs/swagger.json$"
    assert routes[2].target is SwaggerSpecHandler
    assert SwaggerSpecHandler.SWAGGER_SPEC["info"]["title"] == "Configured API"
    assert SwaggerSpecHandler.allow_cors is True
    assert SwaggerUiHandler.allow_cors is True
    assert SwaggerSpecHandler.cors_origin == "https://example.com"
    assert SwaggerUiHandler.cors_origin == "https://example.com"
    assert "/docs/swagger.json" in SwaggerUiHandler.SWAGGER_HOME_TEMPLATE
    assert "defaultModelsExpandDepth: -1" in SwaggerUiHandler.SWAGGER_HOME_TEMPLATE


class StubHandler:
    def __init__(self, allow_cors, cors_origin="*"):
        self.allow_cors = allow_cors
        self.cors_origin = cors_origin
        self.body = ""
        self.headers = {}

    def set_header(self, name, value):
        self.headers[name] = value

    def set_cors_headers(self):
        TornadoBaseHandler.set_cors_headers(self)

    def write(self, body):
        self.body = body


@pytest.mark.parametrize("handler_class", [SwaggerUiHandler, SwaggerSpecHandler])
def test_swagger_handlers_set_cors_headers_when_enabled(handler_class):
    handler = StubHandler(allow_cors=True)

    handler_class.options(handler)

    assert handler.headers == {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
    }


@pytest.mark.parametrize("handler_class", [SwaggerUiHandler, SwaggerSpecHandler])
def test_swagger_handlers_skip_cors_headers_when_disabled(handler_class):
    handler = StubHandler(allow_cors=False)

    handler_class.options(handler)

    assert handler.headers == {}


@pytest.mark.parametrize("handler_class", [SwaggerUiHandler, SwaggerSpecHandler])
def test_swagger_handlers_use_configured_cors_origin(handler_class):
    handler = StubHandler(allow_cors=True, cors_origin="https://example.com")

    handler_class.options(handler)

    assert handler.headers == {
        "Access-Control-Allow-Origin": "https://example.com",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Vary": "Origin",
    }


@pytest.mark.parametrize("handler_class", [SwaggerUiHandler, SwaggerSpecHandler])
def test_swagger_handlers_skip_vary_header_for_wildcard_origin(handler_class):
    handler = StubHandler(allow_cors=True, cors_origin="*")

    handler_class.options(handler)

    assert "Vary" not in handler.headers


@pytest.mark.parametrize("handler_class", [SwaggerUiHandler, SwaggerSpecHandler])
def test_swagger_handlers_set_cors_headers_on_get_when_enabled(handler_class):
    handler = StubHandler(allow_cors=True)
    handler.SWAGGER_HOME_TEMPLATE = ""
    handler.SWAGGER_SPEC = ""

    handler_class.get(handler)

    assert handler.headers == {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
    }


@pytest.mark.parametrize("handler_class", [SwaggerUiHandler, SwaggerSpecHandler])
def test_swagger_handlers_skip_cors_headers_on_get_when_disabled(handler_class):
    handler = StubHandler(allow_cors=False)
    handler.SWAGGER_HOME_TEMPLATE = ""
    handler.SWAGGER_SPEC = ""

    handler_class.get(handler)

    assert handler.headers == {}


def test_base_handler_data_received_is_noop():
    assert TornadoBaseHandler.data_received(None, b"chunk") is None
