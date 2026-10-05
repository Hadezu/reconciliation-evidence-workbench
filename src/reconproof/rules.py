"""Explicit business contract. Unknown rule fields are errors, never ignored."""

import json
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SourceRule(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    columns: dict[str, str]
    sheet: str | None = None
    delimiter: Literal[",", ";", "\t"] = ","
    decimal_separator: Literal[".", ","] = "."
    included_statuses: list[str] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def valid_mapping(self):
        if set(self.columns) != {"key", "currency", "amount", "date", "status"}:
            raise ValueError("Map exactly key, currency, amount, date, status")
        if len(set(self.columns.values())) != 5 or any(
            not x.strip() or len(x) > 128 for x in self.columns.values()
        ):
            raise ValueError("Mapped headers must be distinct and nonempty")
        if any(not x.strip() or len(x) > 80 for x in self.included_statuses):
            raise ValueError("Status values must be nonempty and at most 80 characters")
        if self.sheet is not None and not 1 <= len(self.sheet) <= 128:
            raise ValueError("Invalid sheet name")
        return self


class Rules(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal[1] = 1
    period_start: str
    period_end_exclusive: str
    reporting_timezone: Literal["UTC"] = "UTC"
    currencies: list[Literal["EUR", "PLN", "USD"]] = Field(min_length=1)
    tolerance_minor: int = Field(default=0, ge=0, le=100)
    left: SourceRule
    right: SourceRule

    @model_validator(mode="after")
    def valid_period(self):
        start, end = (
            date.fromisoformat(self.period_start),
            date.fromisoformat(self.period_end_exclusive),
        )
        if (
            start.isoformat() != self.period_start
            or end.isoformat() != self.period_end_exclusive
            or start >= end
        ):
            raise ValueError("Use YYYY-MM-DD and a nonempty half-open period")
        if len(set(self.currencies)) != len(self.currencies):
            raise ValueError("Currencies must be unique")
        return self


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_rules(data: bytes) -> Rules:
    if len(data) > 64_000:
        raise ValueError("Rules exceed 64 KB")
    return Rules.model_validate(
        json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_object)
    )
