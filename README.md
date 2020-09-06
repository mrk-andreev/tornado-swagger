tornado-swagger
===============

[![Maintainability](https://api.codeclimate.com/v1/badges/d45717a5cfedeaef195a/maintainability)](https://codeclimate.com/github/mrk-andreev/tornado-swagger/maintainability)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/mrk-andreev/tornado-swagger.svg)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmrk-andreev%2Ftornado-swagger?ref=badge_shield)
![GitHub](https://img.shields.io/github/license/mrk-andreev/tornado-swagger.svg)


| PyPI                                        | Anaconda                                      |
|----------------------------------------------|----------------------------------------------|
| [![PyPI][pypi_image]][pypi_link] | [![Anaconda][anaconda_image]][anaconda_link] |


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

*tornado-swagger: Swagger API Documentation builder for tornado server. Inspired by [aiohttp-swagger](https://github.com/cr0hn/aiohttp-swagger) package (based on this package sources).*

Documentation |  https://github.com/mrk-andreev/tornado-swagger/wiki
------------- | -------------------------------------------------
Code | https://github.com/mrk-andreev/tornado-swagger
Issues | https://github.com/mrk-andreev/tornado-swagger/issues
Python version | Python 3.5 and above
Swagger Language Specification | https://swagger.io/specification/v2/

Installation
----------------------

    pip install -U tornado-swagger
    conda install -c mrk.andreev tornado-swagger 


What's tornado-swagger
----------------------

tornado-swagger is a plugin for tornado server that allow to document APIs using Swagger show the Swagger-ui console (default url /api/doc).

![](https://github.com/mrk-andreev/tornado-swagger/blob/master/docs/wiki__swagger_single_endpoint.png)

```python
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
        responses:
            200:
              description: list of posts
              schema:
                $ref: '#/definitions/PostModel'
        """
```

What's new?
-----------

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

## Version 1.2.1
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
