import tornado.web


class TornadoHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes):
        pass


class SwaggerHomeHandler(TornadoHandler):
    SWAGGER_HOME_TEMPLATE = ''

    def get(self):
        self.write(self.SWAGGER_HOME_TEMPLATE)
