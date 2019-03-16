import tornado.ioloop
import tornado.options
import tornado.web

from tornado_swagger.setup import setup_swagger


class PostsHandler(tornado.web.RequestHandler):
    def get(self):
        """
        ---
        tags:
        - Posts
        summary: List posts
        description: List all posts in feed
        produces:
        - application/json
        """
        self.write({
            'response': []
        })

    def post(self):
        """
        ---
        tags:
        - Posts
        summary: Add posts
        description: Add posts in feed
        produces:
        - application/json
        """
        self.write({
            'response': {
                'post_id': None
            }
        })


class PostsDetailsHandler(tornado.web.RequestHandler):
    def get(self, posts_id):
        """
        ---
        tags:
        - Posts
        summary: Get posts details
        description: posts full version
        produces:
        - application/json
        parameters:
        -   name: posts_id
            in: path
            description: ID of post to return
            required: true
            type: string
        """
        self.write({
            'response': {
                'id': posts_id,
                'title': '',
                'text': ''
            }
        })

    def patch(self, posts_id):
        """
        ---
        tags:
        - Posts
        summary: Edit posts
        description: Edit posts details
        produces:
        - application/json
        parameters:
        -   name: posts_id
            in: path
            description: ID of post to edit
            required: true
            type: string
        """
        self.write({
            'response': {
                'success': True
            }
        })

    def delete(self, posts_id):
        """
        ---
        tags:
        - Posts
        summary: Delete posts
        description: Remove posts from feed
        produces:
        - application/json
        parameters:
        -   name: posts_id
            in: path
            description: ID of post to delete
            required: true
            type: string
        """
        self.write({
            'response': {
                'success': True
            }
        })


class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r'/api/posts', PostsHandler),
        tornado.web.url(r'/api/posts/(\w+)', PostsDetailsHandler),
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
