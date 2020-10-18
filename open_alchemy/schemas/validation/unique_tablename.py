"""Check that all x-tablename are unique."""

import typing

from ... import helpers as oa_helpers
from ... import types as oa_types
from .. import helpers
from . import types


def _is_single_table_inheritance(
    schemas: oa_types.Schemas, schema: oa_types.Schema
) -> bool:
    """
    Calculate whether the schema uses single table inheritance.

    Args:
        schemas: All defined schemas.
        schema: The schema to check.

    Returns:
        Whether the schema uses single table inheritance.

    """
    if not oa_helpers.schema.inherits(schema=schema, schemas=schemas):
        return False

    inheritance_type = oa_helpers.inheritance.calculate_type(
        schema=schema, schemas=schemas
    )
    return inheritance_type == oa_helpers.inheritance.Type.SINGLE_TABLE


def check(*, schemas: oa_types.Schemas) -> types.Result:
    """
    Check that all x-tablename are unique.

    Assume that schemas are otherwise valid.

    The algorithm is:
    1. iterate over constructable schemas,
    2. skip single table inheritance schemas,
    3. record the tablename and schema name,
    4. if a tablename has already been seen, return result that is not valid and
    5. return valid result.

    Args:
        schemas: The schemas to check.

    Returns:
        Whether the schemas have unique tablenames and the reason if not.

    """
    constructable_schemas = helpers.iterate.constructable(schemas=schemas)
    not_single_inheritance_schemas = filter(
        lambda args: not _is_single_table_inheritance(schemas, args[1]),
        constructable_schemas,
    )

    seen_tablenames: typing.Dict[str, str] = {}
    for name, schema in not_single_inheritance_schemas:
        tablename = oa_helpers.peek.prefer_local(
            get_value=oa_helpers.peek.tablename, schemas=schemas, schema=schema
        )
        assert tablename is not None

        if tablename in seen_tablenames:
            seen_on_schema = seen_tablenames[tablename]
            return types.Result(
                valid=False,
                reason=(
                    f'duplicate "x-tablename" value {tablename} defined on the schema '
                    f"{name}, already defined on the schema {seen_on_schema}"
                ),
            )

        seen_tablenames[tablename] = name

    return types.Result(valid=True, reason=None)
