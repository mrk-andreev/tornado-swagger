"""Parameter."""

import typing

from tornado_swagger._builders import build_swagger_docs


class _SwaggerParameterStore:
    """Singleton with parameter definitions."""

    definitions: typing.ClassVar[typing.Dict[str, typing.Any]] = {}


def _save_parameter_doc(model: type) -> None:
    """Save model docstring to _SwaggerParameterStore."""
    doc = model.__doc__

    if doc is not None and "---" in doc:
        _SwaggerParameterStore.definitions[model.__name__] = build_swagger_docs(doc)


def export_swagger_parameters() -> typing.Dict[str, typing.Any]:
    """Get swagger parameters definition."""
    return _SwaggerParameterStore.definitions


def register_swagger_parameter(model: type) -> type:
    """Register parameter definition in swagger."""
    _save_parameter_doc(model)
    return model
