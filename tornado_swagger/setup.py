import os
import typing

import tornado.web

from tornado_swagger.handlers import SwaggerDefHandler
from tornado_swagger.handlers import SwaggerHomeHandler
from tornado_swagger.helpers.builders import generate_doc_from_each_end_point

STATIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'swagger_ui'))


def setup_swagger(routes: typing.List[tornado.web.URLSpec],
                  *,
                  swagger_url: str = '/api/doc',
                  api_base_url: str = '/',
                  description: str = 'Swagger API definition',
                  api_version: str = '1.0.0',
                  title: str = 'Swagger API',
                  contact: str = '',
                  security_definitions: dict = None
                  ):
    swagger_info = generate_doc_from_each_end_point(
        routes, api_base_url=api_base_url, description=description,
        api_version=api_version, title=title, contact=contact,
        security_definitions=security_definitions,
    )

    _swagger_url = ('/{}'.format(swagger_url)
                    if not swagger_url.startswith('/')
                    else swagger_url)
    _base_swagger_url = _swagger_url.rstrip('/')
    _swagger_def_url = '{}/swagger.json'.format(_base_swagger_url)
    statics_path = '{}/swagger_static'.format(_base_swagger_url)

    routes += [
        tornado.web.url(_swagger_url, SwaggerHomeHandler),
        tornado.web.url('{}/'.format(_base_swagger_url), SwaggerHomeHandler),
        tornado.web.url(_swagger_def_url, SwaggerDefHandler),
        tornado.web.url(statics_path + '/(.*)', tornado.web.StaticFileHandler, {
            'path': STATIC_PATH
        })
    ]

    SwaggerDefHandler.SWAGGER_DEF_CONTENT = swagger_info
    with open(os.path.join(STATIC_PATH, 'index.html'), 'r') as f:
        SwaggerHomeHandler.SWAGGER_HOME_TEMPLATE = (
            f.read().replace(
                '##SWAGGER_CONFIG##', '{}{}'.format(api_base_url.lstrip('/'), _swagger_def_url)
            ).replace(
                '##STATIC_PATH##',
                '{}{}'.format(api_base_url.lstrip('/'), statics_path)
            )
        )
