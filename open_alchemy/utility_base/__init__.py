"""Base class providing utilities for SQLAlchemy models."""

import functools
import json
import typing

from .. import exceptions
from .. import facades
from .. import helpers
from .. import types as oa_types
from . import to_dict

TUtilityBase = typing.TypeVar("TUtilityBase", bound="UtilityBase")
TOptUtilityBase = typing.Optional[TUtilityBase]


class UtilityBase:
    """Base class providing utilities for SQLAlchemy models."""

    # Record of the schema used to construct the model. Must be an object type. For all
    # columns any $ref must be resolved an allOf must be merged for all. Objects must
    # be recorded as a free-form object and have a x-de-$ref extension property with
    # the de-referenced name of the schema.
    _schema: typing.ClassVar[oa_types.Schema]

    def __init__(self, **kwargs: typing.Any) -> None:
        """Construct."""
        raise NotImplementedError

    @classmethod
    def _get_schema(cls) -> oa_types.Schema:
        """
        Get the schema.

        Raise ModelAttributeError if _schema is not defined.

        Returns:
            The schema.

        """
        # Checking for _schema
        if not hasattr(cls, "_schema"):
            raise exceptions.ModelAttributeError(
                "Model does not have a record of its schema. "
                "To support to_dict set the _schema class variable."
            )
        return cls._schema

    @classmethod
    def get_properties(cls) -> oa_types.Schema:
        """
        Get the properties from the schema.

        Raise ModelAttributeError if _schema is not defined.
        Raise MalformedSchemaError if the schema does not have any properties.

        Returns:
            The properties of the schema.

        """
        schema = cls._get_schema()
        # Checking that _schema has properties
        properties = schema.get("properties")
        if properties is None:
            raise exceptions.MalformedSchemaError(
                "The model schema does not have any properties."
            )
        return properties

    @staticmethod
    def _get_model(
        *, spec: oa_types.Schema, name: str, schema: oa_types.Schema
    ) -> typing.Type[TUtilityBase]:
        """Get the model based on the schema."""
        ref_model_name = helpers.ext_prop.get(source=spec, name="x-de-$ref")
        if ref_model_name is None:
            raise exceptions.MalformedSchemaError(
                "To construct object parameters the schema for the property must "
                "include the x-de-$ref extension property with the name of the "
                "model to construct for the property. "
                f"The property is {name}. "
                f"The model schema is {json.dumps(schema)}."
            )
        # Try to get model
        ref_model: TOptUtilityBase = facades.models.get_model(name=ref_model_name)
        if ref_model is None:
            raise exceptions.SchemaNotFoundError(
                f"The {ref_model_name} model was not found on open_alchemy.models."
            )
        return ref_model

    @staticmethod
    def _get_parent(*, schema: oa_types.Schema) -> typing.Type[TUtilityBase]:
        """Get the parent model of a model."""
        parent_name = helpers.ext_prop.get(source=schema, name="x-inherits")
        if parent_name is None or not isinstance(parent_name, str):
            raise exceptions.MalformedSchemaError(
                "To construct a model that inherits x-inherits must be present and a "
                "string. "
                f"The model schema is {json.dumps(schema)}."
            )
        # Try to get model
        parent: TOptUtilityBase = facades.models.get_model(name=parent_name)
        if parent is None:
            raise exceptions.SchemaNotFoundError(
                f"The {parent_name} model was not found on open_alchemy.models."
            )
        return parent

    @staticmethod
    def _model_from_dict(
        kwargs: typing.Dict[str, typing.Any], *, model: typing.Type[TUtilityBase]
    ) -> TUtilityBase:
        """Construct model from dictionary."""
        return model.from_dict(**kwargs)

    @classmethod
    def construct_from_dict_init(
        cls: typing.Type[TUtilityBase], **kwargs: typing.Any
    ) -> typing.Dict[str, typing.Any]:
        """Construct the dictionary passed to model construction."""
        # Check dictionary
        schema = cls._get_schema()
        try:
            facades.jsonschema.validate(instance=kwargs, schema=schema)
        except facades.jsonschema.ValidationError:
            raise exceptions.MalformedModelDictionaryError(
                "The dictionary passed to from_dict is not a valid instance of the "
                "model schema. "
                f"The expected schema is {json.dumps(schema)}. "
                f"The given value is {json.dumps(kwargs)}."
            )

        # Assemble dictionary for construction
        properties = cls.get_properties()
        model_dict: typing.Dict[str, typing.Any] = {}
        for name, value in kwargs.items():
            # Get the specification and type of the property
            spec = properties.get(name)
            if spec is None:
                raise exceptions.MalformedModelDictionaryError(
                    "A parameter was passed in that is not a property in the model "
                    "schema. "
                    f"The parameter is {name}. "
                    f"The model schema is {json.dumps(schema)}."
                )

            # Check readOnly
            read_only = spec.get("readOnly")
            if read_only is True:
                raise exceptions.MalformedModelDictionaryError(
                    "A parameter was passed in that is marked as readOnly in the "
                    "schema. "
                    f"The parameter is {name}. "
                    f"The model schema is {json.dumps(schema)}."
                )

            # Check type
            type_ = spec.get("type")
            format_ = spec.get("format")
            if type_ is None:
                raise exceptions.TypeMissingError(
                    f"The schema for the {name} property does not have a type."
                )

            # Handle object
            ref_model: typing.Type[UtilityBase]
            if type_ == "object":
                ref_model = cls._get_model(spec=spec, name=name, schema=schema)
                ref_model_instance = cls._model_from_dict(value, model=ref_model)
                model_dict[name] = ref_model_instance
                continue

            if type_ == "array":
                item_spec = spec.get("items")
                if item_spec is None:
                    raise exceptions.MalformedSchemaError(
                        "To construct array parameters the schema for the property "
                        "must include the items property with the information about "
                        "the array items. "
                        f"The property is {name}. "
                        f"The model schema is {json.dumps(schema)}."
                    )
                ref_model = cls._get_model(spec=item_spec, name=name, schema=schema)
                model_from_dict = functools.partial(
                    cls._model_from_dict, model=ref_model
                )
                ref_model_instances = map(model_from_dict, value)
                model_dict[name] = list(ref_model_instances)
                continue

            # Handle other types
            model_dict[name] = helpers.oa_to_py_type.convert(
                value=value, type_=type_, format_=format_
            )

        return model_dict

    @classmethod
    def from_dict(cls: typing.Type[TUtilityBase], **kwargs: typing.Any) -> TUtilityBase:
        """
        Construct model instance from a dictionary.

        Raise MalformedModelDictionaryError when the dictionary does not satisfy the
        model schema.

        Args:
            kwargs: The values to construct the class with.

        Returns:
            An instance of the model constructed using the dictionary.

        """
        schema = cls._get_schema()
        # Handle model that inherits
        if helpers.schema.inherits(schema=schema, schemas={}):
            # Retrieve parent model
            parent: typing.Type[UtilityBase] = cls._get_parent(schema=schema)

            # Construct parent initialization dictionary
            # Get properties for schema
            properties = cls.get_properties()
            # Pass kwargs that don't belong to the current model to the parent
            parent_kwargs = {
                key: value for key, value in kwargs.items() if key not in properties
            }
            parent_init_dict = parent.construct_from_dict_init(**parent_kwargs)

            # COnstruct child (the current model) initialization dictionary
            child_kwargs = {
                key: value for key, value in kwargs.items() if key in properties
            }
            init_dict = {
                **parent_init_dict,
                **cls.construct_from_dict_init(**child_kwargs),
            }
        else:
            init_dict = cls.construct_from_dict_init(**kwargs)

        return cls(**init_dict)

    @classmethod
    def from_str(cls: typing.Type[TUtilityBase], value: str) -> TUtilityBase:
        """
        Construct model instance from a JSON string.

        Raise MalformedModelDictionaryError when the value is not a string or the string
        is not valid JSON.

        Args:
            kwargs: The values to construct the class with.

        Returns:
            An instance of the model constructed using the dictionary.

        """
        if not isinstance(value, str):
            raise exceptions.MalformedModelDictionaryError(
                f"The value is not of type string. The value is {value}."
            )
        try:
            dict_value = json.loads(value)
        except json.JSONDecodeError:
            raise exceptions.MalformedModelDictionaryError(
                f"The string value is not valid JSON. The value is {value}."
            )
        if not isinstance(dict_value, dict):
            raise exceptions.MalformedModelDictionaryError(
                f"The string value is not a Python dictionary. The value is {value}."
            )
        return cls.from_dict(**dict_value)

    @classmethod
    def instance_to_dict(cls, instance: TUtilityBase) -> typing.Dict[str, typing.Any]:
        """Convert instance of the model to a dictionary."""
        properties = cls.get_properties()

        # Collecting the values of the properties
        return_dict: typing.Dict[str, typing.Any] = {}
        for name, spec in properties.items():
            value = getattr(instance, name, None)
            return_dict[name] = to_dict.convert(schema=spec, value=value)

        return return_dict

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Convert model instance to dictionary.

        Raise TypeMissingError if a property does not have a type.
        Raise InvalidModelInstanceError is an object to_dict call failed.

        Returns:
            The dictionary representation of the model.

        """
        schema = self._get_schema()
        if helpers.schema.inherits(schema=schema, schemas={}):
            # Retrieve parent model and convert to dict
            parent: typing.Type[UtilityBase] = self._get_parent(schema=schema)
            parent_dict = parent.instance_to_dict(self)
            return {**parent_dict, **self.instance_to_dict(self)}

        return self.instance_to_dict(self)

    def to_str(self) -> str:
        """
        Convert model instance to a string.

        Returns:
            The JSON string representation of the model.

        """
        instance_dict = self.to_dict()
        return json.dumps(instance_dict)
