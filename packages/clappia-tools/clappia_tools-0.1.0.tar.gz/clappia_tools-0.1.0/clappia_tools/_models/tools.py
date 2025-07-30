import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Condition:
    operator: str
    filterKeyType: str
    key: str
    value: str

    def to_dict(self) -> dict:
        return {
            "operator": self.operator,
            "filterKeyType": self.filterKeyType,
            "key": self.key,
            "value": self.value,
        }


@dataclass
class Query:
    conditions: List[Condition]
    operator: Optional[str] = None

    def to_dict(self) -> dict:
        result = {"conditions": [condition.to_dict() for condition in self.conditions]}
        if self.operator:
            result["operator"] = self.operator
        return result


@dataclass
class QueryGroup:
    queries: List[Query]

    def to_dict(self) -> dict:
        return {"queries": [query.to_dict() for query in self.queries]}


@dataclass
class Filters:
    queries: List[QueryGroup]

    def to_dict(self) -> dict:
        return {"queries": [query_group.to_dict() for query_group in self.queries]}


@dataclass
class Dimension:
    fieldName: str
    label: str
    dataType: str
    dimensionType: str = "CUSTOM"
    sortDirection: Optional[str] = None
    sortType: Optional[str] = None
    missingValue: Optional[str] = None
    interval: Optional[str] = None

    def to_dict(self) -> dict:
        result = {
            "fieldName": self.fieldName,
            "label": self.label,
            "dataType": self.dataType,
            "dimensionType": self.dimensionType,
        }
        if self.sortDirection:
            result["sortDirection"] = self.sortDirection
        if self.sortType:
            result["sortType"] = self.sortType
        if self.missingValue is not None:
            result["missingValue"] = self.missingValue
        if self.interval:
            result["interval"] = self.interval
        return result


@dataclass
class AggregationOperand:
    fieldName: str
    label: str
    dataType: str
    dimensionType: str = "CUSTOM"

    def to_dict(self) -> dict:
        return {
            "fieldName": self.fieldName,
            "label": self.label,
            "dataType": self.dataType,
            "dimensionType": self.dimensionType,
        }


@dataclass
class AggregationDimension:
    type: str
    operand: Optional["AggregationOperand"] = None

    def to_dict(self) -> dict:
        result = {"type": self.type}
        if self.operand:
            result["operand"] = self.operand.to_dict()
        return result
