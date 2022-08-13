from typing import List

import pydantic
import pytest

from pydantic_partial import PartialModelMixin


class Something(PartialModelMixin, pydantic.BaseModel):
    name: str = pydantic.Field(..., alias="test_name", title="TEST Name", something_else=True)
    age: int
    already_optional: None = None

    class Config:
        allow_population_by_field_name = True


class SomethingList(PartialModelMixin, pydantic.BaseModel):
    items: List[Something]


def test_setup_is_sane():
    assert Something.__fields__["name"].required is True
    assert Something.__fields__["age"].required is True
    assert SomethingList.__fields__["items"].required is True


def test_partial_will_make_all_fields_optional():
    SomethingPartial = Something.as_partial()

    assert SomethingPartial.__fields__["name"].required is False
    assert SomethingPartial.__fields__["age"].required is False
    SomethingPartial()


def test_partial_will_keep_original_field_options():
    SomethingPartial = Something.as_partial()

    assert SomethingPartial.__fields__["name"].field_info.alias == "test_name"
    assert SomethingPartial.__fields__["name"].field_info.title == "TEST Name"
    assert SomethingPartial.__fields__["name"].field_info.extra["something_else"] is True


def test_partial_allows_to_only_change_certain_fields():
    SomethingNamePartial = Something.as_partial("name")

    assert SomethingNamePartial.__fields__["name"].required is False
    assert SomethingNamePartial.__fields__["age"].required is True
    SomethingNamePartial(age=1)
    with pytest.raises(pydantic.ValidationError):
        SomethingNamePartial(name="test")

    SomethingAgePartial = Something.as_partial("age")

    assert SomethingAgePartial.__fields__["name"].required is True
    assert SomethingAgePartial.__fields__["age"].required is False
    SomethingAgePartial(name="test")
    with pytest.raises(pydantic.ValidationError):
        SomethingAgePartial(age=1)

    SomethingPartial = Something.as_partial("name", "age")

    assert SomethingPartial.__fields__["name"].required is False
    assert SomethingPartial.__fields__["age"].required is False
    SomethingPartial()


def test_partial_allows_recursive_usage():
    SomethingListPartial = SomethingList.as_partial()

    assert SomethingListPartial.__fields__["items"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["name"].required is True
    assert SomethingListPartial.__fields__["items"].type_.__fields__["age"].required is True

    SomethingListRecursivePartial = SomethingList.as_partial(recursive=True)

    assert SomethingListRecursivePartial.__fields__["items"].required is False
    assert SomethingListRecursivePartial.__fields__["items"].type_.__fields__["name"].required is False
    assert SomethingListRecursivePartial.__fields__["items"].type_.__fields__["age"].required is False


def test_partial_allows_explicit_recursive():
    SomethingListPartial = SomethingList.as_partial("items.*")

    assert SomethingListPartial.__fields__["items"].required is True
    assert SomethingListPartial.__fields__["items"].type_.__fields__["name"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["age"].required is False
    SomethingListPartial(items=[])

    SomethingListPartial = SomethingList.as_partial("items")

    assert SomethingListPartial.__fields__["items"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["name"].required is True
    assert SomethingListPartial.__fields__["items"].type_.__fields__["age"].required is True
    SomethingListPartial(items=[])
    SomethingListPartial(items=None)

    SomethingListPartial = SomethingList.as_partial("items.name")

    assert SomethingListPartial.__fields__["items"].required is True
    assert SomethingListPartial.__fields__["items"].type_.__fields__["name"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["age"].required is True
    SomethingListPartial(items=[])
    SomethingListPartial(items=[{"age": 1}])

    SomethingListPartial = SomethingList.as_partial(recursive=True)

    assert SomethingListPartial.__fields__["items"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["name"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["age"].required is False
    SomethingListPartial(items=[])
    SomethingListPartial(items=None)
    SomethingListPartial(items=[{}])

    SomethingListPartial = SomethingList.as_partial("items.name", recursive=True)

    assert SomethingListPartial.__fields__["items"].required is True
    assert SomethingListPartial.__fields__["items"].type_.__fields__["name"].required is False
    assert SomethingListPartial.__fields__["items"].type_.__fields__["age"].required is True
    SomethingListPartial(items=[])
    SomethingListPartial(items=[{"age": 1}])


def test_no_change_to_optional_fields():
    SomethingPartial = Something.as_partial("already_optional")

    assert SomethingPartial is Something
