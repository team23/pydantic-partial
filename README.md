# `pydantic-partial`

Create partial models from your normal pydantic models. Partial models will allow
some or all fields to be optional and thus not be required when creating the model
instance.

Partial models can be used to support PATCH HTTP requests where the suer only wants
to update some fields of the model and normal validation for required fields is not
required. It may also be used to have partial response DTO's where you want to skip
certain fields, this can be useful in combination with `exclude_none`. It is - like
shown in these examples - intended to be used with API use cases, so when using
pydantic with for example FastAPI.

**Disclaimer:** This is still an early release of `pydantic-partial`. Things might
change in the future. PR welcome. ;-)

# Usage example

`pydantic-partial` provides a mixin to generate partial model classes. The mixin can
be used like this:

```python
import pydantic
from pydantic_partial import PartialModelMixin

# Something model, than can be used as a partial, too:
class Something(PartialModelMixin, pydantic.BaseModel):
    name: str
    age: int


# Create a full partial model
FullSomethingPartial = Something.as_partial()
FullSomethingPartial(name=None, age=None)
```

## Without using the mixin mixin

You also may create partial models without using the mixin:

```python
import pydantic
from pydantic_partial import create_partial_model

# Something model, without the mixin:
class Something(pydantic.BaseModel):
    name: str
    age: int


# Create a full partial model
FullSomethingPartial = create_partial_model(Something)
FullSomethingPartial(name=None, age=None)
```

## Only changing some fields to being optional

`pydantic-partial` can be used to create partial models that only change some
of the fields to being optional. Just pass the list of fields to be optional to
the `as_partial()` or `create_partial_model()` function.

```python
import pydantic
from pydantic_partial import create_partial_model

class Something(pydantic.BaseModel):
    name: str
    age: int

# Create a partial model only for the name attribute
FullSomethingPartial = create_partial_model(Something, 'name')
FullSomethingPartial(name=None)
# This would still raise an error: FullSomethingPartial(age=None)
```

## Recursive partials

Partial models can be created changing the field of all nested models to being
optional, too.

```python
from typing import List

import pydantic
from pydantic_partial import PartialModelMixin, create_partial_model

class InnerSomething(PartialModelMixin, pydantic.BaseModel):
    name: str

class OuterSomething(pydantic.BaseModel):
    name: str
    things: List[InnerSomething]

# Create a full partial model
RecursiveOuterSomethingPartial = create_partial_model(OuterSomething, recursive=True)
RecursiveOuterSomethingPartial(things=[
    {},
])
```

**Note:** The inner model MUST extend the `PartialModelMixin` mixin. Otherwise
`pydantic-partial` will not be able to detect which fields may allow to being
converted to partial models.

**Also note:** My recommendation would be to always create such recursive
partials by creating partials for all the required models and then override
the fields on you outer partial model class. This is way more explicit.

# Contributing

If you want to contribute to this project, feel free to just fork the project,
create a dev branch in your fork and then create a pull request (PR). If you
are unsure about whether your changes really suit the project please create an
issue first, to talk about this.
