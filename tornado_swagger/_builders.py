import collections
import inspect
import json
import os
import re
import typing

import tornado.web
import yaml
from jinja2 import BaseLoader
from jinja2 import Environment

SWAGGER_TEMPLATE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'templates', 'swagger.yaml')
)
SWAGGER_DOC_SEPARATOR = '---'


def _extract_swagger_definition(endpoint_doc):
    endpoint_doc = endpoint_doc.splitlines()

    # Find Swagger start point in doc
    for i, doc_line in enumerate(endpoint_doc):
        if SWAGGER_DOC_SEPARATOR in doc_line:
            end_point_swagger_start = i + 1
            endpoint_doc = endpoint_doc[end_point_swagger_start:]
            break
    return '\n'.join(endpoint_doc)


def extract_swagger_docs(endpoint_doc):
    endpoint_doc = _extract_swagger_definition(endpoint_doc)

    # Build JSON YAML Obj
    try:
        end_point_swagger_doc = yaml.safe_load(endpoint_doc)
        if not isinstance(end_point_swagger_doc, dict):
            raise yaml.YAMLError()
    except yaml.YAMLError:
        end_point_swagger_doc = {
            'description': 'Swagger document could not be loaded from docstring',
            'tags': ['Invalid Swagger']
        }
    return end_point_swagger_doc


def _build_doc_from_func_doc(handler):
    out = {}

    for method in handler.SUPPORTED_METHODS:
        method = method.lower()
        doc = getattr(handler, method).__doc__

        if doc is not None and '---' in doc:
            out.update({
                method: extract_swagger_docs(doc)
            })

    return out


def _extract_parameters_names(handler, parameters_count):
    if parameters_count == 0:
        return []

    parameters = ['{?}' for _ in range(parameters_count)]

    for method in handler.SUPPORTED_METHODS:
        method_handler = getattr(handler, method.lower())
        for i, arg in enumerate(inspect.getfullargspec(method_handler).args[1:]):
            if set(arg) != {'_'}:
                parameters[i] = arg

    return parameters


def _format_handler_path(route):
    brackets_regex = re.compile(r'\(.*?\)')
    parameters = _extract_parameters_names(route.target, route.regex.groups)
    route_pattern = route.regex.pattern

    for i, entity in enumerate(brackets_regex.findall(route_pattern)):
        route_pattern = route_pattern.replace(entity, '{%s}' % parameters[i], 1)

    return route_pattern[:-1]


def nesteddict2yaml(d, indent=10, result=''):
    for key, value in d.items():
        result += ' ' * indent + str(key) + ':'
        if isinstance(value, dict):
            result = nesteddict2yaml(value, indent + 2, result + '\n')
        else:
            result += ' ' + str(value) + '\n'
    return result


def generate_doc_from_endpoints(routes: typing.List[tornado.web.URLSpec],
                                *,
                                api_base_url,
                                description,
                                api_version,
                                title,
                                contact,
                                schemes,
                                security_definitions):
    from tornado_swagger.model import swagger_models
    # Clean description
    _start_desc = 0
    for i, word in enumerate(description):
        if word != '\n':
            _start_desc = i
            break
    cleaned_description = '    '.join(description[_start_desc:].splitlines())

    # Load base Swagger template
    jinja2_env = Environment(loader=BaseLoader())
    jinja2_env.filters['nesteddict2yaml'] = nesteddict2yaml

    with open(SWAGGER_TEMPLATE, 'r') as f:
        swagger_base = (
            jinja2_env.from_string(f.read()).render(
                description=cleaned_description,
                version=api_version,
                title=title,
                contact=contact,
                base_path=api_base_url,
                security_definitions=security_definitions,
            )
        )

    # The Swagger OBJ
    swagger = yaml.safe_load(swagger_base)
    swagger['schemes'] = schemes
    swagger['paths'] = collections.defaultdict(dict)
    swagger['definitions'] = swagger_models

    for route in routes:
        swagger["paths"][_format_handler_path(route)].update(_build_doc_from_func_doc(route.target))

    return json.dumps(swagger)
