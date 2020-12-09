import tornado.web


class ExampleHandler(tornado.web.RequestHandler):
    def get(self):
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
        self.write({})


class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/api/example", ExampleHandler, name="example"),
    ]

    def __init__(self):
        settings = {"debug": True}
        from tornado_swagger.setup import setup_swagger

        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)
