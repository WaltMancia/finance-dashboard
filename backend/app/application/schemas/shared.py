from typing import Generic, TypeVar
from pydantic import BaseModel

# TypeVar define un tipo genérico — como los generics de TypeScript
T = TypeVar("T")


class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Schema reutilizable para cualquier lista paginada.
    Generic[T] permite tiparlo con cualquier schema:
      PaginatedResponse[TransactionResponse]
      PaginatedResponse[CategoryResponse]
    """
    data: list[T]
    pagination: Pagination