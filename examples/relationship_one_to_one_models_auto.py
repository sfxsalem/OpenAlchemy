"""Autogenerated SQLAlchemy models based on OpenAlchemy models."""
# pylint: disable=no-member,super-init-not-called,unused-argument

import typing

import sqlalchemy
from sqlalchemy import orm

from open_alchemy import models


class PayInfoDict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    id: typing.Optional[int]
    account_number: typing.Optional[str]


class TPayInfo(typing.Protocol):
    """SQLAlchemy model protocol."""

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    id: typing.Optional[int]
    account_number: typing.Optional[str]
    employee: typing.Optional["TEmployee"]

    def __init__(
        self,
        id: typing.Optional[int] = None,
        account_number: typing.Optional[str] = None,
    ) -> None:
        """Construct."""
        ...

    @classmethod
    def from_dict(
        cls,
        id: typing.Optional[int] = None,
        account_number: typing.Optional[str] = None,
    ) -> "TPayInfo":
        """Construct from a dictionary (eg. a POST payload)."""
        ...

    @classmethod
    def from_str(cls, value: str) -> "TPayInfo":
        """Construct from a JSON string (eg. a POST payload)."""
        ...

    def to_dict(self) -> PayInfoDict:
        """Convert to a dictionary (eg. to send back for a GET request)."""
        ...

    def to_str(self) -> str:
        """Convert to a JSON string (eg. to send back for a GET request)."""
        ...


PayInfo: TPayInfo = models.PayInfo  # type: ignore


class EmployeeDict(typing.TypedDict, total=False):
    """TypedDict for properties that are not required."""

    id: typing.Optional[int]
    name: typing.Optional[str]
    pay_info: typing.Optional["PayInfoDict"]


class TEmployee(typing.Protocol):
    """SQLAlchemy model protocol."""

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    id: typing.Optional[int]
    name: typing.Optional[str]
    pay_info: typing.Optional["TPayInfo"]

    def __init__(
        self,
        id: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        pay_info: typing.Optional["TPayInfo"] = None,
    ) -> None:
        """Construct."""
        ...

    @classmethod
    def from_dict(
        cls,
        id: typing.Optional[int] = None,
        name: typing.Optional[str] = None,
        pay_info: typing.Optional["PayInfoDict"] = None,
    ) -> "TEmployee":
        """Construct from a dictionary (eg. a POST payload)."""
        ...

    @classmethod
    def from_str(cls, value: str) -> "TEmployee":
        """Construct from a JSON string (eg. a POST payload)."""
        ...

    def to_dict(self) -> EmployeeDict:
        """Convert to a dictionary (eg. to send back for a GET request)."""
        ...

    def to_str(self) -> str:
        """Convert to a JSON string (eg. to send back for a GET request)."""
        ...


Employee: TEmployee = models.Employee  # type: ignore
