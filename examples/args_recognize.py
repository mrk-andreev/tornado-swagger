"""Args recognize"""
import tornado.ioloop
import tornado.options
import tornado.web

from tornado_swagger.setup import setup_swagger


class ExampleHandler(tornado.web.RequestHandler):
    def get(self, arg_1):
        """
        ---
           tags:
           - Posts
           summary: Get posts details
           description: posts full version
           produces:
           - application/json
           parameters:
           -   name: arg_1
               in: path
               description: arg 1
               required: true
               type: string
        """
        self.write({"value": arg_1})

    def post(self, arg_2):
        """
        ---
            tags:
            - Posts
            summary: Get posts details
            description: posts full version
            produces:
            - application/json
            parameters:
            -   name: arg_2
                in: path
                description: arg 2
                required: true
                type: string
        """
        self.write({"value": arg_2})


class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/api/example/(\w+)", ExampleHandler, name="example"),
    ]

    def __init__(self):
        settings = {"debug": True}

        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)


if __name__ == "__main__":
    tornado.options.define("port", default="8080", help="Port to listen on")
    tornado.options.parse_command_line()

    app = Application()
    app.listen(port=8080)

    tornado.ioloop.IOLoop.current().start()
