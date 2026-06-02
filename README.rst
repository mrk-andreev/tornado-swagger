tornado-swagger
===============

|PyPI| |GitHub| |Code style: black| |Maintainability|

tornado-swagger builds Swagger/OpenAPI documentation for Tornado
applications from YAML blocks in request-handler docstrings. It can inject a
Swagger UI endpoint into your route list and can also export the generated
schema as a Python dictionary.

The default output is Swagger 2.0. Experimental OpenAPI 3 output is available
with ``api_definition_version=API_OPENAPI_3`` or
``api_definition_version=API_OPENAPI_3_1``.

Links
-----

- Documentation: https://github.com/mrk-andreev/tornado-swagger/wiki
- Source code: https://github.com/mrk-andreev/tornado-swagger
- Issues: https://github.com/mrk-andreev/tornado-swagger/issues
- PyPI: https://pypi.org/project/tornado-swagger/
- Swagger 2.0 specification: https://swagger.io/specification/v2/
- OpenAPI specification: https://swagger.io/specification/

Installation
------------

::

   pip install -U tornado-swagger

Requirements
------------

- Python 3.7 through 3.14
- Tornado 5.0 or newer
- PyYAML 5.4 or newer

Standards compatibility
-----------------------

tornado-swagger generates documents compatible with Swagger 2.0, OpenAPI
3.0.3, and OpenAPI 3.1.0. Compatibility tests validate generated documents
against the corresponding standards. Valid operation, schema, parameter,
response, request body, and security YAML blocks are passed through into the
generated document for the selected standard.

Quick start
-----------

Add YAML documentation to Tornado handler method docstrings after a ``---``
separator, then call ``setup_swagger`` before constructing the application.

.. code:: python

   import tornado.ioloop
   import tornado.web

   from tornado_swagger.setup import setup_swagger


   class ExampleHandler(tornado.web.RequestHandler):
       def get(self):
           """
           ---
           tags:
           - Example
           summary: Get an example response
           produces:
           - application/json
           responses:
               200:
                 description: Successful response
           """
           self.write({"ok": True})


   routes = [
       tornado.web.url(r"/api/example", ExampleHandler),
   ]

   setup_swagger(
       routes,
       swagger_url="/api/doc",
       api_base_url="/",
       title="Example API",
       api_version="1.0.0",
   )

   app = tornado.web.Application(routes)
   app.listen(8080)
   tornado.ioloop.IOLoop.current().start()

Open http://localhost:8080/api/doc to view Swagger UI. The generated schema is
served at http://localhost:8080/api/doc/swagger.json.

Models and Parameters
---------------------

Reusable definitions can be registered with decorators. For Swagger 2.0, refer
to models with ``#/definitions/...`` and parameters with ``#/parameters/...``.

.. code:: python

   import tornado.web
   from tornado_swagger.model import register_swagger_model
   from tornado_swagger.parameter import register_swagger_parameter


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
           -   $ref: '#/parameters/PostId'
           responses:
               200:
                 description: list of posts
                 schema:
                   $ref: '#/definitions/PostModel'
           """


   @register_swagger_parameter
   class PostId:
       """
       ---
       name: posts_id
       in: path
       description: ID of post
       required: true
       type: string
       """


   @register_swagger_model
   class PostModel:
       """
       ---
       type: object
       description: Post model representation
       properties:
           id:
               type: integer
               format: int64
           title:
               type: string
           text:
               type: string
           is_visible:
               type: boolean
               default: true
       """

OpenAPI 3
---------

OpenAPI 3 support is available by passing ``API_OPENAPI_3`` or
``API_OPENAPI_3_1`` to ``setup_swagger`` or ``export_swagger``.
``API_OPENAPI_3`` emits OpenAPI 3.0.3, while ``API_OPENAPI_3_1`` emits
OpenAPI 3.1.0. OpenAPI 3 references use ``#/components/schemas/...`` and
``#/components/parameters/...``. OpenAPI 3 security schemes can be passed with
``security_schemes``.

.. code:: python

   from tornado_swagger.const import API_OPENAPI_3
   from tornado_swagger.setup import setup_swagger


   setup_swagger(
       routes,
       api_definition_version=API_OPENAPI_3,
   )

JWT bearer authentication requires OpenAPI 3 because Swagger 2.0 does not
support ``type: http`` security schemes.

.. code:: python

   from tornado_swagger.const import API_OPENAPI_3
   from tornado_swagger.setup import setup_swagger


   setup_swagger(
       routes,
       api_definition_version=API_OPENAPI_3,
       security_schemes={
           "BearerAuth": {
               "type": "http",
               "scheme": "bearer",
               "bearerFormat": "JWT",
           },
       },
       security=[{"BearerAuth": []}],
   )

Configuration
-------------

``setup_swagger(routes, **kwargs)`` inserts Swagger UI and schema routes at the
front of the supplied route list.

Supported options:

- ``swagger_url``: UI URL prefix. Defaults to ``/api/doc``.
- ``api_base_url``: API base path in the generated schema. Defaults to ``/``.
  Swagger 2 emits this as ``basePath``; OpenAPI 3 emits it as
  ``servers[0].url``.
- ``description``: API description text.
- ``api_version``: API version string.
- ``title``: API title.
- ``contact``: Contact name included in the schema.
- ``schemes``: Swagger 2 scheme list, for example ``["https"]``.
- ``security_definitions``: Swagger 2 security definitions to include in the
  schema. For backwards compatibility, OpenAPI 3 also accepts this option and
  emits it as ``components.securitySchemes``.
- ``security_schemes``: OpenAPI 3 security schemes to include under
  ``components.securitySchemes``.
- ``security``: Global security requirements.
- ``display_models``: Show or hide the Swagger UI models panel. Defaults to
  ``True``.
- ``api_definition_version``: ``API_SWAGGER_2`` by default, or
  ``API_OPENAPI_3`` / ``API_OPENAPI_3_1``.
- ``allow_cors``: Add CORS headers to Swagger UI and ``swagger.json``
  responses (both the ``GET`` and preflight ``OPTIONS`` responses). Defaults
  to ``False``.
- ``cors_origin``: Value for the ``Access-Control-Allow-Origin`` header when
  ``allow_cors`` is enabled. Defaults to ``"*"``. Set a specific origin (e.g.
  ``"https://example.com"``) to restrict cross-origin access; a ``Vary:
  Origin`` header is then added automatically.

To generate the schema without installing UI routes, use ``export_swagger``:

.. code:: python

   from tornado_swagger.setup import export_swagger


   schema = export_swagger(routes, title="Example API", api_version="1.0.0")

Examples
--------

Runnable examples are available in the ``examples`` directory:

- ``examples/simple_server.py``: minimal Swagger UI setup.
- ``examples/model_and_param_declaration.py``: reusable Swagger 2 models and
  parameters.
- ``examples/model_and_param_declaration_openapi3.py``: OpenAPI 3 output.
- ``examples/auth_server.py`` and ``examples/under_security/app.py``:
  security-related examples.
- ``examples/decorated_handlers.py``: documented handlers with decorators.
- ``examples/args_recognize.py``: route argument name recognition.

Development
-----------

Install runtime and development dependencies, then run tests and linters with
the Makefile targets:

::

   pip install -r requirements-dev.txt
   make test
   make lint

Additional targets:

- ``make format``: run Ruff fixes and Black formatting.
- ``make test-matrix``: run the tox matrix.
- ``make test-in-docker``: run the Docker-based Python version matrix.

The tox matrix covers Tornado 5.0, 6.0, and 6.5.6 on older supported Python
versions, and Tornado 6.5.6 on Python 3.11, 3.12, 3.13, and 3.14.

What’s new?
-----------

Version 1.6.0
~~~~~~~~~~~~~

- Add OpenAPI 3.1 support and standards compatibility tests for Swagger 2.0,
  OpenAPI 3.0.3, and OpenAPI 3.1.0.
- Fix ``allow_cors`` so CORS headers are also sent on the ``GET`` responses
  (previously only the preflight ``OPTIONS`` response carried them, so
  cross-origin spec fetches still failed in browsers).
- Add ``cors_origin`` option to configure ``Access-Control-Allow-Origin``
  instead of always using ``*``.
- Fix OpenAPI 3 server metadata generation and security scheme placement.
- Add OpenAPI 3 JWT bearer authentication support.
- Fix executable Swagger example endpoint and installation issue.
- Add tox, Ruff linting, mypy checks, and broader test coverage.
- Improve README and example documentation.

Version 1.5.0
~~~~~~~~~~~~~

- Add ``allow_cors`` option
  (`pull request #73 <https://github.com/mrk-andreev/tornado-swagger/pull/73>`__).
  Thanks to `@MarkParker5 <https://github.com/MarkParker5>`__.


Version 1.4.5
~~~~~~~~~~~~~

- Specify supported python versions: 3.7, 3.8, 3.9, 3.10, 3.11 and nightly
- Remove ``flake8-eradicate``, ``flake8-isort`` from dev deps
- Create ``make test-in-docker`` for test application across python versions


Version 1.4.4
~~~~~~~~~~~~~

- Fix path parsing with groups (skip + warning)
  (`issue #58 <https://github.com/mrk-andreev/tornado-swagger/issues/58>`__)

Version 1.4.3
~~~~~~~~~~~~~

- Update swagger-ui lib from ``3.37.2`` to ``4.13.2``
  (`issue #62 <https://github.com/mrk-andreev/tornado-swagger/issues/62>`__,
  `issue #61 <https://github.com/mrk-andreev/tornado-swagger/issues/61>`__)


Version 1.4.2
~~~~~~~~~~~~~

- Update dev requirements (fix broken packages)
- Update PyYAML from ``PyYAML==5.4`` to ``PyYAML>=5.4``
  (`issue #59 <https://github.com/mrk-andreev/tornado-swagger/issues/59>`__)
- Specify encoding in ``tornado_swagger/setup.py::open``

Version 1.4.1
~~~~~~~~~~~~~

- Fix pypi build (migrate README from md to rst)

Version 1.4.0
~~~~~~~~~~~~~

-  Add experimental openapi support (api_definition_version =
   API_OPENAPI_3; examples/model_and_param_declaration_openapi3.py)

Version 1.3.0
~~~~~~~~~~~~~

-  Add swagger parameter ref (@register_swagger_parameter). Thanks to
   `@Weltraumpenner <https://github.com/Weltraumpenner>`__

Version 1.2.11
~~~~~~~~~~~~~~

-  Fix link to spec swagger.json
   `issue <https://github.com/mrk-andreev/tornado-swagger/issues/47>`__.

Version 1.2.10
~~~~~~~~~~~~~~

-  Update PyYAML version to 5.4 (Fix for CVE-2020-14343)

Version 1.2.9
~~~~~~~~~~~~~

-  Fix handler args name parsing (``examples/args_recognize.py``).
   Thanks to @reubinoff

Version 1.2.8
~~~~~~~~~~~~~

-  Add ``security`` to setup. Thanks to
   `@daominwang <https://github.com/daominwang>`__
-  Add black code formatter
-  Update swagger-ui library to 3.37.2
-  Add integrity attribute to script / link tags
-  Remove Python 3.5 support

Version 1.2.7
~~~~~~~~~~~~~

-  Add display_models param to setup (``defaultModelsExpandDepth``).
   Thanks to `@Sloknatos <https://github.com/Sloknatos>`__
-  Fix swagger-ui bundle
   `CVE-2019-17495 <https://github.com/mrk-andreev/tornado-swagger/issues/35>`__
-  Specify supported python versions: 3.5, 3.6, 3.7, 3.8, nightly

Version 1.2.6
~~~~~~~~~~~~~

-  Fix issue with ``StaticFileHandler``
   (https://github.com/mrk-andreev/tornado-swagger/pull/28)

Version 1.2.5
~~~~~~~~~~~~~

-  Update dependencies

   -  ``PyYAML==5.3.1`` fix vulnerabilities
   -  ``pytest==6.0.1``, ``pytest-flake8==1.0.6`` fix test crash

Version 1.2.4
~~~~~~~~~~~~~

-  Fix “index out of range issue for StaticFileHandler”
   (https://github.com/mrk-andreev/tornado-swagger/issues/23)

Version 1.2.3
~~~~~~~~~~~~~

-  Fix ``\t`` bug in Windows
   (https://github.com/mrk-andreev/tornado-swagger/issues/21)

Version 1.2.1
~~~~~~~~~~~~~

-  Support wrapped methods
-  Remove jinja2 from deps

Version 1.2.0
~~~~~~~~~~~~~

-  Replace local js/css to cdn
-  Remove static files serving

Version 1.1.0
~~~~~~~~~~~~~

-  Swagger model definition
-  Parameters filling in route path
-  Schema definition
-  ``export_swagger(routes)`` as public function
-  Update frontend

Version 1.0.0
~~~~~~~~~~~~~

-  First version released

License
-------

|FOSSA Status|

.. |Maintainability| image:: https://api.codeclimate.com/v1/badges/d45717a5cfedeaef195a/maintainability
   :target: https://codeclimate.com/github/mrk-andreev/tornado-swagger/maintainability
.. |FOSSA Status| image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger.svg?type=shield
   :target: https://app.fossa.io/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger?ref=badge_shield
.. |GitHub| image:: https://img.shields.io/github/license/mrk-andreev/tornado-swagger.svg
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |PyPI| image:: https://img.shields.io/pypi/v/tornado-swagger.svg
   :target: https://pypi.org/project/tornado-swagger/
