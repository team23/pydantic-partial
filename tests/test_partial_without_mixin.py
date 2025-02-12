from typing import Union

import pydantic

from pydantic_partial import PartialModelMixin, create_partial_model
from pydantic_partial._compat import PYDANTIC_V1, PYDANTIC_V2

if PYDANTIC_V1:
    def _field_is_required(model: Union[type[pydantic.BaseModel], pydantic.BaseModel], field_name: str) -> bool:
        """Check if a field is required on a pydantic V1 model."""
        return model.__fields__[field_name].required
elif PYDANTIC_V2:
    def _field_is_required(model: Union[type[pydantic.BaseModel], pydantic.BaseModel], field_name: str) -> bool:
        """Check if a field is required on a pydantic V2 model."""
        return model.model_fields[field_name].is_required()
else:
    raise DeprecationWarning("Pydantic has to be in version 1 or 2.")


class Something(pydantic.BaseModel):
    name: str
    age: int
    already_optional: None = None


class SomethingWithMixin(PartialModelMixin, pydantic.BaseModel):
    name: str


def test_setup_is_sane():
    assert _field_is_required(Something, "name") is True
    assert _field_is_required(Something, "age") is True


def test_partial_will_make_all_fields_optional():
    SomethingPartial = create_partial_model(Something)

    assert _field_is_required(SomethingPartial, "name") is False
    assert _field_is_required(SomethingPartial, "age") is False
    SomethingPartial()


def test_partial_model_will_be_cached():
    SomethingPartial1 = create_partial_model(Something)
    SomethingPartial2 = create_partial_model(Something)

    assert SomethingPartial1 is SomethingPartial2


def test_partial_model_will_only_be_cached_with_same_params():
    SomethingPartial1 = create_partial_model(Something, 'name')
    SomethingPartial2 = create_partial_model(Something, 'age')

    assert SomethingPartial1 is not SomethingPartial2


def test_partial_model_will_be_the_same_on_mixin():
    # Note: When we do not pass recursive=False and partial_cls_name=None the functools.lru_cache will
    #       actually create a separate model class, as the parameters differ.
    SomethingWithMixinPartial1 = create_partial_model(SomethingWithMixin, recursive=False, partial_cls_name=None)
    SomethingWithMixinPartial2 = SomethingWithMixin.model_as_partial()

    assert SomethingWithMixinPartial1 is SomethingWithMixinPartial2


def test_partial_class_name_can_be_overridden():
    SomethingPartial = create_partial_model(Something, "name")
    assert SomethingPartial.__name__ == "SomethingPartial"

    partial_cls_name = "SomethingWithOptionalName"
    SomethingWithOptionalName = create_partial_model(Something, "name", partial_cls_name=partial_cls_name)
    assert SomethingWithOptionalName.__name__ == partial_cls_name
