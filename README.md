tornado-swagger
===============

[![Maintainability](https://api.codeclimate.com/v1/badges/d45717a5cfedeaef195a/maintainability)](https://codeclimate.com/github/mrk-andreev/tornado-swagger/maintainability)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/mrk-andreev/tornado-swagger.svg)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger?ref=badge_shield)
![GitHub](https://img.shields.io/github/license/mrk-andreev/tornado-swagger.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

| PyPI                                        |
|----------------------------------------------|
| [![PyPI][pypi_image]][pypi_link] |

[pypi_link]: https://pypi.org/project/tornado-swagger/

[pypi_image]: https://img.shields.io/pypi/v/tornado-swagger.svg

[anaconda_link]: https://anaconda.org/mrk.andreev/tornado-swagger

[anaconda_image]: https://anaconda.org/mrk.andreev/tornado-swagger/badges/version.svg

| Linux                                        | Windows                                      |
|----------------------------------------------|----------------------------------------------|
| [![TravisCI][travisci_image]][travisci_link] | [![AppVeyor][appveyor_image]][appveyor_link] |

[travisci_link]: https://travis-ci.org/mrk-andreev/tornado-swagger

[travisci_image]: https://travis-ci.org/mrk-andreev/tornado-swagger.svg?branch=master

[appveyor_link]: https://ci.appveyor.com/project/mrk-andreev/tornado-swagger/branch/master

[appveyor_image]: https://img.shields.io/appveyor/ci/mrk-andreev/tornado-swagger/master.svg

*tornado-swagger: Swagger API Documentation builder for tornado server. Inspired
by [aiohttp-swagger](https://github.com/cr0hn/aiohttp-swagger) package (based on this package sources).*

Documentation |  https://github.com/mrk-andreev/tornado-swagger/wiki
------------- | -------------------------------------------------
Code | https://github.com/mrk-andreev/tornado-swagger
Issues | https://github.com/mrk-andreev/tornado-swagger/issues
Python version | Python 3.6, 3.7, 3.8, nightly
Swagger Language Specification | https://swagger.io/specification/v2/

Installation
----------------------

    pip install -U tornado-swagger

What's tornado-swagger
----------------------

tornado-swagger is a plugin for tornado server that allow to document APIs using Swagger show the Swagger-ui console (
default url /api/doc).

![](https://github.com/mrk-andreev/tornado-swagger/blob/master/docs/wiki__swagger_single_endpoint.png)

```python
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

```

What's new?
-----------

### Version 1.4.0

- Add experimental openapi support (api_definition_version = API_OPENAPI_3; examples/model_and_param_declaration_openapi3.py) 

### Version 1.3.0

- Add swagger parameter ref (@register_swagger_parameter). Thanks to [@Weltraumpenner](https://github.com/Weltraumpenner)

### Version 1.2.11

- Fix link to spec swagger.json [issue](https://github.com/mrk-andreev/tornado-swagger/issues/47).

### Version 1.2.10

- Update PyYAML version to 5.4 (Fix for CVE-2020-14343)

### Version 1.2.9

- Fix handler args name parsing (`examples/args_recognize.py`). Thanks to [@reubinoff]

### Version 1.2.8

- Add `security` to setup. Thanks to [@daominwang](https://github.com/daominwang)
- Add black code formatter
- Update swagger-ui library to 3.37.2
- Add integrity attribute to script / link tags
- Remove Python 3.5 support

### Version 1.2.7

- Add display_models param to setup (`defaultModelsExpandDepth`). Thanks to [@Sloknatos](https://github.com/Sloknatos)
- Fix swagger-ui bundle [CVE-2019-17495](https://github.com/mrk-andreev/tornado-swagger/issues/35)
- Specify supported python versions: 3.5, 3.6, 3.7, 3.8, nightly

### Version 1.2.6

- Fix issue with `StaticFileHandler` (https://github.com/mrk-andreev/tornado-swagger/pull/28)

### Version 1.2.5

- Update dependencies
    - `PyYAML==5.3.1` fix vulnerabilities
    - `pytest==6.0.1`, `pytest-flake8==1.0.6` fix test crash

### Version 1.2.4

- Fix "index out of range issue for StaticFileHandler" (https://github.com/mrk-andreev/tornado-swagger/issues/23)

### Version 1.2.3

- Fix `\t` bug in Windows (https://github.com/mrk-andreev/tornado-swagger/issues/21)

### Version 1.2.1

- Support wrapped methods
- Remove jinja2 from deps

### Version 1.2.0

- Replace local js/css to cdn
- Remove static files serving

### Version 1.1.0

- Swagger model definition
- Parameters filling in route path
- Schema definition
- `export_swagger(routes)` as public function
- Update frontend

### Version 1.0.0

- First version released

## License

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger?ref=badge_large)
