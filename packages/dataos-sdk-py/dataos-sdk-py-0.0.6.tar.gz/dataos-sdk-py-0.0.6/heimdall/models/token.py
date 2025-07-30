from pydantic import BaseModel, Field
from typing import Dict

from heimdall.models.links import Links


class Token(BaseModel):
    name: str
    expiration: str
    type: str
    data: Dict
    user_id: str
    links: Links = Field(alias="_links")
