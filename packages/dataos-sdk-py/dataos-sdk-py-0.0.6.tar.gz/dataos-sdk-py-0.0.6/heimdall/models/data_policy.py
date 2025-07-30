from pydantic import BaseModel
from typing import Optional, List

from heimdall.models.filter import Filter
from heimdall.models.mask import Mask


class UserSelector(BaseModel):
    match: str
    tags: List[str]


class ColumnSelector(BaseModel):
    tags: Optional[List[str]]
    names: Optional[List[str]]


class Selector(BaseModel):
    user: Optional[UserSelector]
    column: Optional[ColumnSelector]


class DataPolicy(BaseModel):
    priority: int
    type: str
    selector: Optional[Selector]
    mask: Optional[Mask]
    filters: Optional[List[Filter]]
    dataset_id: str
    name: Optional[str]
    description: Optional[str]
