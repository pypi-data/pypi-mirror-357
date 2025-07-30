from langchain.tools import tool
from typing import Dict, Any
from clappia_tools.client.clappia_client import ClappiaClient


@tool(parse_docstring=True)
def edit_clappia_submission(
    app_id: str,
    submission_id: str,
    data: Dict[str, Any],
    email: str,
) -> str:
    """Edits an existing Clappia submission by updating specified field values.

    Modifies field data in an existing submission record while preserving other field values.
    Use this to update form data, correct information, or add missing details to submissions.

    Args:
        app_id: Application ID in uppercase letters and numbers format (e.g., MFX093412). Use this to specify which Clappia app contains the submission.
        submission_id: Unique identifier of the submission to update (e.g., HGO51464561). This identifies the specific submission record to modify.
        data: Dictionary of field data to update. Keys should match field names from the app definition, values should match expected field types. Only specified fields will be updated. Example: {"employee_name": "Jane Doe", "department": "Marketing", "salary": 80000, "start_date": "20-02-2025"}.
        email: Email address of the user requesting the edit. This user must have permission to modify the submission. Must be a valid email format.

    Returns:
        str: Formatted response with edit details and status
    """
    client = ClappiaClient()
    return client.edit_submission(app_id, submission_id, data, email)
