import multiprocessing
import socket
import time
from contextlib import closing

import pytest
import tornado.httpclient
import tornado.ioloop

from examples.decorated_handlers import Application


SERVER_START_TIMEOUT = 3


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


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


def test_example_handler_returns_organization(server):
    client = tornado.httpclient.HTTPClient()
    organization = "acme"
    response = client.fetch(f"http://localhost:{server}/api/example/{organization}")
    assert response.code == 200
    assert f'"organization": "{organization}"' in response.body.decode()


def test_swagger_ui_renders(server):
    client = tornado.httpclient.HTTPClient()
    response = client.fetch(f"http://localhost:{server}/api/doc")
    assert "Swagger UI" in response.body.decode()


