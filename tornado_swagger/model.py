import functools

from tornado_swagger.helpers.builders import extract_swagger_docs

swagger_models = {}


def _save_model_doc(model):
    global swagger_models
    doc = model.__doc__

    if doc is not None and '---' in doc:
        swagger_models[model.__name__] = extract_swagger_docs(doc)


def register_swagger_model(model):
    _save_model_doc(model)

    @functools.wraps(model)
    def wrapper(*args, **kwargs):
        return model(*args, **kwargs)

    return wrapper