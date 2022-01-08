from tornado_swagger._builders import build_swagger_docs


class _SwaggerParameterStore:
    """Singleton with parameter definitions"""

    definitions = {}


def _save_parameter_doc(model):
    """Save model docstring to _SwaggerParameterStore"""
    doc = model.__doc__

    if doc is not None and "---" in doc:
        _SwaggerParameterStore.definitions[model.__name__] = build_swagger_docs(doc)


def export_swagger_parameters():
    """Get swagger parameters definition"""
    return _SwaggerParameterStore.definitions


def register_swagger_parameter(model):
    """Register parameter definition in swagger"""
    _save_parameter_doc(model)
    return model
