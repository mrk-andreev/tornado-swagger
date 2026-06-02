# pylint: disable=R0401,C0415
"""Builders."""

import abc
import collections
import inspect
import re
import typing
import warnings
from pathlib import Path

import tornado.web
import yaml

from tornado_swagger.const import API_OPENAPI_3, API_OPENAPI_3_1, API_SWAGGER_2

SwaggerDict = typing.Dict[str, typing.Any]

SWAGGER_TEMPLATE = Path(__file__).parent / "templates" / "swagger.yaml"
SWAGGER_DOC_SEPARATOR = "---"


def _extract_swagger_definition(endpoint_doc: str) -> str:
    """Extract swagger definition after SWAGGER_DOC_SEPARATOR."""
    endpoint_doc_lines = endpoint_doc.splitlines()

    for i, doc_line in enumerate(endpoint_doc_lines):
        if SWAGGER_DOC_SEPARATOR in doc_line:
            end_point_swagger_start = i + 1
            endpoint_doc_lines = endpoint_doc_lines[end_point_swagger_start:]
            break
    return "\n".join(endpoint_doc_lines)


def build_swagger_docs(endpoint_doc: str) -> SwaggerDict:
    """Build swagger doc based on endpoint docstring."""
    endpoint_doc = _extract_swagger_definition(endpoint_doc)

    # Build JSON YAML Obj
    endpoint_doc = endpoint_doc.replace("\t", "    ")  # fix windows tabs bug
    try:
        end_point_swagger_doc = yaml.safe_load(endpoint_doc)
    except yaml.YAMLError:
        return {
            "description": "Swagger document could not be loaded from docstring",
            "tags": ["Invalid Swagger"],
        }
    else:
        if not isinstance(end_point_swagger_doc, dict):
            return {
                "description": "Swagger document could not be loaded from docstring",
                "tags": ["Invalid Swagger"],
            }
        return end_point_swagger_doc


def _try_extract_doc(func: typing.Callable[..., typing.Any]) -> typing.Optional[str]:
    """Extract docstring from origin function removing decorators."""
    return inspect.unwrap(func).__doc__


def _build_doc_from_func_doc(handler: typing.Type[tornado.web.RequestHandler]) -> typing.Dict[str, SwaggerDict]:
    out: typing.Dict[str, SwaggerDict] = {}

    for supported_method in handler.SUPPORTED_METHODS:
        method = supported_method.lower()
        doc = _try_extract_doc(getattr(handler, method))

        if doc is not None and "---" in doc:
            out.update({method: build_swagger_docs(doc)})

    return out


def _try_extract_args(method_handler: typing.Callable[..., typing.Any]) -> typing.List[str]:
    """Extract method args from origin function removing decorators."""
    return inspect.getfullargspec(inspect.unwrap(method_handler)).args[1:]


def _extract_parameters_names(handler: typing.Type[tornado.web.RequestHandler], parameters_count: int, method: str) -> typing.List[str]:
    """Extract parameters names from handler."""
    if parameters_count == 0:
        return []

    parameters = ["{?}" for _ in range(parameters_count)]

    method_handler = getattr(handler, method.lower())
    args = _try_extract_args(method_handler)

    for i, arg in enumerate(args):
        if set(arg) != {"_"} and i < len(parameters):
            parameters[i] = arg

    return parameters


def _format_handler_path(route: tornado.web.URLSpec, method: str) -> typing.Optional[str]:
    brackets_regex = re.compile(r"\(.*?\)")
    parameters = _extract_parameters_names(route.target, route.regex.groups, method)
    route_pattern = route.regex.pattern
    brackets = brackets_regex.findall(route_pattern)

    if len(brackets) != len(parameters):
        warnings.warn("Illegal route. route.regex.groups does not match all parameters. Route = " + str(route), stacklevel=2)
        return None

    for i, entity in enumerate(brackets):
        route_pattern = route_pattern.replace(entity, f"{{{parameters[i]}}}", 1)

    return route_pattern[:-1]


def _normalize_path_prefix(prefix: str) -> str:
    """Normalize a path prefix for route path comparisons."""
    if not prefix:
        return ""
    normalized = prefix if prefix.startswith("/") else f"/{prefix}"
    return normalized.rstrip("/") or "/"


def _strip_path_prefix(path: str, strip_prefix: typing.Optional[str]) -> str:
    """Strip a path prefix only when it matches full path boundaries."""
    if not strip_prefix:
        return path

    normalized_prefix = _normalize_path_prefix(strip_prefix)
    if normalized_prefix == "/":
        return path
    if path == normalized_prefix:
        return "/"
    if path.startswith(f"{normalized_prefix}/"):
        return path[len(normalized_prefix) :]
    return path


def nesteddict2yaml(d: SwaggerDict, indent: int = 10, result: str = "") -> str:
    for key, value in d.items():
        result += " " * indent + str(key) + ":"
        if isinstance(value, dict):
            result = nesteddict2yaml(value, indent + 2, result + "\n")
        else:
            result += " " + str(value) + "\n"
    return result


def _clean_description(description: str) -> str:
    """Remove empty space from description begin."""
    _start_desc = 0
    for i, word in enumerate(description):
        if word != "\n":
            _start_desc = i
            break
    return "    ".join(description[_start_desc:].splitlines())


def _extract_paths(
    routes: typing.List[tornado.web.URLSpec],
    *,
    strip_prefix: typing.Optional[str],
) -> typing.DefaultDict[str, SwaggerDict]:
    paths: typing.DefaultDict[str, SwaggerDict] = collections.defaultdict(dict)

    for route in routes:
        for method_name, method_description in _build_doc_from_func_doc(route.target).items():
            path_handler = _format_handler_path(route, method_name)
            if path_handler is None:
                continue

            path_handler = _strip_path_prefix(path_handler, strip_prefix)
            paths[path_handler].update({method_name: method_description})

    return paths


class BaseDocBuilder(abc.ABC):
    """Doc builder."""

    @property
    @abc.abstractmethod
    def schema(self) -> str:
        """Supported Schema."""

    @abc.abstractmethod
    def generate_doc(
        self,
        routes: typing.List[tornado.web.URLSpec],
        *,
        api_base_url: str,
        description: str,
        api_version: str,
        title: str,
        contact: str,
        strip_prefix: typing.Optional[str],
        schemes: typing.Optional[typing.List[typing.Any]],
        security_definitions: typing.Optional[SwaggerDict],
        security_schemes: typing.Optional[SwaggerDict],
        security: typing.Optional[typing.List[typing.Any]],
        models: SwaggerDict,
        parameters: SwaggerDict,
    ) -> SwaggerDict:
        """Generate docs."""


class Swagger2DocBuilder(BaseDocBuilder):
    """Swagger2.0 schema builder."""

    @property
    def schema(self) -> str:
        """Supported Schema."""
        return API_SWAGGER_2

    def generate_doc(
        self,
        routes: typing.List[tornado.web.URLSpec],
        *,
        api_base_url: str,
        description: str,
        api_version: str,
        title: str,
        contact: str,
        strip_prefix: typing.Optional[str],
        schemes: typing.Optional[typing.List[typing.Any]],
        security_definitions: typing.Optional[SwaggerDict],
        security_schemes: typing.Optional[SwaggerDict],
        security: typing.Optional[typing.List[typing.Any]],
        models: SwaggerDict,
        parameters: SwaggerDict,
    ) -> SwaggerDict:
        """Generate docs."""
        if security_schemes:
            msg = "security_schemes is only supported with api_definition_version=API_OPENAPI_3"
            raise ValueError(msg)

        if security_definitions:
            for security_definition in security_definitions.values():
                if security_definition.get("type") == "http":
                    msg = "HTTP security schemes require api_definition_version=API_OPENAPI_3"
                    raise ValueError(msg)

        swagger_spec: SwaggerDict = {
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
            "paths": _extract_paths(routes, strip_prefix=strip_prefix),
        }
        if contact:
            swagger_spec["info"]["contact"] = {"name": contact}
        if security_definitions:
            swagger_spec["securityDefinitions"] = security_definitions
        if security:
            swagger_spec["security"] = security

        return swagger_spec


class OpenApiDocBuilder(BaseDocBuilder):
    """OpenAPI 3 Schema builder."""

    openapi_version = "3.0.3"

    @property
    def schema(self) -> str:
        """Supported Schema."""
        return API_OPENAPI_3

    def generate_doc(
        self,
        routes: typing.List[tornado.web.URLSpec],
        *,
        api_base_url: str,
        description: str,
        api_version: str,
        title: str,
        contact: str,
        strip_prefix: typing.Optional[str],
        schemes: typing.Optional[typing.List[typing.Any]],
        security_definitions: typing.Optional[SwaggerDict],
        security_schemes: typing.Optional[SwaggerDict],
        security: typing.Optional[typing.List[typing.Any]],
        models: SwaggerDict,
        parameters: SwaggerDict,
    ) -> SwaggerDict:
        """Generate docs."""
        del schemes

        security_schemes = security_schemes or security_definitions

        swagger_spec: SwaggerDict = {
            "openapi": self.openapi_version,
            "info": {
                "title": title,
                "description": _clean_description(description),
                "version": api_version,
            },
            "servers": [
                {"url": api_base_url},
            ],
            "components": {
                "schemas": models,
                "parameters": parameters,
            },
            "paths": _extract_paths(routes, strip_prefix=strip_prefix),
        }

        if contact:
            swagger_spec["info"]["contact"] = {"name": contact}
        if security_schemes:
            swagger_spec["components"]["securitySchemes"] = security_schemes
        if security:
            swagger_spec["security"] = security

        return swagger_spec


class OpenApi31DocBuilder(OpenApiDocBuilder):
    """OpenAPI 3.1 Schema builder."""

    openapi_version = "3.1.0"

    @property
    def schema(self) -> str:
        """Supported Schema."""
        return API_OPENAPI_3_1


doc_builders = {b.schema: b for b in [Swagger2DocBuilder(), OpenApiDocBuilder(), OpenApi31DocBuilder()]}


def generate_doc_from_endpoints(
    routes: typing.List[tornado.web.URLSpec],
    *,
    api_base_url: str,
    description: str,
    api_version: str,
    title: str,
    contact: str,
    schemes: typing.Optional[typing.List[typing.Any]],
    security_definitions: typing.Optional[SwaggerDict],
    security: typing.Optional[typing.List[typing.Any]],
    api_definition_version: str,
    security_schemes: typing.Optional[SwaggerDict] = None,
    strip_prefix: typing.Optional[str] = None,
) -> SwaggerDict:
    """Generate doc based on routes."""
    from tornado_swagger.model import export_swagger_models  # noqa: PLC0415
    from tornado_swagger.parameter import export_swagger_parameters  # noqa: PLC0415

    if api_definition_version not in doc_builders:
        raise ValueError("Unknown api_definition_version = " + api_definition_version)

    return doc_builders[api_definition_version].generate_doc(
        routes,
        api_base_url=api_base_url,
        description=description,
        api_version=api_version,
        title=title,
        contact=contact,
        strip_prefix=strip_prefix,
        schemes=schemes,
        security_definitions=security_definitions,
        security_schemes=security_schemes,
        security=security,
        models=export_swagger_models(),
        parameters=export_swagger_parameters(),
    )
