from typing import Any, no_type_check

import pydantic
from pydantic.fields import FieldInfo


@no_type_check
def copy_field_info(field_info: FieldInfo, **overrides: Any) -> FieldInfo:
    """
    Return a copy of a pydantic FieldInfo object, allow to override
    certain values.
    """

    return pydantic.Field(**{
        **{
            k: v
            for k, v
            in field_info.__repr_args__()
            if k != "extra"
        },
        **field_info.extra,
        **overrides,
    })
