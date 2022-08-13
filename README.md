# pydantic-partial

Create partial models from your normal pydantic models. Partial models will allow
some or all fields to be optional and thus not be required when creating the model
instance.

Partial models can be used to support PATCH HTTP requests where the suer only wants
to update some fields of the model and normal validation for required fields is not
required. It may also be used to have partial response DTO's where you want to skip
certain fields, this can be useful in combination with `exclude_none`. It is - like
shown in these examples - intended to be used with API use cases, so when using
pydantic with for example FastAPI.

**Disclaimer:** This is the first public release of pydantic-partial. Things might
change in the future.

# Usage example

pydantic-partial provides a mixin to generate partial model classes. The mixin can
be used like this:

```python
# Something model, than can be used as a partial, too:
class Something(PartialModelMixin, pydantic.BaseModel):
    name: str
    age: int


# Create a full partial model
FullSomethingPartial = Something.as_partial()
FullSomethingPartial(name=None, age=None)
# You could also create a "partial Partial":
#AgeSomethingPartial = Something.as_partial("age")
```
