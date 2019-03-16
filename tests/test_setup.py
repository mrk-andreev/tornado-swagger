import multiprocessing
import socket
import time
from contextlib import closing

import pytest
import tornado.httpclient
import tornado.ioloop
import tornado.web

from tornado_swagger.setup import export_swagger
from tornado_swagger.setup import setup_swagger

SERVER_START_TIMEOUT = 3

SWAGGER_URL = '/api/doc'


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


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
        """
        self.write({})


class Application(tornado.web.Application):
    routes = [
        tornado.web.url(r'/api/example', ExampleHandler)
    ]

    def __init__(self):
        setup_swagger(
            self.routes,
            swagger_url=SWAGGER_URL,
        )
        super(Application, self).__init__(self.routes)


def test_export_swagger():
    assert export_swagger(Application.routes)


def server_holder(port):
    app = Application()
    app.listen(port=port)
    tornado.ioloop.IOLoop.current().start()


@pytest.fixture()
def server():
    port = find_free_port()

    server_holder_process = multiprocessing.Process(target=server_holder, args=(port,))
    server_holder_process.start()
    time.sleep(SERVER_START_TIMEOUT)
    yield port
    server_holder_process.terminate()
    server_holder_process.join()


def test_swagger_setup_integration(server):
    client = tornado.httpclient.HTTPClient()
    response = client.fetch('http://localhost:{0}{1}'.format(server, SWAGGER_URL))
    assert 'Swagger UI' in response.body.decode()


@pytest.fixture()
def swaggered_app():
    return Application()


def test_swagger_schema_endpoints(swaggered_app):
    router_rules = [
        rule.regex.pattern
        for rule in swaggered_app.wildcard_router.rules
    ]

    assert any([
        rule[:-1].endswith('/swagger.json')
        for rule in router_rules
    ])
