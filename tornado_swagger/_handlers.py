"""Handlers."""

import typing

import tornado.web


class TornadoBaseHandler(tornado.web.RequestHandler):
    allow_cors: bool = False
    cors_origin: str = "*"

    def data_received(self, chunk: bytes) -> None:
        # Streamed request bodies are not used by these handlers; the abstract
        # method from tornado.web.RequestHandler is overridden as a no-op.
        pass

    def set_cors_headers(self) -> None:
        if self.allow_cors:
            self.set_header("Access-Control-Allow-Origin", self.cors_origin)
            self.set_header("Access-Control-Allow-Headers", "Content-Type")
            self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            if self.cors_origin != "*":
                # A response tied to a specific origin must not be cached and
                # reused for a different origin.
                self.set_header("Vary", "Origin")


class SwaggerUiHandler(TornadoBaseHandler):
    SWAGGER_HOME_TEMPLATE = ""

    def get(self) -> None:
        self.set_cors_headers()
        self.write(self.SWAGGER_HOME_TEMPLATE)

    def options(self) -> None:
        self.set_cors_headers()


class SwaggerSpecHandler(TornadoBaseHandler):
    SWAGGER_SPEC: typing.ClassVar[typing.Any] = ""

    def get(self) -> None:
        self.set_cors_headers()
        self.write(self.SWAGGER_SPEC)

    def options(self) -> None:
        self.set_cors_headers()
