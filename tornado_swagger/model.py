from tornado_swagger._builders import build_swagger_docs


class _SwaggerModelsStore:
    """Singleton with models definitions"""

    definitions = {}


def _save_model_doc(model):
    """Save model docstring to _SwaggerModelsStore"""
    doc = model.__doc__

    if doc is not None and "---" in doc:
        _SwaggerModelsStore.definitions[model.__name__] = build_swagger_docs(doc)


def export_swagger_models():
    """Get swagger models definition"""
    return _SwaggerModelsStore.definitions


def register_swagger_model(model):
    """Register model definition in swagger"""
    _save_model_doc(model)
    return model
