import pydantic

from pydantic_partial import PartialModelMixin, create_partial_model


class Something(pydantic.BaseModel):
    name: str
    age: int
    already_optional: None = None


class SomethingWithMixin(PartialModelMixin, pydantic.BaseModel):
    name: str


def test_setup_is_sane():
    assert Something.__fields__["name"].required is True
    assert Something.__fields__["age"].required is True


def test_partial_will_make_all_fields_optional():
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
    SomethingWithMixinPartial2 = SomethingWithMixin.as_partial()

    assert SomethingWithMixinPartial1 is SomethingWithMixinPartial2
