from langchain.tools import tool
from typing import Dict, Any
from clappia_tools.client.clappia_client import ClappiaClient


@tool(parse_docstring=True)
def create_clappia_submission(
    app_id: str,
    data: Dict[str, Any],
    email: str,
) -> str:
    """Creates a new submission in a Clappia application with specified field data.

    Submits form data to create a new record in the specified Clappia app.
    Use this to programmatically add entries, automate data collection, or integrate external systems.

    Args:
        app_id: Application ID in uppercase letters and numbers format (e.g., MFX093412). Use this to specify which Clappia app to create the submission in.
        data: Dictionary of field data to submit. Keys should match field names from the app definition, values should match expected field types. Example: {"employee_name": "John Doe", "department": "Engineering", "salary": 75000, "start_date": "20-02-2025"}.
        email: Email address of the user creating the submission. This user becomes the submission owner and must have access to the specified app. Must be a valid email format.

    Returns:
        str: Formatted response with submission details and status
    """
    client = ClappiaClient()
    return client.create_submission(app_id, data, email)
