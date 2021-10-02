import tornado.ioloop
import tornado.options
import tornado.web
from tornado_http_auth import BasicAuthMixin

from tornado_swagger import _handlers
from app import Application

credentials = {"user1": "pass1"}


class SwaggerHomeHandlerSecure(BasicAuthMixin, _handlers.SwaggerUiHandler):
    def prepare(self):
        self.get_authenticated_user(
            check_credentials_func=credentials.get, realm="Protected"
        )


_handlers.SwaggerUiHandler = SwaggerHomeHandlerSecure

if __name__ == "__main__":
    tornado.options.define("port", default="8080", help="Port to listen on")
    tornado.options.parse_command_line()

    app = Application()
    app.listen(port=8081)

    tornado.ioloop.IOLoop.current().start()
