from pydantic import BaseModel
from typing import List, Dict, Optional


class AuthObject(BaseModel):
    tags: Optional[List[str]] = None


class Result(BaseModel):
    """
    Represents the result of an authorization request.

    :param id: The identifier of the result, defaults to "".
    :type id: str
    :param tags: The tags associated with the result, defaults to None.
    :type tags: List[str], optional
    """
    id: str = None
    tags: Optional[List[str]] = None


class Error(BaseModel):
    """
    Represents an error encountered during an authorization request.

    :param status: The status code associated with the error, defaults to -1.
    :type status: int
    :param message: The error message associated with the error, defaults to "".
    :type message: str
    """
    status: int = -1
    message: str = ""


class AuthorizationResponse(BaseModel):
    """
    Represents the response of an authorization request.

    :param allow: Whether the request is allowed, defaults to False.
    :type allow: bool
    :param valid: Whether the request is valid, defaults to False.
    :type valid: bool
    :param result: The result of the authorization request, defaults to None.
    :type result: Result, optional
    :param error: The error encountered during the authorization request, defaults to None.
    :type error: Error, optional
    """
    allow: bool = False
    valid: bool = False
    result: Optional[Result] = None
    error: Optional[Error] = None


class AuthorizationResponseBatch(BaseModel):
    """
    Represents a batch of authorization responses.

    :param id: The identifier of the batch, defaults to "".
    :type id: str
    :param tags: The tags associated with the batch, defaults to None.
    :type tags: Optional[List[str]]
    :param results: The results of the authorization request, defaults to None.
    :type results: Optional[Dict[str, AuthorizationResponse]]
    """
    id: str = None
    tags: Optional[List[str]] = None
    results: Optional[Dict[str, AuthorizationResponse]] = None


class AuthResponseSingle(BaseModel):
    """
    Represents a single authorization response within a batch.

    :param allow: Whether the request is allowed, defaults to False.
    :type allow: bool
    :param valid: Whether the request is valid, defaults to False.
    :type valid: bool
    :param error: The error encountered during the authorization request, defaults to None.
    :type error: Optional[Error]
    """
    allow: bool = False
    valid: bool = False
    error: Optional[Error] = None
