import json
from typing import Dict, Any, Optional, Tuple
from clappia_tools._utils.api_utils import ClappiaAPIUtils
from clappia_tools._utils.validators import ClappiaInputValidator
from clappia_tools._utils.logging_utils import get_logger

logger = get_logger(__name__)


class ClappiaClient:
    """
    Unified client for all Clappia API operations
    
    This is the main interface for interacting with Clappia APIs.
    All functionality is accessible through this client.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        workplace_id: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize Clappia client

        Args:
            api_key: Clappia API key
            base_url: API base URL
            workplace_id: Workspace ID
            timeout: Request timeout in seconds
        """
        self.api_utils = ClappiaAPIUtils(api_key, base_url, workplace_id, timeout)

    def create_submission(self, app_id: str, data: Dict[str, Any], email: str) -> str:
        """
        Create a new submission in Clappia app

        Args:
            app_id: Application ID
            data: Submission data
            email: User email

        Returns:
            Formatted result string
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        if not email or not email.strip():
            return "Error: email is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(email):
            return "Error: email must be a valid email address"

        if not isinstance(data, dict):
            return "Error: data must be a dictionary"

        if not data:
            return "Error: data cannot be empty - at least one field is required"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "requestingUserEmailAddress": email.strip(),
            "data": data,
        }

        logger.info(
            f"Creating submission for app_id: {app_id} with data: {data} and email: {email}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/create", data=payload
        )

        if not success:
            return f"Error: {error_message}"

        submission_id = response_data.get("submissionId") if response_data else None

        submission_info = {
            "submissionId": submission_id,
            "status": "created",
            "appId": app_id,
            "owner": email,
            "fieldsSubmitted": len(data),
        }

        return f"Successfully created submission:\n\nSUMMARY:\n{json.dumps(submission_info, indent=2)}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"

    def edit_submission(
        self, app_id: str, submission_id: str, data: Dict[str, Any], email: str
    ) -> str:
        """
        Edit an existing submission in Clappia app

        Args:
            app_id: Application ID
            submission_id: Submission ID to edit
            data: Updated data
            email: User email

        Returns:
            Formatted result string
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        is_valid, error_msg = ClappiaInputValidator.validate_submission_id(
            submission_id
        )
        if not is_valid:
            return f"Error: Invalid submission_id - {error_msg}"

        if not email or not email.strip():
            return "Error: email is required and cannot be empty"

        if not ClappiaInputValidator.validate_email(email):
            return "Error: email must be a valid email address"

        if not isinstance(data, dict):
            return "Error: data must be a dictionary"

        if not data:
            return "Error: data cannot be empty - at least one field is required"

        payload = {
            "workplaceId": self.api_utils.workplace_id,
            "appId": app_id.strip(),
            "submissionId": submission_id.strip(),
            "requestingUserEmailAddress": email.strip(),
            "data": data,
        }

        logger.info(
            f"Editing submission {submission_id} for app_id: {app_id} with data: {data} and email: {email}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/edit", data=payload
        )

        if not success:
            return f"Error: {error_message}"

        edit_info = {
            "submissionId": submission_id,
            "appId": app_id,
            "requestingUser": email,
            "fieldsUpdated": len(data),
            "updatedFields": list(data.keys()),
            "status": "updated",
        }

        return f"Successfully edited submission:\n\nSUMMARY:\n{json.dumps(edit_info, indent=2)}\n\nFULL RESPONSE:\n{json.dumps(response_data, indent=2)}"

    def get_app_definition(
        self,
        app_id: str,
        language: str = "en",
        strip_html: bool = True,
        include_tags: bool = True,
    ) -> str:
        """
        Get application definition from Clappia

        Args:
            app_id: Application ID
            language: Language code
            strip_html: Whether to strip HTML
            include_tags: Whether to include tags

        Returns:
            Formatted result string
        """
        is_valid, error_msg = ClappiaInputValidator.validate_app_id(app_id)
        if not is_valid:
            return f"Error: Invalid app_id - {error_msg}"

        params = {
            "appId": app_id.strip(),
            "workplaceId": self.api_utils.workplace_id,
            "language": language,
            "stripHtml": str(strip_html).lower(),
            "includeTags": str(include_tags).lower(),
        }

        logger.info(
            f"Getting app definition for app_id: {app_id} with params: {params}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="GET",
            endpoint="appdefinition-external/getAppDefinition",
            params=params,
        )

        if not success:
            return f"Error: {error_message}"

        app_info = {
            "appId": response_data.get("appId") if response_data else None,
            "version": response_data.get("version") if response_data else None,
            "state": response_data.get("state") if response_data else None,
            "pageCount": len(response_data.get("pageIds", [])) if response_data else 0,
            "sectionCount": (
                len(response_data.get("sectionIds", [])) if response_data else 0
            ),
            "fieldCount": (
                len(response_data.get("fieldDefinitions", {})) if response_data else 0
            ),
            "appName": (
                response_data.get("metadata", {}).get("sectionName", "Unknown")
                if response_data
                else "Unknown"
            ),
            "description": (
                response_data.get("metadata", {}).get("description", "")
                if response_data
                else ""
            ),
        }

        return f"Successfully retrieved app definition:\n\nSUMMARY:\n{json.dumps(app_info, indent=2)}\n\nFULL DEFINITION:\n{json.dumps(response_data, indent=2)}"