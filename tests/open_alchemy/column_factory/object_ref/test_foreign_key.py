"""Tests for foreign key module."""

import pytest

from open_alchemy import exceptions
from open_alchemy.column_factory.object_ref import foreign_key


@pytest.mark.parametrize(
    "model_schema",
    [
        {
            "properties": {
                "ref_table_fk_column": {"x-foreign-key": "ref_table.fk_column"}
            }
        },
        {
            "properties": {
                "ref_table_fk_column": {
                    "type": "not_fk_type",
                    "x-foreign-key": "ref_table.fk_column",
                }
            }
        },
        {"properties": {"ref_table_fk_column": {"type": "fk_type"}}},
        {
            "properties": {
                "ref_table_fk_column": {
                    "type": "fk_type",
                    "x-foreign-key": "wrong_table.wrong_column",
                }
            }
        },
    ],
    ids=["no type", "wrong type", "no x-foreign-key", "wrong x-foreign-key"],
)
@pytest.mark.column
def test_check_required_invalid_schema(model_schema):
    """
    GIVEN model schema that is not valid
    WHEN check_required is called
    THEN MalformedRelationshipError is raised.
    """
    fk_spec = {"type": "fk_type", "x-foreign-key": "ref_table.fk_column"}
    fk_logical_name = "ref_table_fk_column"

    with pytest.raises(exceptions.MalformedRelationshipError):
        foreign_key.check_required(
            fk_spec=fk_spec,
            fk_logical_name=fk_logical_name,
            model_schema=model_schema,
            schemas={},
        )


@pytest.mark.parametrize(
    "model_schema, schemas, expected_required",
    [
        ({"properties": {}}, {}, True),
        (
            {
                "properties": {
                    "ref_table_fk_column": {
                        "type": "fk_type",
                        "x-foreign-key": "ref_table.fk_column",
                    }
                }
            },
            {},
            False,
        ),
        (
            {
                "properties": {
                    "ref_table_fk_column": {"$ref": "#/components/schemas/FkSchema"}
                }
            },
            {"FkSchema": {"type": "fk_type", "x-foreign-key": "ref_table.fk_column"}},
            False,
        ),
        (
            {
                "properties": {
                    "ref_table_fk_column": {
                        "allOf": [
                            {"type": "fk_type", "x-foreign-key": "ref_table.fk_column"}
                        ]
                    }
                }
            },
            {},
            False,
        ),
    ],
    ids=[
        "not in model schema",
        "in model schema",
        "in model schema $ref",
        "in model schema allOf",
    ],
)
@pytest.mark.column
def test_check_required(model_schema, schemas, expected_required):
    """
    GIVEN foreign key spec, foreign key logical name, model schema, schemas and
        expected required
    WHEN check_required is called
    THEN the expected required is returned.
    """
    fk_spec = {"type": "fk_type", "x-foreign-key": "ref_table.fk_column"}
    fk_logical_name = "ref_table_fk_column"

    required = foreign_key.check_required(
        fk_spec=fk_spec,
        fk_logical_name=fk_logical_name,
        model_schema=model_schema,
        schemas=schemas,
    )

    assert required == expected_required


@pytest.mark.parametrize(
    "schema, schemas, fk_column",
    [
        ({"properties": {"id": {}}}, {}, "id"),
        ({"x-tablename": "table 1"}, {}, "id"),
        ({"x-tablename": "table 1", "properties": {}}, {}, "id"),
        (
            {"x-tablename": "table 1", "properties": {"id": {"type": "integer"}}},
            {},
            "column_1",
        ),
        ({"x-tablename": "table 1", "properties": {"id": {}}}, {}, "id"),
    ],
    ids=[
        "no tablename",
        "no properties",
        "no id property",
        "custom foreign key property missing",
        "id property no type",
    ],
)
@pytest.mark.column
def test_gather_artifacts_malformed_schema(schema, schemas, fk_column):
    """
    GIVEN schema, schemas and foreign key column
    WHEN gather_artifacts is called with the schema, schemas and foreign key
        column
    THEN a MalformedSchemaError is raised.
    """
    with pytest.raises(exceptions.MalformedSchemaError):
        foreign_key.gather_artifacts(
            model_schema=schema, schemas=schemas, fk_column=fk_column
        )


@pytest.mark.column
def test_gather_artifacts_return():
    """
    GIVEN foreign key column and object schema with x-tablename and id and foreign key
        property with a type
    WHEN gather_artifacts is called with the schema
    THEN artifacts with the type of the foreign key property and x-foreign-key property.
    """
    schema = {
        "x-tablename": "table 1",
        "properties": {"id": {"type": "idType"}, "fk": {"type": "fkType"}},
    }
    schemas = {}

    logical_name, artifacts = foreign_key.gather_artifacts(
        model_schema=schema, schemas=schemas, fk_column="fk"
    )

    assert logical_name == "table 1_fk"
    assert artifacts.type == "fkType"
    assert artifacts.foreign_key == "table 1.fk"
