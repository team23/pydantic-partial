import pydantic
import pytest

from pydantic_partial import PartialModelMixin, create_partial_model
from pydantic_partial._compat import PYDANTIC_V1, PYDANTIC_V2


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
