from unittest.mock import patch, Mock
from clappia_tools._tools.create_submission import create_clappia_submission
from clappia_tools._tools.edit_submission import edit_clappia_submission
from clappia_tools._tools.get_definition import get_app_definition


class TestToolsIntegration:
    @patch("clappia_tools._tools.create_submission.ClappiaClient")
    def test_create_submission_tool(self, mock_client_class):
        # Setup mock
        mock_client = Mock()
        mock_client.create_submission.return_value = (
            "Success: Created submission TEST123"
        )
        mock_client_class.return_value = mock_client

        # Call tool
        result = create_clappia_submission.invoke(
            {
                "app_id": "MFX093412",
                "data": {"name": "Test User"},
                "email": "test@example.com",
            }
        )

        # Verify
        assert "Success: Created submission TEST123" in result
        mock_client.create_submission.assert_called_once_with(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

    @patch("clappia_tools._tools.get_definition.ClappiaClient")
    def test_get_definition_tool(self, mock_client_class):
        # Setup mock
        mock_client = Mock()
        mock_client.get_app_definition.return_value = "App definition for MFX093412"
        mock_client_class.return_value = mock_client

        # Call tool
        result = get_app_definition.invoke({"app_id": "MFX093412"})

        # Verify
        assert "App definition for MFX093412" in result
        mock_client.get_app_definition.assert_called_once_with(
            "MFX093412", "en", True, True
        )
