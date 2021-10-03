import tornado.ioloop
import tornado.options
import tornado.web

from tornado_swagger.setup import setup_swagger


class AuthHandler(tornado.web.RequestHandler):
    def get(self):
        """
        ---
        tags:
        - Auth
        summary: Get user auth key
        description: Get user auth key
        produces:
        - application/json
        """
        self.finish("test user auth")

    def post(self):
        """
        ---
        tags:
        - Auth
        summary: Check user auth
        description: check user auth
        produces:
        - application/json
        responses:
            200:
              description: the auth key return
        """
        x_api_key = self.request.headers.get("X-API-Key")
        self.finish("the x-api-key request get is %s" % x_api_key)


class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/api/auth", AuthHandler),
    ]

    def __init__(self):
        settings = {"debug": True}

        setup_swagger(
            self._routes,
            swagger_url="/doc",
            api_base_url="/",
            description="",
            api_version="1.0.0",
            title="Journal API",
            contact="name@domain",
            security_definitions={"ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
            security=[{"ApiKeyAuth": []}],
        )
        super(Application, self).__init__(self._routes, **settings)


if __name__ == "__main__":
    tornado.options.define("port", default="8080", help="Port to listen on")
    tornado.options.parse_command_line()

    app = Application()
    app.listen(port=8080)

    tornado.ioloop.IOLoop.current().start()
