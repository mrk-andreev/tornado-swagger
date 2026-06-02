"""Test builders"""

import functools
import types

import pytest
import tornado.web

from tornado_swagger._builders import (
    SWAGGER_DOC_SEPARATOR,
    _build_doc_from_func_doc,
    _extract_parameters_names,
    _format_handler_path,
    _strip_path_prefix,
    _try_extract_args,
    _try_extract_doc,
    build_swagger_docs,
    doc_builders,
    generate_doc_from_endpoints,
    nesteddict2yaml,
)
from tornado_swagger.const import API_OPENAPI_3, API_OPENAPI_3_1, API_SWAGGER_2

INVALID_ENDPOINT_DOC = SWAGGER_DOC_SEPARATOR + """
tag"""
ENDPOINT_DOC = SWAGGER_DOC_SEPARATOR + """
tags:
  - Example
summary: Create user
description: This can only be done by the logged in user.
operationId: examples.api.api.createUser
produces:
  - application/json
parameters:
  - in: body
    name: body
    description: Created user object
    required: false
    schema:
      type: object
      properties:
        id:
          type: integer
          format: int64
        username:
          type:
            - "string"
            - "null"
        firstName:
          type: string
        lastName:
          type: string
        email:
          type: string
        password:
          type: string
        phone:
          type: string
        userStatus:
          type: integer
          format: int32
          description: User Status
responses:
  201:
    description: successful operation
"""
INVALID_SWAGGER_TEXT = "Invalid Swagger"


def test_extract_swagger_docs():
    docs = build_swagger_docs(ENDPOINT_DOC)
    assert INVALID_SWAGGER_TEXT not in docs["tags"]


def test_invalid_extract_swagger_docs():
    docs = build_swagger_docs(INVALID_ENDPOINT_DOC)
    assert INVALID_SWAGGER_TEXT in docs["tags"]


def test_extract_swagger_docs_replaces_tabs():
    docs = build_swagger_docs(SWAGGER_DOC_SEPARATOR + """
tags:
\t- Example
""")
    assert docs["tags"] == ["Example"]


class ExampleHandler(tornado.web.RequestHandler):
    def get(self):
        pass


def test_build_doc_from_func_doc():
    ExampleHandler.get.__doc__ = ENDPOINT_DOC
    docs = _build_doc_from_func_doc(ExampleHandler)
    assert INVALID_SWAGGER_TEXT not in docs["get"]["tags"]


@pytest.mark.parametrize("api_definition_version", doc_builders.keys())
def test_generate_doc_from_each_end_point(api_definition_version):
    ExampleHandler.get.__doc__ = ENDPOINT_DOC
    routes = [
        tornado.web.url(r"/api/example", ExampleHandler, name="example"),
    ]

    docs = generate_doc_from_endpoints(
        routes,
        api_base_url="/",
        description="",
        api_version="",
        title="",
        contact="",
        strip_prefix=None,
        security_definitions=None,
        schemes=[],
        security=None,
        api_definition_version=api_definition_version,
    )
    assert docs


def test_generate_doc_keeps_request_body_on_post_operations():
    class PostExampleHandler(tornado.web.RequestHandler):
        def post(self):
            # Body is irrelevant; only the method signature and docstring are introspected.
            pass

    PostExampleHandler.post.__doc__ = ENDPOINT_DOC
    routes = [
        tornado.web.url(r"/api/example", PostExampleHandler, name="example"),
    ]

    docs = generate_doc_from_endpoints(
        routes,
        api_base_url="/",
        description="",
        api_version="",
        title="",
        contact="",
        strip_prefix=None,
        security_definitions=None,
        schemes=[],
        security=None,
        api_definition_version=API_SWAGGER_2,
    )

    operation = docs["paths"]["/api/example"]["post"]
    assert operation["parameters"][0]["in"] == "body"
    assert operation["responses"] == {201: {"description": "successful operation"}}


def test_generate_doc_unknown_api_definition_version():
    with pytest.raises(ValueError, match="Unknown api_definition_version"):
        generate_doc_from_endpoints(
            [],
            api_base_url="/",
            description="",
            api_version="",
            title="",
            contact="",
            strip_prefix=None,
            security_definitions=None,
            schemes=[],
            security=None,
            api_definition_version="unknown",
        )


def test_generate_swagger_2_doc_includes_optional_metadata():
    docs = generate_doc_from_endpoints(
        [],
        api_base_url="/api",
        description="\n\nExample API",
        api_version="1.2.3",
        title="Example",
        contact="Team",
        strip_prefix=None,
        security_definitions={"ApiKeyAuth": {"type": "apiKey"}},
        schemes=["https"],
        security=[{"ApiKeyAuth": []}],
        api_definition_version=API_SWAGGER_2,
    )

    assert docs["swagger"] == "2.0"
    assert docs["info"] == {
        "title": "Example",
        "description": "Example API",
        "version": "1.2.3",
        "contact": {"name": "Team"},
    }
    assert docs["basePath"] == "/api"
    assert docs["schemes"] == ["https"]
    assert docs["securityDefinitions"] == {"ApiKeyAuth": {"type": "apiKey"}}
    assert docs["security"] == [{"ApiKeyAuth": []}]


def test_generate_openapi_doc_uses_components_for_models_and_parameters(monkeypatch):
    monkeypatch.setattr(
        "tornado_swagger.model.export_swagger_models",
        lambda: {"Pet": {"type": "object"}},
    )
    monkeypatch.setattr(
        "tornado_swagger.parameter.export_swagger_parameters",
        lambda: {"Limit": {"name": "limit"}},
    )

    docs = generate_doc_from_endpoints(
        [],
        api_base_url="/api",
        description="Example API",
        api_version="1.2.3",
        title="Example",
        contact="",
        strip_prefix=None,
        security_definitions=None,
        schemes=["https"],
        security=None,
        api_definition_version=API_OPENAPI_3,
    )

    assert docs["openapi"] == "3.0.3"
    assert docs["components"] == {
        "schemas": {"Pet": {"type": "object"}},
        "parameters": {"Limit": {"name": "limit"}},
    }


def test_generate_openapi_doc_uses_servers_instead_of_swagger_2_base_fields():
    docs = generate_doc_from_endpoints(
        [],
        api_base_url="/api",
        description="Example API",
        api_version="1.2.3",
        title="Example",
        contact="",
        strip_prefix=None,
        security_definitions=None,
        schemes=["https"],
        security=None,
        api_definition_version=API_OPENAPI_3,
    )

    assert docs["servers"] == [{"url": "/api"}]
    assert "basePath" not in docs
    assert "schemes" not in docs


def test_generate_openapi_31_doc_emits_31_version():
    docs = generate_doc_from_endpoints(
        [],
        api_base_url="/api",
        description="Example API",
        api_version="1.2.3",
        title="Example",
        contact="",
        strip_prefix=None,
        security_definitions=None,
        schemes=["https"],
        security=None,
        api_definition_version=API_OPENAPI_3_1,
    )

    assert docs["openapi"] == "3.1.0"
    assert docs["servers"] == [{"url": "/api"}]


def test_generate_openapi_doc_includes_optional_metadata():
    security_schemes = {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}

    docs = generate_doc_from_endpoints(
        [],
        api_base_url="/api",
        description="Example API",
        api_version="1.2.3",
        title="Example",
        contact="Team",
        strip_prefix=None,
        security_definitions=None,
        security_schemes=security_schemes,
        schemes=["https"],
        security=[{"BearerAuth": []}],
        api_definition_version=API_OPENAPI_3,
    )

    assert docs["info"]["contact"] == {"name": "Team"}
    assert "securityDefinitions" not in docs
    assert docs["components"]["securitySchemes"] == security_schemes
    assert docs["security"] == [{"BearerAuth": []}]


def test_generate_openapi_doc_keeps_security_definitions_backwards_compatibility():
    security_definitions = {"ApiKeyAuth": {"type": "apiKey"}}

    docs = generate_doc_from_endpoints(
        [],
        api_base_url="/api",
        description="Example API",
        api_version="1.2.3",
        title="Example",
        contact="",
        strip_prefix=None,
        security_definitions=security_definitions,
        schemes=["https"],
        security=[{"ApiKeyAuth": []}],
        api_definition_version=API_OPENAPI_3,
    )

    assert docs["components"]["securitySchemes"] == security_definitions


def test_generate_swagger_2_doc_rejects_openapi_security_schemes():
    with pytest.raises(ValueError, match="security_schemes is only supported"):
        generate_doc_from_endpoints(
            [],
            api_base_url="/api",
            description="Example API",
            api_version="1.2.3",
            title="Example",
            contact="",
            strip_prefix=None,
            security_definitions=None,
            security_schemes={"BearerAuth": {"type": "http", "scheme": "bearer"}},
            schemes=["https"],
            security=[{"BearerAuth": []}],
            api_definition_version=API_SWAGGER_2,
        )


def test_generate_swagger_2_doc_rejects_http_security_definition():
    with pytest.raises(ValueError, match="HTTP security schemes require"):
        generate_doc_from_endpoints(
            [],
            api_base_url="/api",
            description="Example API",
            api_version="1.2.3",
            title="Example",
            contact="",
            strip_prefix=None,
            security_definitions={"BearerAuth": {"type": "http", "scheme": "bearer"}},
            schemes=["https"],
            security=[{"BearerAuth": []}],
            api_definition_version=API_SWAGGER_2,
        )


def test_extract_parameters_names_empty_parameter():
    class HandlerWithEmptyParameter(tornado.web.RequestHandler):
        def get(self):
            pass

    parameters = _extract_parameters_names(HandlerWithEmptyParameter, 0, method="get")
    assert parameters == []


def test_extract_parameters_names_signle_parameter():
    class HandlerWithSingleParameter(tornado.web.RequestHandler):
        def get(self, posts_id):
            pass

    parameters = _extract_parameters_names(HandlerWithSingleParameter, 1, method="get")
    assert parameters == ["posts_id"]


def test_extract_parameters_names_multiple():
    class HandlerWithMultipleParameter(tornado.web.RequestHandler):
        def get(self, posts_id, post_id2, post_id3):
            pass

    parameters = _extract_parameters_names(HandlerWithMultipleParameter, 3, method="get")
    assert parameters == ["posts_id", "post_id2", "post_id3"]


def test_extract_parameters_names_ignores_underscore_placeholders():
    class HandlerWithIgnoredParameter(tornado.web.RequestHandler):
        def get(self, _, post_id):
            # Body is irrelevant; only the method signature is introspected.
            pass

    parameters = _extract_parameters_names(HandlerWithIgnoredParameter, 2, method="get")
    assert parameters == ["{?}", "post_id"]


def test__format_handler_path():
    class HandlerWithMultipleParameter(tornado.web.RequestHandler):
        def get(self, posts_id, post_id2, post_id3):
            pass

    route_path = _format_handler_path(
        tornado.web.url(r"/api/(\w+)/(\w+)/(\w+)", HandlerWithMultipleParameter),
        method="get",
    )
    assert route_path == "/api/{posts_id}/{post_id2}/{post_id3}"


@pytest.mark.parametrize(
    ("path", "strip_prefix", "expected"),
    [
        ("/services/gradingtool-service/submit_sync", "/services/gradingtool-service", "/submit_sync"),
        ("/services/gradingtool-service", "/services/gradingtool-service", "/"),
        ("/services/gradingtool-service/submit_sync", "services/gradingtool-service/", "/submit_sync"),
        ("/apiary/submit_sync", "/api", "/apiary/submit_sync"),
        ("/api/submit_sync", None, "/api/submit_sync"),
        ("/api/submit_sync", "/", "/api/submit_sync"),
    ],
)
def test_strip_path_prefix_respects_path_boundaries(path, strip_prefix, expected):
    assert _strip_path_prefix(path, strip_prefix) == expected


@pytest.mark.parametrize("api_definition_version", doc_builders.keys())
def test_generate_doc_strips_configured_route_prefix(api_definition_version):
    class PrefixedHandler(tornado.web.RequestHandler):
        def get(self, item_id=None):
            """---
            tags:
            - Example
            """

    routes = [
        tornado.web.url(r"/services/gradingtool-service/submit_sync", PrefixedHandler),
        tornado.web.url(r"/services/gradingtool-service/items/(\w+)", PrefixedHandler),
    ]

    docs = generate_doc_from_endpoints(
        routes,
        api_base_url="/services/gradingtool-service",
        description="",
        api_version="",
        title="",
        contact="",
        strip_prefix="/services/gradingtool-service",
        security_definitions=None,
        schemes=[],
        security=None,
        api_definition_version=api_definition_version,
    )

    assert sorted(docs["paths"]) == ["/items/{item_id}", "/submit_sync"]


def test_generate_doc_keeps_prefixed_routes_without_strip_prefix():
    class PrefixedHandler(tornado.web.RequestHandler):
        def get(self):
            """---
            tags:
            - Example
            """

    routes = [tornado.web.url(r"/services/gradingtool-service/submit_sync", PrefixedHandler)]

    docs = generate_doc_from_endpoints(
        routes,
        api_base_url="/services/gradingtool-service",
        description="",
        api_version="",
        title="",
        contact="",
        security_definitions=None,
        schemes=[],
        security=None,
        api_definition_version=API_SWAGGER_2,
    )

    assert sorted(docs["paths"]) == ["/services/gradingtool-service/submit_sync"]


def test_format_handler_path_skips_illegal_route():
    class HandlerWithMultipleParameter(tornado.web.RequestHandler):
        def get(self, posts_id, post_id2):
            # Body is irrelevant; only the method signature is introspected.
            pass

    route = types.SimpleNamespace(
        target=HandlerWithMultipleParameter,
        regex=types.SimpleNamespace(groups=2, pattern=r"/api/(\w+)$"),
    )

    with pytest.warns(UserWarning, match="Illegal route"):
        route_path = _format_handler_path(route, method="get")

    assert route_path is None


def test_generate_doc_skips_illegal_route_paths():
    class HandlerWithIllegalRoute(tornado.web.RequestHandler):
        def get(self, posts_id, post_id2):
            """---
            tags:
            - Example
            """

    route = types.SimpleNamespace(
        target=HandlerWithIllegalRoute,
        regex=types.SimpleNamespace(groups=2, pattern=r"/api/(\w+)$"),
    )

    with pytest.warns(UserWarning, match="Illegal route"):
        docs = generate_doc_from_endpoints(
            [route],
            api_base_url="/",
            description="",
            api_version="",
            title="",
            contact="",
            security_definitions=None,
            schemes=[],
            security=None,
            api_definition_version=API_SWAGGER_2,
        )

    assert docs["paths"] == {}


def test_nesteddict2yaml():
    rendered = nesteddict2yaml({"info": {"title": "Example"}, "basePath": "/"}, indent=0)
    assert rendered == "info:\n  title: Example\nbasePath: /\n"


def test_try_extract_args():
    def method_handler(self, arg_name):
        raise NotImplementedError

    args = _try_extract_args(method_handler)
    assert "arg_name" in args


def test_try_extract_decorated_args():
    def dummy_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    @dummy_decorator
    def method_handler(self, arg_name):
        raise NotImplementedError

    args = _try_extract_args(method_handler)
    assert "arg_name" in args


def test_try_extract_doc():
    def method_handler(self, arg_name):
        """---
        Foo
        """
        raise NotImplementedError

    doc = _try_extract_doc(method_handler)
    assert "Foo" in doc


def test_try_extract_decorated_doc():
    def dummy_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    @dummy_decorator
    def method_handler(self, arg_name):
        """---
        Foo
        """
        raise NotImplementedError

    doc = _try_extract_doc(method_handler)
    assert "Foo" in doc
