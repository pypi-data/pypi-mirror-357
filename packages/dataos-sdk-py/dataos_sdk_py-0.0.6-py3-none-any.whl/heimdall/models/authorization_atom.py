from typing import List, Optional

from pydantic import BaseModel


class AuthObject(BaseModel):
    tags: Optional[List[str]] = None
    paths: Optional[List[str]] = None


class AuthContext(BaseModel):
    predicate: str
    context: AuthObject


class AuthorizationAtom(BaseModel):
    id: str
    description: str
    predicate: str
    tags: Optional[List[str]] = None
    paths: Optional[List[str]] = None
    variables: Optional[List[str]] = None

    class Config:
        orm_mode = True

    def to_auth_context(self) -> AuthContext:
        return AuthContext(predicate=self.predicate, context=AuthObject(tags=self.tags, paths=self.paths))

    def has_variables(self) -> bool:
        return bool(self.variables)

    def copy(self):
        return self.copy()

# Usage:
# auth_atom_data = {
#     'id': 'atom123',
#     'description': 'Example Authorization Atom',
#     'predicate': 'some_expression',
#     'tags': ['tag1', 'tag2'],
#     'paths': ['path1', 'path2'],
# }
# auth_atom = AuthorizationAtom(**auth_atom_data)
# print(auth_atom)
