from clappia_tools._utils.validators import ClappiaInputValidator, ClappiaValidator


class TestClappiaInputValidator:
    def test_validate_email_valid(self):
        assert ClappiaInputValidator.validate_email("test@example.com") == True
        assert (
            ClappiaInputValidator.validate_email("user.name+tag@domain.co.uk") == True
        )

    def test_validate_email_invalid(self):
        assert ClappiaInputValidator.validate_email("invalid-email") == False
        assert ClappiaInputValidator.validate_email("@domain.com") == False
        assert ClappiaInputValidator.validate_email("") == False
        assert ClappiaInputValidator.validate_email(None) == False

    def test_validate_app_id_valid(self):
        is_valid, error = ClappiaInputValidator.validate_app_id("MFX093412")
        assert is_valid == True
        assert error == ""

    def test_validate_app_id_invalid(self):
        is_valid, error = ClappiaInputValidator.validate_app_id("invalid-id")
        assert is_valid == False
        assert "uppercase letters and numbers" in error

    def test_validate_submission_id_valid(self):
        is_valid, error = ClappiaInputValidator.validate_submission_id("HGO51464561")
        assert is_valid == True
        assert error == ""
