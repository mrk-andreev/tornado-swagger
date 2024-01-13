"""Handlers"""
import tornado.web


class TornadoBaseHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes):
        pass


class SwaggerUiHandler(TornadoBaseHandler):
    SWAGGER_HOME_TEMPLATE = ""
    allow_cors: bool = False

    def get(self):
        self.write(self.SWAGGER_HOME_TEMPLATE)
        
    def options(self):
        if self.allow_cors:
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Headers", "Content-Type")
            self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")


class SwaggerSpecHandler(TornadoBaseHandler):
    SWAGGER_SPEC = ""
    allow_cors: bool = False

    def get(self):
        self.write(self.SWAGGER_SPEC)
        
    def options(self):
        if self.allow_cors:
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Headers", "Content-Type")
            self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
