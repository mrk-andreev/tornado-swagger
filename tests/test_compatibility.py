"""Compatibility tests for generated Swagger/OpenAPI documents."""

from pathlib import Path

import pytest
import tornado.web
import yaml

try:
    from openapi_spec_validator import validate
except ImportError:
    from openapi_spec_validator import validate_spec as validate

# OpenAPI 3.1 validation requires openapi-spec-validator >= 0.6, which is not
# installed on older Python versions (see requirements-dev.txt). The dedicated
# 3.1 validator class only exists from that release onwards, so its presence is
# used as a capability probe.
try:
    from openapi_spec_validator import OpenAPIV31SpecValidator  # noqa: F401

    _SUPPORTS_OPENAPI_31 = True
except ImportError:
    _SUPPORTS_OPENAPI_31 = False

from tornado_swagger.const import API_OPENAPI_3, API_OPENAPI_3_1, API_SWAGGER_2
from tornado_swagger.setup import export_swagger

FIXTURES = Path(__file__).parent / "fixtures" / "compat"


def _load_fixture(filename):
    with (FIXTURES / filename).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _docstring(operation):
    return "---\n" + yaml.safe_dump(operation, sort_keys=False)


def _routes_from_fixture(expected):
    class PetHandler(tornado.web.RequestHandler):
        def get(self, pet_id):
            raise NotImplementedError

        def post(self, pet_id):
            raise NotImplementedError

    class SearchHandler(tornado.web.RequestHandler):
        def post(self):
            raise NotImplementedError

    pet_path = expected["paths"]["/pets/{pet_id}"]
    PetHandler.get.__doc__ = _docstring(pet_path["get"])
    PetHandler.post.__doc__ = _docstring(pet_path["post"])
    SearchHandler.post.__doc__ = _docstring(expected["paths"]["/pets/search"]["post"])

    return [
        tornado.web.url(r"/pets/([^/]+)", PetHandler),
        tornado.web.url(r"/pets/search", SearchHandler),
    ]


def _export_from_fixture(expected, api_definition_version):
    kwargs = {
        "api_base_url": "/v1",
        "description": expected["info"]["description"],
        "api_version": expected["info"]["version"],
        "title": expected["info"]["title"],
        "contact": expected["info"]["contact"]["name"],
        "security": expected["security"],
        "api_definition_version": api_definition_version,
    }

    if api_definition_version == API_SWAGGER_2:
        kwargs.update(
            schemes=expected["schemes"],
            security_definitions=expected["securityDefinitions"],
        )
    else:
        kwargs.update(
            schemes=["https"],
            security_schemes=expected["components"]["securitySchemes"],
        )

    return export_swagger(_routes_from_fixture(expected), **kwargs)


@pytest.mark.parametrize(
    ("fixture_name", "api_definition_version"),
    [
        ("swagger2.yaml", API_SWAGGER_2),
        ("openapi3.yaml", API_OPENAPI_3),
        ("openapi31.yaml", API_OPENAPI_3_1),
    ],
)
def test_generated_document_matches_and_validates_against_spec(monkeypatch, fixture_name, api_definition_version):
    expected = _load_fixture(fixture_name)

    if api_definition_version == API_SWAGGER_2:
        monkeypatch.setattr("tornado_swagger.model.export_swagger_models", lambda: expected["definitions"])
        monkeypatch.setattr("tornado_swagger.parameter.export_swagger_parameters", lambda: expected["parameters"])
    else:
        monkeypatch.setattr("tornado_swagger.model.export_swagger_models", lambda: expected["components"]["schemas"])
        monkeypatch.setattr("tornado_swagger.parameter.export_swagger_parameters", lambda: expected["components"]["parameters"])

    docs = _export_from_fixture(expected, api_definition_version)

    assert docs == expected

    if api_definition_version == API_OPENAPI_3_1 and not _SUPPORTS_OPENAPI_31:
        pytest.skip("installed openapi-spec-validator lacks OpenAPI 3.1 support")
    validate(docs)


@pytest.mark.parametrize("api_definition_version", [API_OPENAPI_3, API_OPENAPI_3_1])
def test_openapi_documents_do_not_emit_swagger_2_top_level_fields(monkeypatch, api_definition_version):
    fixture_name = "openapi3.yaml" if api_definition_version == API_OPENAPI_3 else "openapi31.yaml"
    expected = _load_fixture(fixture_name)
    monkeypatch.setattr("tornado_swagger.model.export_swagger_models", lambda: expected["components"]["schemas"])
    monkeypatch.setattr("tornado_swagger.parameter.export_swagger_parameters", lambda: expected["components"]["parameters"])

    docs = _export_from_fixture(expected, api_definition_version)

    assert "basePath" not in docs
    assert "schemes" not in docs
    assert "securityDefinitions" not in docs


def test_swagger_2_rejects_openapi_security_schemes():
    with pytest.raises(ValueError, match="security_schemes is only supported"):
        export_swagger(
            [],
            api_definition_version=API_SWAGGER_2,
            security_schemes={"BearerAuth": {"type": "http", "scheme": "bearer"}},
            security=[{"BearerAuth": []}],
        )


def test_swagger_2_rejects_http_security_definitions():
    with pytest.raises(ValueError, match="HTTP security schemes require"):
        export_swagger(
            [],
            api_definition_version=API_SWAGGER_2,
            security_definitions={"BearerAuth": {"type": "http", "scheme": "bearer"}},
            security=[{"BearerAuth": []}],
        )
