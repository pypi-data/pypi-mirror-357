import uuid

from sqlmodel import Field

from ..general.models import IAMModel
from sqlalchemy import Column, JSON


class CompositeRole(IAMModel, table=True):
    name: str = Field(index=True)
    roles: list = Field(sa_column=Column(JSON))
    organization: uuid.UUID = Field(index=True, nullable=True)
