"""Tests for full relationship schema checking."""

import pytest

from open_alchemy.schemas.validation.relationship import full

TESTS = [
    pytest.param(
        {"properties": {"id": {"type": "integer", "x-primary-key": True}}},
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (False, "source schema :: schema must define x-tablename"),
        id="many-to-many source no tablename",
    ),
    pytest.param(
        {
            "x-tablename": True,
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (
            False,
            "malformed schema :: The x-tablename property must be of type string. ",
        ),
        id="many-to-many referenced invalid tablename",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (False, "referenced schema :: schema must define x-tablename"),
        id="many-to-many referenced no tablename",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-secondary": "schema_ref_schema",
                "x-tablename": True,
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (
            False,
            "malformed schema :: The x-tablename property must be of type string. ",
        ),
        id="many-to-many referenced invalid tablename",
    ),
    pytest.param(
        {"x-tablename": "schema", "properties": {"id": {"type": "integer"}}},
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (False, "source schema :: schema must have a primary key"),
        id="many-to-many source no primary key property",
    ),
    pytest.param(
        {"x-tablename": "schema", "properties": {"id": {"x-primary-key": True}}},
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (
            False,
            "source schema :: id property :: malformed schema :: Every property "
            "requires a type. ",
        ),
        id="many-to-many source invalid primary key property",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {
                "id": {"type": "integer", "x-primary-key": True},
                "name": {"type": "string", "x-primary-key": True},
            },
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (
            False,
            "source schema :: many-to-many relationships currently only support single "
            "primary key schemas",
        ),
        id="many-to-many source multiple primary key property",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer"}},
            }
        },
        (False, "referenced schema :: schema must have a primary key"),
        id="many-to-many referenced no primary key property",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"x-primary-key": True}},
            }
        },
        (
            False,
            "referenced schema :: id property :: malformed schema :: Every property "
            "requires a type. ",
        ),
        id="many-to-many referenced invalid primary key property",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {
                    "id": {"type": "integer", "x-primary-key": True},
                    "name": {"type": "string", "x-primary-key": True},
                },
            }
        },
        (
            False,
            "referenced schema :: many-to-many relationships currently only support "
            "single primary key schemas",
        ),
        id="many-to-many referenced multiple primary key property",
    ),
    pytest.param(
        {
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer", "x-primary-key": True}},
        },
        "ref_schemas",
        {"type": "array", "items": {"$ref": "#/components/schemas/RefSchema"}},
        {
            "RefSchema": {
                "x-tablename": "ref_schema",
                "x-secondary": "schema_ref_schema",
                "properties": {"id": {"type": "integer", "x-primary-key": True}},
            }
        },
        (True, None),
        id="many-to-many valid",
    ),
]


@pytest.mark.parametrize(
    "parent_schema, property_name, property_schema, schemas, expected_result", TESTS,
)
@pytest.mark.schemas
def test_check(parent_schema, property_name, property_schema, schemas, expected_result):
    """
    GIVEN schemas, the parent and property schema and the expected result
    WHEN check is called with the schemas and parent and property schema
    THEN the expected result is returned.
    """
    # pylint: disable=assignment-from-no-return
    returned_result = full.check(schemas, parent_schema, property_name, property_schema)

    assert returned_result == expected_result
