import pydantic
import pytest

from pydantic_partial import PartialModelMixin, create_partial_model
from pydantic_partial._compat import PYDANTIC_V1, PYDANTIC_V2

if PYDANTIC_V1:
    def _field_is_required(model: pydantic.BaseModel, field_name: str) -> bool:
        """Check if a field is required on a pydantic V1 model."""
        return model.__fields__[field_name].required
elif PYDANTIC_V2:
    def _field_is_required(model: pydantic.BaseModel, field_name: str) -> bool:
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


@pytest.mark.skipif(PYDANTIC_V1, reason="pydantic v1 did change fields handling")
def test_setup_is_sane_v2():
    assert Something.model_fields["name"].is_required() is True
    assert Something.model_fields["age"].is_required() is True


@pytest.mark.skipif(PYDANTIC_V2, reason="pydantic v1 did change fields handling")
def test_setup_is_sane_v1():
    assert Something.__fields__["name"].required is True
    assert Something.__fields__["age"].required is True

def test_setup_is_sane():
    assert _field_is_required(Something, "name") is True
    assert _field_is_required(Something, "age") is True


@pytest.mark.skipif(PYDANTIC_V1, reason="pydantic v1 did change fields handling")
def test_partial_will_make_all_fields_optional_v2():
    SomethingPartial = create_partial_model(Something)

    assert SomethingPartial.model_fields["name"].is_required() is False
    assert SomethingPartial.model_fields["age"].is_required() is False
    SomethingPartial()


@pytest.mark.skipif(PYDANTIC_V2, reason="pydantic v1 did change fields handling")
def test_partial_will_make_all_fields_optional_v1():
    SomethingPartial = create_partial_model(Something)

    assert SomethingPartial.__fields__["name"].required is False
    assert SomethingPartial.__fields__["age"].required is False
    SomethingPartial()


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
    # Note: When we do not pass recursive=False the functools.lru_cache will
    #       actually create a separate model class, as the parameters differ.
    SomethingWithMixinPartial1 = create_partial_model(SomethingWithMixin, recursive=False)
    SomethingWithMixinPartial2 = SomethingWithMixin.model_as_partial()

    assert SomethingWithMixinPartial1 is SomethingWithMixinPartial2
