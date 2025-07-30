from unittest.mock import patch
from clappia_tools import ClappiaClient


class TestClappiaClient:
    def test_init_with_defaults(self):
        client = ClappiaClient()
        assert client.api_utils is not None

    def test_init_with_custom_params(self):
        client = ClappiaClient(
            api_key="test_key",
            base_url="https://test.com",
            workplace_id="TEST123",
            timeout=60,
        )
        assert client.api_utils.api_key == "test_key"
        assert client.api_utils.base_url == "https://test.com"
        assert client.api_utils.workplace_id == "TEST123"
        assert client.api_utils.timeout == 60

    def test_create_submission_validation_error(self):
        client = ClappiaClient()
        result = client.create_submission("invalid-id", {}, "test@example.com")
        assert "Error: Invalid app_id" in result

    def test_create_submission_empty_email(self):
        client = ClappiaClient()
        result = client.create_submission("MFX093412", {"test": "data"}, "")
        assert "Error: email is required" in result

    def test_create_submission_invalid_email(self):
        client = ClappiaClient()
        result = client.create_submission(
            "MFX093412", {"test": "data"}, "invalid-email"
        )
        assert "Error: email must be a valid email address" in result

    def test_create_submission_empty_data(self):
        client = ClappiaClient()
        result = client.create_submission("MFX093412", {}, "test@example.com")
        assert "Error: data cannot be empty" in result

    @patch("clappia_tools._utils.api_utils.ClappiaAPIUtils.make_request")
    def test_create_submission_success(self, mock_request):
        # Mock successful API response
        mock_request.return_value = (True, None, {"submissionId": "TEST123"})

        client = ClappiaClient()
        result = client.create_submission(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

        assert "Successfully created submission" in result
        assert "TEST123" in result
        mock_request.assert_called_once()
