"""
A partial model will set certain (or all) fields to be optional with a default value of
`None`. This means you can construct a model copy with a partial representation of the details
you would normally provide.

Partial models can be used to for example only send a reduced version of your internal
models as response data to the client when you combine partial models with actively
replacing certain fields with `None` values and usage of `exclude_none` (or
`response_model_exclude_none`).

Usage example:
```python
# Something can be used as a partial, too
class Something(PartialModelMixin, pydantic.BaseModel):
    name: str
    age: int


# Create a full partial model
FullSomethingPartial = Something.as_partial()
FullSomethingPartial(name=None, age=None)
# You could also create a "partial Partial":
#AgeSomethingPartial = Something.as_partial("age")
```
"""

import functools
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_args, get_origin

import pydantic

from .utils import copy_field_info

SelfT = TypeVar("SelfT", bound=pydantic.BaseModel)


@functools.lru_cache(maxsize=None, typed=True)
def create_partial_model(
    base_cls: Type[SelfT],
    *fields: str,
    recursive: bool = False,
) -> Type[SelfT]:
    # Convert one type to being partial - if possible
    def _partial_type(field_name_: str, field_type_: Type) -> Type:
        if (
                isinstance(field_type_, type)
                and issubclass(field_type_, PartialModelMixin)
        ):
            field_prefix = f"{field_name_}."
            children_fields = [
                field.removeprefix(field_prefix)
                for field
                in fields_
                if field.startswith(field_prefix)
            ]
            if children_fields == ["*"]:
                children_fields = []
            return field_type_.as_partial(*children_fields, recursive=recursive)
        else:
            return field_type_

    # By default make all fields optional, but use passed fields when possible
    if fields:
        fields_ = list(fields)
    else:
        fields_ = list(base_cls.__fields__.keys())

    # Construct list of optional new field overrides
    optional_fields: dict[str, Any] = {}
    for field_name in base_cls.__fields__.keys():
        field_type = base_cls.__fields__[field_name].outer_type_
        if field_type is None:
            continue

        # Do we have any fields starting with $FIELD_NAME + "."?
        has_sub_fields = any(
            field.startswith(f"{field_name}.")
                for field
                in fields_
        )

        # Continue if this field needs not to be handled
        if field_name not in fields_ and not has_sub_fields:
            continue

        # Change type for sub models, if requested
        if recursive or has_sub_fields:
            field_type_origin = get_origin(field_type)
            if field_type_origin in (Union, list, List, dict, Dict):
                field_type = field_type_origin[
                    tuple(
                        _partial_type(field_name, field_args_type)
                            for field_args_type
                            in get_args(field_type)
                    )
                ]
            else:
                field_type = _partial_type(field_name, field_type)

        # Construct new field definition
        if field_name in fields_:
            if (
                    base_cls.__fields__[field_name].required
                    or base_cls.__fields__[field_name].default is not None
            ):
                optional_fields[field_name] = (
                    Optional[field_type],
                    copy_field_info(
                        base_cls.__fields__[field_name].field_info,
                        default=None,  # Set default to None
                        defaul_factory=None,  # Remove default_factory if set
                        nullable=True,  # For API usage
                    ),
                )
        elif recursive or has_sub_fields:
            optional_fields[field_name] = (
                field_type,
                copy_field_info(base_cls.__fields__[field_name].field_info),
            )

    # Return original model class if nothing has changed
    if not optional_fields:
        return base_cls

    # Generate new subclass model with those optional fields
    return pydantic.create_model(
        f"{base_cls.__name__}Partial",
        __base__=base_cls,
        **optional_fields,
    )


class PartialModelMixin(pydantic.BaseModel):
    """
    Partial model mixin. Will allow usage of `as_partial()` on the model class
    to create a partial version of the model class.
    """

    @classmethod
    def as_partial(  # noqa: C901
        cls: Type[SelfT],
        *fields: str,
        recursive: bool = False,
    ) -> Type[SelfT]:
        return create_partial_model(cls, *fields, recursive=recursive)
