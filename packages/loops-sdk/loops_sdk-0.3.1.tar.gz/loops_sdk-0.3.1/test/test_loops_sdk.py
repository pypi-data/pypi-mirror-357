"""
Tests for the Loops SDK module.
This test suite mirrors the testing patterns from the existing Loops SDKs,
providing comprehensive coverage of the SDK functionality.
"""

import unittest
import os
from unittest.mock import Mock, patch
import requests

from loops_sdk import (
    LoopsEmail,
    APIError,
    RateLimitExceededError,
    ValidationError,
    LoopsClient,
    Attachment,
)


class TestLoopsEmail(unittest.TestCase):
    """Test the LoopsEmail class."""

    def test_loops_email_to_dict(self):
        """Test that LoopsEmail converts to dictionary correctly."""
        attachment = Attachment(
            filename="test.pdf", content_type="application/pdf", data="base64data"
        )

        email = LoopsEmail(
            email="test@example.com",
            transactional_id="test-id",
            add_to_audience=True,
            data_variables={"name": "John"},
            attachments=[attachment],
        )

        result = email.to_dict()

        expected = {
            "email": "test@example.com",
            "transactionalId": "test-id",
            "addToAudience": True,
            "dataVariables": {"name": "John"},
            "attachments": [
                {
                    "filename": "test.pdf",
                    "contentType": "application/pdf",
                    "data": "base64data",
                }
            ],
        }

        self.assertEqual(result, expected)

    def test_loops_email_empty_attachments(self):
        """Test LoopsEmail with empty attachments."""
        email = LoopsEmail(
            email="test@example.com",
            transactional_id="test-id",
            add_to_audience=False,
            data_variables={},
            attachments=[],
        )

        result = email.to_dict()
        self.assertEqual(result["attachments"], [])


class TestLoopsClient(unittest.TestCase):
    """Test the LoopsClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_api_key = "test-api-key"
        self.client = LoopsClient(api_key=self.test_api_key)
        # Patcher for requests.Session.request used by _make_query
        self.request_patcher = patch("requests.Session.request")
        self.mock_request = self.request_patcher.start()

    def tearDown(self):
        self.request_patcher.stop()

    def test_client_initialization_with_api_key(self):
        """Test client initialization with provided API key."""
        client = LoopsClient(api_key="test-key")
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.session.headers["Authorization"], "Bearer test-key")
        self.assertEqual(client.session.headers["Content-Type"], "application/json")

    @patch.dict(os.environ, {"LOOPS_TOKEN": "env-api-key"})
    def test_client_initialization_from_env(self):
        """Test client initialization from environment variable."""
        client = LoopsClient()
        self.assertEqual(client.api_key, "env-api-key")

    def test_client_initialization_no_api_key(self):
        """Test client initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                LoopsClient()
            self.assertIn("Loops API key is required", str(context.exception))

    # ------------------------------------------------------------------
    # New tests mirrored from TypeScript SDK suite
    # ------------------------------------------------------------------
    def test_test_api_key_success(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "teamName": "Test Team"}
        mock_resp.content = b'{"success":true}'
        self.mock_request.return_value = mock_resp

        result = self.client.test_api_key()
        self.assertEqual(result, {"success": True, "teamName": "Test Team"})
        self.mock_request.assert_called_once()
        self.assertIn("v1/api-key", self.mock_request.call_args[0][1])  # URL argument

    def test_test_api_key_invalid(self):
        mock_resp = Mock()
        mock_resp.ok = False
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"error": "Invalid API key"}
        mock_resp.content = b'{"error":"Invalid API key"}'
        self.mock_request.return_value = mock_resp

        with self.assertRaises(APIError):
            self.client.test_api_key()

    def test_test_api_key_rate_limited(self):
        mock_resp = Mock()
        mock_resp.ok = False
        mock_resp.status_code = 429
        mock_resp.headers = {"x-ratelimit-limit": "10", "x-ratelimit-remaining": "0"}
        self.mock_request.return_value = mock_resp

        with self.assertRaises(RateLimitExceededError) as ctx:
            self.client.test_api_key()
        self.assertEqual(ctx.exception.limit, 10)
        self.assertEqual(ctx.exception.remaining, 0)

    def test_test_api_key_network_error(self):
        self.mock_request.side_effect = requests.ConnectionError("Network error")
        with self.assertRaises(requests.ConnectionError):
            self.client.test_api_key()

    # -------------------------- create_contact ---------------------------
    def test_create_contact_email_only(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "id": "123"}
        mock_resp.content = b'{"success":true,"id":"123"}'
        self.mock_request.return_value = mock_resp

        res = self.client.create_contact("test@example.com")
        self.assertEqual(res["id"], "123")
        payload = self.mock_request.call_args[1]["json"]
        self.assertEqual(payload["email"], "test@example.com")

    def test_create_contact_with_properties(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "id": "123"}
        mock_resp.content = b'{"success":true}'
        self.mock_request.return_value = mock_resp

        props = {"name": "John", "age": 30, "isActive": True}
        res = self.client.create_contact("test@example.com", props)
        self.assertTrue(res["success"])
        payload = self.mock_request.call_args[1]["json"]
        for k, v in props.items():
            self.assertEqual(payload[k], v)

    def test_create_contact_api_error(self):
        mock_resp = Mock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.json.return_value = {
            "success": False,
            "message": "Contact with this email already exists",
        }
        mock_resp.content = b'{"success":false}'
        self.mock_request.return_value = mock_resp

        with self.assertRaises(APIError):
            self.client.create_contact("existing@example.com")

    def test_create_contact_invalid_email(self):
        with self.assertRaises(TypeError):
            self.client.create_contact("not-an-email")

    # -------------------------- update_contact ---------------------------
    def test_update_contact_success(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "id": "123"}
        mock_resp.content = b'{"success":true}'
        self.mock_request.return_value = mock_resp

        props = {"firstName": "John", "lastName": "Doe"}
        res = self.client.update_contact("test@example.com", props)
        self.assertEqual(res["id"], "123")
        payload = self.mock_request.call_args[1]["json"]
        for k, v in props.items():
            self.assertEqual(payload[k], v)

    def test_update_contact_invalid_email(self):
        with self.assertRaises(TypeError):
            self.client.update_contact("not-an-email", {})

    # ----------------------- create_contact_property ----------------------
    def test_create_contact_property_success(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True}
        mock_resp.content = b'{"success":true}'
        self.mock_request.return_value = mock_resp

        res = self.client.create_contact_property("customField", "string")
        self.assertTrue(res["success"])
        payload = self.mock_request.call_args[1]["json"]
        self.assertEqual(payload["name"], "customField")
        self.assertEqual(payload["type"], "string")

    def test_create_contact_property_invalid_type(self):
        with self.assertRaises(ValidationError):
            self.client.create_contact_property("field", "invalid")

    # ------------------------------- send_event ---------------------------
    def test_send_event_email(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True}
        mock_resp.content = b'{"success":true}'
        self.mock_request.return_value = mock_resp

        res = self.client.send_event(event_name="test_event", email="test@example.com")
        self.assertTrue(res["success"])
        payload = self.mock_request.call_args[1]["json"]
        self.assertEqual(payload["eventName"], "test_event")
        self.assertEqual(payload["email"], "test@example.com")

    def test_send_event_missing_identifiers(self):
        with self.assertRaises(ValidationError):
            self.client.send_event(event_name="test_event")

    # ------------------------ get_transactional_emails ---------------------
    def test_list_transactional_emails(self):
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pagination": {"totalResults": 0, "returnedResults": 0, "perPage": 20, "totalPages": 0},
            "data": [],
        }
        mock_resp.content = b'{"pagination": {}}'
        self.mock_request.return_value = mock_resp

        res = self.client.get_transactional_emails()
        self.assertIn("pagination", res)
        self.mock_request.assert_called_once()


if __name__ == "__main__":
    unittest.main()