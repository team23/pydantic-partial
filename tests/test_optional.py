from typing import Any, Union

import pydantic

import pytest

from pydantic_partial import create_partial_model
from pydantic_partial._compat import PYDANTIC_V1, PYDANTIC_V2


if PYDANTIC_V1:
    def _field_is_required(
        model: Union[type[pydantic.BaseModel], pydantic.BaseModel],
        field_name: str,
    ) -> bool:
        """Check if a field is required on a pydantic V1 model."""
        # noinspection PyDeprecation
        return model.__fields__[field_name].required


    def _field_get_default(
        model: Union[type[pydantic.BaseModel], pydantic.BaseModel],
        field_name: str,
    ) -> tuple[Any, Any]:
        """Return field default info"""
        field_info = model.__fields__[field_name]
        return field_info.default, field_info.default_factory
elif PYDANTIC_V2:
    def _field_is_required(
        model: Union[type[pydantic.BaseModel], pydantic.BaseModel],
        field_name: str,
    ) -> bool:
        """Check if a field is required on a pydantic V2 model."""
        return model.model_fields[field_name].is_required()


    def _field_get_default(
        model: Union[type[pydantic.BaseModel], pydantic.BaseModel],
        field_name: str,
    ) -> tuple[Any, Any]:
        """Return field default info"""
        field_info = model.model_fields[field_name]
        return field_info.default, field_info.default_factory
else:
    raise DeprecationWarning("Pydantic has to be in version 1 or 2.")


class Something(pydantic.BaseModel):
    name: Union[str, None] = "Joe Doe"
    something_else_id: int


PartialSomething = create_partial_model(Something, optional=False)
PartialSomethingOptional = create_partial_model(Something, optional=True)


def test_fields_not_required():
    assert _field_is_required(PartialSomething, "name") is False
    assert _field_is_required(PartialSomething, "something_else_id") is False


def test_field_defaults():
    assert _field_get_default(PartialSomething, "name") == ("Joe Doe", None)
    assert _field_get_default(PartialSomething, "something_else_id") == (None, None)


def test_validate_ok():
    # It shouldn't be necessary to check that the right default values end
    # up in the models. That should already be done by pydantic's own tests.
    # We just check that validation succeeds.
    PartialSomething()
    PartialSomething(name='Jane Doe')
    PartialSomething(name=None)
    PartialSomething(something_else_id=42)
    PartialSomething(name='Jane Doe', something_else_id=42)
    PartialSomething(name=None, something_else_id=42)


def test_validate_fail():
    with pytest.raises(pydantic.ValidationError):
        PartialSomething(something_else_id=None)


def test_validate_optional():
    PartialSomethingOptional(something_else_id=None)
