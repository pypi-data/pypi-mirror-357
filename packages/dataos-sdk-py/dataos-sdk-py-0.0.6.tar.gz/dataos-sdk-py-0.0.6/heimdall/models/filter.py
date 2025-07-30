from pydantic import BaseModel, Field
from typing import Optional, List


class ValueFrom(BaseModel):
    user_attribute: str


class Filter(BaseModel):
    column: Optional[str] = Field(None, alias="column")
    operator: Optional[str] = Field(None, alias="operator")
    value: Optional[str] = Field(None, alias="value")
    value_from: Optional[ValueFrom] = Field(None, alias="valueFrom")
    supported_data_types: Optional[List[str]] = Field(None, alias="supported_data_types")
