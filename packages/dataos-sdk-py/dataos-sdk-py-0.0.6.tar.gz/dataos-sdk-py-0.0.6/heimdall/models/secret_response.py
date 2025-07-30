from pydantic import BaseModel, Field
from typing import List

from heimdall.models.data import Data
from heimdall.models.links import Links


class SecretResponse(BaseModel):
    id: str
    data: List[Data]
    links: Links = Field(alias="_links")
