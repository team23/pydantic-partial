from typing import Any, Dict, Optional, Type

import pydantic
from pydantic.fields import FieldInfo
from pydantic.version import VERSION as PYDANTIC_VERSION

from .utils import copy_field_info

PYDANTIC_V1 = PYDANTIC_VERSION.startswith("1.")
PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

if PYDANTIC_V1:  # pragma: no cover
    from pydantic.fields import ModelField  # type: ignore

    class PydanticCompat:  # noqa: F811
        model_class: Type[pydantic.BaseModel]

        def __init__(
            self,
            model_class: Type[pydantic.BaseModel],
        ) -> None:
            self.model_class = model_class

        # We are are actually working on ModelField objects for all of this, but
        # pydantic 2.x does not include this layer any more. So naming follows
        # pydantic 2.x naming.

        @property
        def model_fields(self) -> Dict[str, ModelField]:
            return self.model_class.__fields__  # type: ignore

        def get_model_field_info_annotation(self, model_field: ModelField) -> type:
            return model_field.outer_type_  # type: ignore

        def is_model_field_info_required(self, model_field: ModelField) -> bool:
            return (
                model_field.required
                or model_field.default is not None
            )

        def copy_model_field_info(self, model_field: ModelField, **kwargs: Any) -> bool:
            return copy_field_info(model_field.field_info, **kwargs)

elif PYDANTIC_V2:  # pragma: no cover
    class PydanticCompat:  # type: ignore
        model_class: Type[pydantic.BaseModel]

        def __init__(
            self,
            model_class: Type[pydantic.BaseModel],
        ) -> None:
            self.model_class = model_class

        @property
        def model_fields(self) -> Dict[str, FieldInfo]:
            return self.model_class.model_fields

        def get_model_field_info_annotation(self, field_info: FieldInfo) -> Optional[Type[Any]]:
            return field_info.annotation

        def is_model_field_info_required(self, field_info: FieldInfo) -> bool:
            return field_info.is_required()  # type: ignore

        def copy_model_field_info(self, field_info: FieldInfo, **kwargs: Any) -> bool:
            return copy_field_info(field_info, **kwargs)
