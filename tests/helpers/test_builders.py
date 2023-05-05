import functools

import pytest
import tornado.web

from tornado_swagger._builders import (
    SWAGGER_DOC_SEPARATOR,
    _build_doc_from_func_doc,
    _extract_parameters_names,
    _format_handler_path,
    _try_extract_args,
    _try_extract_doc,
    build_swagger_docs,
    doc_builders,
    generate_doc_from_endpoints,
)

INVALID_ENDPOINT_DOC = (
    SWAGGER_DOC_SEPARATOR
    + """
tag"""
)
ENDPOINT_DOC = (
    SWAGGER_DOC_SEPARATOR
    + """
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
"201":
  description: successful operation
"""
)
INVALID_SWAGGER_TEXT = "Invalid Swagger"


def test_extract_swagger_docs():
    docs = build_swagger_docs(ENDPOINT_DOC)
    assert INVALID_SWAGGER_TEXT not in docs["tags"]


def test_invalid_extract_swagger_docs():
    docs = build_swagger_docs(INVALID_ENDPOINT_DOC)
    assert INVALID_SWAGGER_TEXT in docs["tags"]


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
        security_definitions=None,
        schemes=[],
        security=None,
        api_definition_version=api_definition_version
    )
    assert docs


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


def test__format_handler_path():
    class HandlerWithMultipleParameter(tornado.web.RequestHandler):
        def get(self, posts_id, post_id2, post_id3):
            pass

    route_path = _format_handler_path(
        tornado.web.url(r"/api/(\w+)/(\w+)/(\w+)", HandlerWithMultipleParameter),
        method="get",
    )
    assert route_path == "/api/{posts_id}/{post_id2}/{post_id3}"


def test_try_extract_args():
    def method_handler(self, arg_name):
        raise NotImplementedError()

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
        raise NotImplementedError()

    args = _try_extract_args(method_handler)
    assert "arg_name" in args


def test_try_extract_doc():
    def method_handler(self, arg_name):
        """
        ---
        Foo
        """
        raise NotImplementedError()

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
        """
        ---
        Foo
        """
        raise NotImplementedError()

    doc = _try_extract_doc(method_handler)
    assert "Foo" in doc
