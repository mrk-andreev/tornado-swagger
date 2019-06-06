import functools

import tornado.ioloop
import tornado.options
import tornado.web

from tornado_swagger.setup import setup_swagger


class ExampleHandler(tornado.web.RequestHandler):
    @functools.lru_cache()
    def get(self, organization):
        """
        Description end-point

        ---
        tags:
        - Example
        summary: Create user
        description: This can only be done by the logged in user.
        operationId: examples.api.api.createUser
        produces:
        - application/json
        parameters:
        - in: request
          name: organization
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
                type: string
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
        self.write({
            'organization': organization
        })


class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r'/api/example/(.*)', ExampleHandler, name='example'),
    ]

    def __init__(self):
        settings = {
            'debug': True
        }

        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)


if __name__ == '__main__':
    tornado.options.define('port', default='8080', help='Port to listen on')
    tornado.options.parse_command_line()

    app = Application()
    app.listen(port=8080)

    tornado.ioloop.IOLoop.current().start()
