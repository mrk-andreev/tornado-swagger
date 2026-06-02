"""Test model and parameter registration helpers"""

import pytest

from tornado_swagger import model, parameter


@pytest.fixture(autouse=True)
def clean_swagger_stores():
    model._SwaggerModelsStore.definitions = {}
    parameter._SwaggerParameterStore.definitions = {}
    yield
    model._SwaggerModelsStore.definitions = {}
    parameter._SwaggerParameterStore.definitions = {}


def test_register_swagger_model_saves_definition_and_returns_class():
    @model.register_swagger_model
    class Pet:
        """---
        type: object
        properties:
          name:
            type: string
        """

    assert model.export_swagger_models() == {
        "Pet": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
            },
        },
    }
    assert Pet.__name__ == "Pet"


def test_register_swagger_model_ignores_classes_without_swagger_doc():
    @model.register_swagger_model
    class Undocumented:
        """Plain class documentation."""

    assert model.export_swagger_models() == {}
    assert Undocumented.__name__ == "Undocumented"


def test_register_swagger_parameter_saves_definition_and_returns_class():
    @parameter.register_swagger_parameter
    class Limit:
        """---
        name: limit
        in: query
        required: false
        schema:
          type: integer
        """

    assert parameter.export_swagger_parameters() == {
        "Limit": {
            "name": "limit",
            "in": "query",
            "required": False,
            "schema": {
                "type": "integer",
            },
        },
    }
    assert Limit.__name__ == "Limit"


def test_register_swagger_parameter_ignores_classes_without_swagger_doc():
    @parameter.register_swagger_parameter
    class Undocumented:
        """Plain class documentation."""

    assert parameter.export_swagger_parameters() == {}
    assert Undocumented.__name__ == "Undocumented"
