# pylint: disable=R0401,C0415
import abc
import collections
import inspect
import os
import re
import typing

import tornado.web
import yaml

from tornado_swagger.const import API_OPENAPI_3, API_SWAGGER_2

SWAGGER_TEMPLATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates", "swagger.yaml"))
SWAGGER_DOC_SEPARATOR = "---"


def _extract_swagger_definition(endpoint_doc):
    """Extract swagger definition after SWAGGER_DOC_SEPARATOR"""
    endpoint_doc = endpoint_doc.splitlines()

    for i, doc_line in enumerate(endpoint_doc):
        if SWAGGER_DOC_SEPARATOR in doc_line:
            end_point_swagger_start = i + 1
            endpoint_doc = endpoint_doc[end_point_swagger_start:]
            break
    return "\n".join(endpoint_doc)


def build_swagger_docs(endpoint_doc):
    """Build swagger doc based on endpoint docstring"""
    endpoint_doc = _extract_swagger_definition(endpoint_doc)

    # Build JSON YAML Obj
    try:
        endpoint_doc = endpoint_doc.replace("\t", "    ")  # fix windows tabs bug
        end_point_swagger_doc = yaml.safe_load(endpoint_doc)
        if not isinstance(end_point_swagger_doc, dict):
            raise yaml.YAMLError()
        return end_point_swagger_doc
    except yaml.YAMLError:
        return {
            "description": "Swagger document could not be loaded from docstring",
            "tags": ["Invalid Swagger"],
        }


def _try_extract_doc(func):
    """Extract docstring from origin function removing decorators"""
    return inspect.unwrap(func).__doc__


def _build_doc_from_func_doc(handler):
    out = {}

    for method in handler.SUPPORTED_METHODS:
        method = method.lower()
        doc = _try_extract_doc(getattr(handler, method))

        if doc is not None and "---" in doc:
            out.update({method: build_swagger_docs(doc)})

    return out


def _try_extract_args(method_handler):
    """Extract method args from origin function removing decorators"""
    return inspect.getfullargspec(inspect.unwrap(method_handler)).args[1:]


def _extract_parameters_names(handler, parameters_count, method):
    """Extract parameters names from handler"""
    if parameters_count == 0:
        return []

    parameters = ["{?}" for _ in range(parameters_count)]

    method_handler = getattr(handler, method.lower())
    args = _try_extract_args(method_handler)

    for i, arg in enumerate(args):
        if set(arg) != {"_"} and i < len(parameters):
            parameters[i] = arg

    return parameters


def _format_handler_path(route, method):
    brackets_regex = re.compile(r"\(.*?\)")
    parameters = _extract_parameters_names(route.target, route.regex.groups, method)
    route_pattern = route.regex.pattern

    for i, entity in enumerate(brackets_regex.findall(route_pattern)):
        route_pattern = route_pattern.replace(entity, "{%s}" % parameters[i], 1)

    return route_pattern[:-1]


def nesteddict2yaml(d, indent=10, result=""):
    for key, value in d.items():
        result += " " * indent + str(key) + ":"
        if isinstance(value, dict):
            result = nesteddict2yaml(value, indent + 2, result + "\n")
        else:
            result += " " + str(value) + "\n"
    return result


def _clean_description(description):
    """Remove empty space from description begin"""
    _start_desc = 0
    for i, word in enumerate(description):
        if word != "\n":
            _start_desc = i
            break
    return "    ".join(description[_start_desc:].splitlines())


def _extract_paths(routes):
    paths = collections.defaultdict(dict)

    for route in routes:
        for method_name, method_description in _build_doc_from_func_doc(route.target).items():
            paths[_format_handler_path(route, method_name)].update({method_name: method_description})

    return paths


class BaseDocBuilder(abc.ABC):
    """Doc builder"""

    @property
    @abc.abstractmethod
    def schema(self):
        """Supported Schema"""

    @abc.abstractmethod
    def generate_doc(
        self,
        routes: typing.List[tornado.web.URLSpec],
        *,
        api_base_url,
        description,
        api_version,
        title,
        contact,
        schemes,
        security_definitions,
        security,
        models,
        parameters
    ):
        """Generate docs"""


class Swagger2DocBuilder(BaseDocBuilder):
    """Swagger2.0 schema builder"""

    @property
    def schema(self):
        """Supported Schema"""
        return API_SWAGGER_2

    def generate_doc(
        self,
        routes: typing.List[tornado.web.URLSpec],
        *,
        api_base_url,
        description,
        api_version,
        title,
        contact,
        schemes,
        security_definitions,
        security,
        models,
        parameters
    ):
        """Generate docs"""
        swagger_spec = {
            "swagger": "2.0",
            "info": {
                "title": title,
                "description": _clean_description(description),
                "version": api_version,
            },
            "basePath": api_base_url,
            "schemes": schemes,
            "definitions": models,
            "parameters": parameters,
            "paths": _extract_paths(routes),
        }
        if contact:
            swagger_spec["info"]["contact"] = {"name": contact}
        if security_definitions:
            swagger_spec["securityDefinitions"] = security_definitions
        if security:
            swagger_spec["security"] = security

        return swagger_spec


class OpenApiDocBuilder(BaseDocBuilder):
    """OpenAPI 3 Schema builder"""

    @property
    def schema(self):
        """Supported Schema"""
        return API_OPENAPI_3

    def generate_doc(
        self,
        routes: typing.List[tornado.web.URLSpec],
        *,
        api_base_url,
        description,
        api_version,
        title,
        contact,
        schemes,
        security_definitions,
        security,
        models,
        parameters
    ):
        """Generate docs"""
        swagger_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": title,
                "description": _clean_description(description),
                "version": api_version,
            },
            "basePath": api_base_url,
            "schemes": schemes,
            "components": {
                "schemas": models,
                "parameters": parameters,
            },
            "paths": _extract_paths(routes),
        }

        if contact:
            swagger_spec["info"]["contact"] = {"name": contact}
        if security_definitions:
            swagger_spec["securityDefinitions"] = security_definitions
        if security:
            swagger_spec["security"] = security

        return swagger_spec


doc_builders = {b.schema: b for b in [Swagger2DocBuilder(), OpenApiDocBuilder()]}


def generate_doc_from_endpoints(
    routes: typing.List[tornado.web.URLSpec],
    *,
    api_base_url,
    description,
    api_version,
    title,
    contact,
    schemes,
    security_definitions,
    security,
    api_definition_version
):
    """Generate doc based on routes"""
    from tornado_swagger.model import export_swagger_models
    from tornado_swagger.parameter import export_swagger_parameters

    if api_definition_version not in doc_builders:
        raise ValueError("Unknown api_definition_version = " + api_definition_version)

    return doc_builders[api_definition_version].generate_doc(
        routes,
        api_base_url=api_base_url,
        description=description,
        api_version=api_version,
        title=title,
        contact=contact,
        schemes=schemes,
        security_definitions=security_definitions,
        security=security,
        models=export_swagger_models(),
        parameters=export_swagger_parameters(),
    )
