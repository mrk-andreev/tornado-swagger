import collections
import json
import os
import typing

import tornado.web
import yaml
from jinja2 import BaseLoader
from jinja2 import Environment

SWAGGER_TEMPLATE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'templates')
)


def _extract_swagger_docs(endpoint_doc, method):
    # Find Swagger start point in doc
    end_point_swagger_start = 0
    for i, doc_line in enumerate(endpoint_doc):
        if "---" in doc_line:
            end_point_swagger_start = i + 1
            break

    # Build JSON YAML Obj
    try:
        end_point_swagger_doc = (
            yaml.safe_load("\n".join(endpoint_doc[end_point_swagger_start:]))
        )
    except yaml.YAMLError:
        end_point_swagger_doc = {
            "description": "⚠ Swagger document could not be loaded "
                           "from docstring ⚠",
            "tags": ["Invalid Swagger"]
        }
    return {
        method: end_point_swagger_doc
    }


def _build_doc_from_func_doc(handler):
    out = {}

    for method in handler.SUPPORTED_METHODS:
        method = method.lower()
        doc = getattr(handler, method).__doc__

        if doc is not None and '---' in doc:
            end_point_doc = doc.splitlines()
            out.update(_extract_swagger_docs(end_point_doc, method=method))

    return out


def generate_doc_from_each_end_point(routes: typing.List[tornado.web.URLSpec],
                                     *,
                                     api_base_url,
                                     description,
                                     api_version,
                                     title,
                                     contact,
                                     security_definitions):
    # Clean description
    _start_desc = 0
    for i, word in enumerate(description):
        if word != '\n':
            _start_desc = i
            break
    cleaned_description = '    '.join(description[_start_desc:].splitlines())

    def nesteddict2yaml(d, indent=10, result=''):
        for key, value in d.items():
            result += ' ' * indent + str(key) + ':'
            if isinstance(value, dict):
                result = nesteddict2yaml(value, indent + 2, result + '\n')
            else:
                result += ' ' + str(value) + '\n'
        return result

    # Load base Swagger template
    jinja2_env = Environment(loader=BaseLoader())
    jinja2_env.filters['nesteddict2yaml'] = nesteddict2yaml

    with open(os.path.join(SWAGGER_TEMPLATE, 'swagger.yaml'), 'r') as f:
        swagger_base = (
            jinja2_env.from_string(f.read()).render(
                description=cleaned_description,
                version=api_version,
                title=title,
                contact=contact,
                base_path=api_base_url,
                security_definitions=security_definitions)
        )

    # The Swagger OBJ
    swagger = yaml.safe_load(swagger_base)
    swagger['paths'] = collections.defaultdict(dict)

    for route in routes:
        swagger["paths"][route.regex.pattern[:-1]].update(_build_doc_from_func_doc(route.target))

    return json.dumps(swagger)
