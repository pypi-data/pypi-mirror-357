from pydantic import BaseModel
from typing import Optional, Any, List


class AuthorizationResultData(BaseModel):
    id: Optional[str] = None
    data: Any = None
    tags: Optional[List[str]] = None
