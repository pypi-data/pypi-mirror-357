from typing import List, Optional

from pydantic import BaseModel


class Column(BaseModel):
    # Define the fields for the Column model if required
    # For example:
    name: str
    data_type: str


class Dataset(BaseModel):
    id: str
    tags: Optional[List[str]] = None
    columns: Optional[List[Column]] = None
