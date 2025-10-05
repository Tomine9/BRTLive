from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import TypeVar, Generic, Type, Optional, List

ModelType = TypeVar("ModelType")

class BaseService(Generic[ModelType]):
    pass