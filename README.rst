tornado-swagger
===============

|Maintainability| |Snyk Vulnerabilities for GitHub Repo| |FOSSA Status|
|GitHub| |Code style: black|

+--------+
| PyPI   |
+========+
| |PyPI| |
+--------+

+-----------------------------------+-----------------------------------+
| Linux                             | Windows                           |
+===================================+===================================+
| |TravisCI|                        | |AppVeyor|                        |
+-----------------------------------+-----------------------------------+

*tornado-swagger: Swagger API Documentation builder for tornado server.
Inspired
by*\ `aiohttp-swagger <https://github.com/cr0hn/aiohttp-swagger>`__\ *package
(based on this package sources).*

+--------------------------------+-------------------------------------------------------+
| Documentation                  | https://github.com/mrk-andreev/tornado-swagger/wiki   |
+--------------------------------+-------------------------------------------------------+
| Code                           | https://github.com/mrk-andreev/tornado-swagger        |
+--------------------------------+-------------------------------------------------------+
| Issues                         | https://github.com/mrk-andreev/tornado-swagger/issues |
+--------------------------------+-------------------------------------------------------+
| Python version                 |      Python 3.7, 3.8, 3.9, 3.10, 3.11 nightly         |
+--------------------------------+-------------------------------------------------------+
| Swagger Language Specification | https://swagger.io/specification/v2/                  |
+--------------------------------+-------------------------------------------------------+

Installation
------------

::

   pip install -U tornado-swagger

What’s tornado-swagger
----------------------

tornado-swagger is a plugin for tornado server that allow to document
APIs using Swagger show the Swagger-ui console ( default url /api/doc).

|image8|

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

What’s new?
-----------

Version 1.5.0
~~~~~~~~~~~~~

- Add allow_cors option [pull-73](https://github.com/mrk-andreev/tornado-swagger/pull/73) Thanks to
   [@MarkParker5](https://github.com/MarkParker5)


Version 1.4.5
~~~~~~~~~~~~~

- Specify supported python versions: 3.7, 3.8, 3.9, 3.10, 3.11 and nightly
- Remove `flake8-eradicate`, `flake8-isort` from dev deps
- Create `make test-in-docker` for test application across python versions


Version 1.4.4
~~~~~~~~~~~~~

- Fix path parsing with groups (skip + warning) [issue-58](https://github.com/mrk-andreev/tornado-swagger/issues/58)

Version 1.4.3
~~~~~~~~~~~~~

- Update swagger-ui lib from `3.37.2` to `4.13.2`  [issue-62](https://github.com/mrk-andreev/tornado-swagger/issues/62) [issue-61](https://github.com/mrk-andreev/tornado-swagger/issues/61)


Version 1.4.2
~~~~~~~~~~~~~

- Update dev requirements (fix broken packages)
- Update PyYAML from `PyYAML==5.4` to `PyYAML>=5.4` [issue-59](https://github.com/mrk-andreev/tornado-swagger/issues/59)
- Specify encoding in `tornado_swagger/setup.py::open`

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
   [@Weltraumpenner](https://github.com/Weltraumpenner)

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
   Thanks to [@reubinoff]

Version 1.2.8
~~~~~~~~~~~~~

-  Add ``security`` to setup. Thanks to
   [@daominwang](https://github.com/daominwang)
-  Add black code formatter
-  Update swagger-ui library to 3.37.2
-  Add integrity attribute to script / link tags
-  Remove Python 3.5 support

Version 1.2.7
~~~~~~~~~~~~~

-  Add display_models param to setup (``defaultModelsExpandDepth``).
   Thanks to [@Sloknatos](https://github.com/Sloknatos)
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
.. |Snyk Vulnerabilities for GitHub Repo| image:: https://img.shields.io/snyk/vulnerabilities/github/mrk-andreev/tornado-swagger.svg
.. |FOSSA Status| image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger.svg?type=shield
   :target: https://app.fossa.io/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger?ref=badge_shield
.. |GitHub| image:: https://img.shields.io/github/license/mrk-andreev/tornado-swagger.svg
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |PyPI| image:: https://img.shields.io/pypi/v/tornado-swagger.svg
   :target: https://pypi.org/project/tornado-swagger/
.. |TravisCI| image:: https://travis-ci.org/mrk-andreev/tornado-swagger.svg?branch=master
   :target: https://travis-ci.org/mrk-andreev/tornado-swagger
.. |AppVeyor| image:: https://img.shields.io/appveyor/ci/mrk-andreev/tornado-swagger/master.svg
   :target: https://ci.appveyor.com/project/mrk-andreev/tornado-swagger/branch/master
.. |image8| image:: https://github.com/mrk-andreev/tornado-swagger/blob/master/docs/wiki__swagger_single_endpoint.png
.. |FOSSA Status Large| image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger.svg?type=large
   :target: https://app.fossa.io/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger?ref=badge_large
