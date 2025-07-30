from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class AuthObject(BaseModel):
    tags: Optional[List[str]] = None
    paths: Optional[List[str]] = None


class AuthContext(BaseModel):
    predicate: str
    object: AuthObject
    metadata: Optional[Dict[str, Any]] = None


class PepContext(BaseModel):
    user_agent: Optional[str] = None
    authorization_atom_id: str


class AuthorizationRequest(BaseModel):
    token: str
    context: Optional[AuthContext] = None
    pep_context: Optional[PepContext] = None


class AuthorizationRequestBatch(BaseModel):
    token: str
    contexts: Dict[str, AuthContext]
