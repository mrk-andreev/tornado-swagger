import tornado.web

from tornado_swagger.helpers.builders import _build_doc_from_func_doc
from tornado_swagger.helpers.builders import _extract_swagger_docs
from tornado_swagger.helpers.builders import generate_doc_from_each_end_point

SWAGGER_DOC_SEPARATOR = '---'

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
"201":
  description: successful operation
"""

METHOD_NAME = 'get'


def test_extract_swagger_docs():
    docs = _extract_swagger_docs(ENDPOINT_DOC.splitlines(), METHOD_NAME)
    assert 'Invalid Swagger' not in docs['get']['tags']


def test_invalid_extract_swagger_docs():
    docs = _extract_swagger_docs(ENDPOINT_DOC, METHOD_NAME)
    assert 'Invalid Swagger' in docs['get']['tags']


class ExampleHandler(tornado.web.RequestHandler):
    def get(self):
        pass


def test_build_doc_from_func_doc():
    ExampleHandler.get.__doc__ = ENDPOINT_DOC
    docs = _build_doc_from_func_doc(ExampleHandler)
    assert 'Invalid Swagger' not in docs['get']['tags']


def test_generate_doc_from_each_end_point():
    ExampleHandler.get.__doc__ = ENDPOINT_DOC
    routes = [
        tornado.web.url(r'/api/example', ExampleHandler, name='example'),
    ]

    docs = generate_doc_from_each_end_point(
        routes,
        api_base_url='/',
        description='',
        api_version='',
        title='',
        contact='',
        security_definitions=None
    )
    assert docs
