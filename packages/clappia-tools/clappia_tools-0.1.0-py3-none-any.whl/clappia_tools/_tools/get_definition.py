from langchain.tools import tool
from typing import Dict, Any
from clappia_tools.client.clappia_client import ClappiaClient


@tool(parse_docstring=True)
def get_app_definition(
    app_id: str,
    language: str = "en",
    strip_html: bool = True,
    include_tags: bool = True,
) -> str:
    """Fetches complete definition of a Clappia application including forms, fields, sections, and metadata.

    Retrieves structure and configuration of a Clappia app to understand available fields,
    validation rules, and workflow logic before creating charts, filtering submissions, or planning integrations.

    Args:
        app_id: Unique application identifier in uppercase letters and numbers format (e.g., QGU236634). Use this to specify which Clappia app definition to retrieve.
        language: Language code for field labels and translations. Available options: "en" (English, default), "es" (Spanish), "fr" (French), "de" (German). Use "es" for Spanish reports or "fr" for French localization.
        strip_html: Whether to remove HTML formatting from text fields. True (default) removes HTML tags for clean text, False preserves HTML formatting for display purposes.
        include_tags: Whether to include metadata tags in response. True (default) includes full metadata tags, False returns basic structure only for lightweight responses.

    Returns:
        str: Formatted response with app definition details and complete structure
    """
    client = ClappiaClient()
    return client.get_app_definition(app_id, language, strip_html, include_tags)
