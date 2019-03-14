import tornado.web


class SwaggerHomeHandler(tornado.web.RequestHandler):
    SWAGGER_HOME_TEMPLATE = ''

    def get(self):
        self.write(self.SWAGGER_HOME_TEMPLATE)


class SwaggerDefHandler(tornado.web.RequestHandler):
    SWAGGER_DEF_CONTENT = ''

    def get(self):
        self.write(self.SWAGGER_DEF_CONTENT)
