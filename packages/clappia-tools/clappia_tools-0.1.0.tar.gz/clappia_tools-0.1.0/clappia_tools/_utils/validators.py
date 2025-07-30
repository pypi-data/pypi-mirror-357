import re
from typing import Optional, Tuple, List
from clappia_tools._enums.tools_enum import (
    FilterOperator,
    LogicalOperator,
    FilterKeyType,
    AggregationType,
    DimensionType,
)


class ClappiaValidator:
    """Validates Clappia data structures and business logic"""

    STANDARD_FIELDS = {
        "$submissionId",
        "$owner",
        "$status",
        "$createdAt",
        "$updatedAt",
        "$state",
        "submissionId",
        "owner",
        "status",
        "createdAt",
        "updatedAt",
        "state",
    }

    @staticmethod
    def validate_status(status: dict) -> Tuple[bool, str]:
        """Validate the status dictionary structure"""
        if not isinstance(status, dict):
            return False, "status must be a dictionary"

        if not status:
            return False, "status cannot be empty"

        if "statusName" not in status and "name" not in status:
            return False, "status must contain 'statusName' or 'name' field"

        status_value = status.get("statusName") or status.get("name")
        if (
            not status_value
            or not isinstance(status_value, str)
            or not status_value.strip()
        ):
            return False, "status name must be a non-empty string"

        return True, ""

    @staticmethod
    def validate_condition(condition: dict) -> Tuple[bool, str]:
        """Validate a single filter condition"""
        required_fields = ["operator", "filterKeyType", "key", "value"]
        for field in required_fields:
            if field not in condition:
                return False, f"Condition missing required field: {field}"

        if condition["operator"] not in [op.value for op in FilterOperator]:
            return False, f"Invalid operator: {condition['operator']}"

        if condition["filterKeyType"] not in [fkt.value for fkt in FilterKeyType]:
            return False, f"Invalid filterKeyType: {condition['filterKeyType']}"

        key = condition["key"]
        if not isinstance(key, str) or len(key.strip()) == 0:
            return False, "Key must be a non-empty string"

        if (
            condition["filterKeyType"] == FilterKeyType.STANDARD.value
            and key not in ClappiaValidator.STANDARD_FIELDS
        ):
            return (
                False,
                f"Standard filterKeyType used but key '{key}' is not a standard field",
            )

        operator = condition["operator"]
        value = condition["value"]

        if operator in [FilterOperator.EMPTY.value, FilterOperator.NON_EMPTY.value]:
            if value and value.strip():
                return False, f"Operator {operator} should have empty value"
        else:
            if not isinstance(value, str) or len(value.strip()) == 0:
                return False, f"Operator {operator} requires a non-empty value"

        return True, ""

    @staticmethod
    def validate_filters(filters: dict) -> Tuple[bool, str]:
        """Validate complete filter structure"""
        if "queries" not in filters:
            return False, "Filters must contain 'queries' key"

        queries = filters["queries"]
        if not isinstance(queries, list) or len(queries) == 0:
            return False, "Queries must be a non-empty list"

        for query_group in queries:
            if not isinstance(query_group, dict):
                return False, "Each query group must be a dictionary"

            if "queries" not in query_group:
                return False, "Each query group must contain 'queries' key"

            inner_queries = query_group["queries"]
            if not isinstance(inner_queries, list):
                return False, "Inner queries must be a list"

            for inner_query in inner_queries:
                if not isinstance(inner_query, dict):
                    return False, "Each inner query must be a dictionary"

                if "conditions" not in inner_query:
                    return False, "Each query must contain 'conditions'"

                conditions = inner_query["conditions"]
                if not isinstance(conditions, list) or len(conditions) == 0:
                    return False, "Conditions must be a non-empty list"

                for condition in conditions:
                    is_valid, error_msg = ClappiaValidator.validate_condition(condition)
                    if not is_valid:
                        return False, error_msg

                if "operator" in inner_query:
                    logical_op = inner_query["operator"]
                    if logical_op not in [op.value for op in LogicalOperator]:
                        return False, f"Invalid logical operator: {logical_op}"

        return True, ""

    @staticmethod
    def validate_aggregation_type(agg_type: str) -> bool:
        """Validate that aggregation type is valid"""
        return agg_type in [at.value for at in AggregationType]

    @staticmethod
    def validate_dimension_type(dim_type: str) -> bool:
        """Validate that dimension type is valid"""
        return dim_type in [dt.value for dt in DimensionType]


class ClappiaInputValidator:
    """Validates user inputs like app IDs, emails, etc."""

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    APP_ID_PATTERN = r"^[A-Z0-9]+$"
    SUBMISSION_ID_PATTERN = r"^[A-Z0-9]+$"

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        return bool(re.match(ClappiaInputValidator.EMAIL_PATTERN, email.strip()))

    @staticmethod
    def validate_email_list(email_ids: List[str]) -> Tuple[bool, str, List[str]]:
        """Validate a list of email addresses and return valid ones"""
        if not isinstance(email_ids, list):
            return False, "email_ids must be a list", []

        if not email_ids:
            return False, "email_ids cannot be empty", []

        valid_emails = []
        invalid_emails = []

        for email in email_ids:
            if not isinstance(email, str):
                invalid_emails.append(str(email))
                continue

            if ClappiaInputValidator.validate_email(email.strip()):
                valid_emails.append(email.strip())
            else:
                invalid_emails.append(email)

        if not valid_emails:
            return (
                False,
                f"No valid email addresses found. Invalid emails: {invalid_emails}",
                [],
            )

        if invalid_emails:
            return (
                True,
                f"Some emails were invalid and skipped: {invalid_emails}",
                valid_emails,
            )

        return True, "", valid_emails

    @staticmethod
    def validate_app_id(app_id: str) -> Tuple[bool, str]:
        """Validate Clappia app ID format"""
        if not app_id or not isinstance(app_id, str) or not app_id.strip():
            return False, "App ID is required and cannot be empty"

        if not re.match(ClappiaInputValidator.APP_ID_PATTERN, app_id.strip()):
            return False, "App ID must contain only uppercase letters and numbers"

        return True, ""

    @staticmethod
    def validate_submission_id(submission_id: str) -> Tuple[bool, str]:
        """Validate Clappia submission ID format"""
        if (
            not submission_id
            or not isinstance(submission_id, str)
            or not submission_id.strip()
        ):
            return False, "Submission ID is required and cannot be empty"

        if not re.match(
            ClappiaInputValidator.SUBMISSION_ID_PATTERN, submission_id.strip()
        ):
            return (
                False,
                "Submission ID must contain only uppercase letters and numbers",
            )

        return True, ""
