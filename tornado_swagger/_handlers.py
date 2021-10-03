import tornado.web


class TornadoBaseHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes):
        pass


class SwaggerUiHandler(TornadoBaseHandler):
    SWAGGER_HOME_TEMPLATE = ""

    def get(self):
        self.write(self.SWAGGER_HOME_TEMPLATE)


class SwaggerSpecHandler(TornadoBaseHandler):
    SWAGGER_SPEC = ""

    def get(self):
        self.write(self.SWAGGER_SPEC)
