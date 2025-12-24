from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ErrorSchema(BaseModel):
    code: str
    message: str


class ResponseSchema(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorSchema] = None
