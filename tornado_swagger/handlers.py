from typing import Awaitable
from typing import Optional

import tornado.web


class TornadoHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass


class SwaggerHomeHandler(tornado.web.RequestHandler):
    SWAGGER_HOME_TEMPLATE = ''

    def get(self):
        self.write(self.SWAGGER_HOME_TEMPLATE)


class SwaggerDefHandler(tornado.web.RequestHandler):
    SWAGGER_DEF_CONTENT = ''

    def get(self):
        self.write(self.SWAGGER_DEF_CONTENT)
