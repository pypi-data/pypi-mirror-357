import os

os.environ["AF_RETRY_MAX"] = "2"
os.environ["AF_RETRY_BASE_DELAY"] = "0.1"
import unittest
from unittest.mock import patch, MagicMock
import responses
from requests.exceptions import ConnectTimeout
from af_client_sdk.client import ActiveFenceClient
from af_client_sdk.types import AnalysisContext, GuardedResult
import pytest

pytestmark = pytest.mark.citest


class TestActiveFenceClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.app_name = "test_app"
        self.client = ActiveFenceClient(api_key=self.api_key, app_name=self.app_name)

    @patch("af_client_sdk.client.requests.post")
    def test_sync_internal_call_success(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "action": "ALLOW",
            "detections": [],
        }
        mock_post.return_value = mock_response

        result = self.client.sync_internal_call(
            text="test text",
            type="prompt",
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model="test_model",
            version="test_version",
            platform="test_platform",
        )

        self.assertIsInstance(result, GuardedResult)
        self.assertFalse(result.blocked)
        self.assertIsNone(result.reason)
        self.assertEqual(result.final_response, "test text")

    @patch("af_client_sdk.client.requests.post")
    def test_sync_internal_call_blocked(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "action": "BLOCK",
            "detections": [{"type": "test_reason"}],
        }
        mock_post.return_value = mock_response

        result = self.client.sync_internal_call(
            text="test text",
            type="prompt",
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model="test_model",
            version="test_version",
            platform="test_platform",
        )

        self.assertIsInstance(result, GuardedResult)
        self.assertTrue(result.blocked)
        self.assertEqual(result.reason, "test_reason")
        self.assertEqual(result.final_response, "BLOCKED")

    @patch("af_client_sdk.client.requests.post")
    def test_sync_internal_call_mask(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "action": "MASK",
            "action_text": "***** text",
            "detections": [{"type": "test_reason"}],
        }
        mock_post.return_value = mock_response

        result = self.client.sync_internal_call(
            text="test text",
            type="prompt",
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model="test_model",
            version="test_version",
            platform="test_platform",
        )

        self.assertIsInstance(result, GuardedResult)
        self.assertFalse(result.blocked)
        self.assertEqual(result.reason, "test_reason")
        self.assertEqual(result.final_response, "***** text")

    @patch("af_client_sdk.client.requests.post")
    def test_evaluate_prompt(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "action": "ALLOW",
            "detections": [],
        }
        mock_post.return_value = mock_response

        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = self.client.evaluate_prompt_sync(prompt="test prompt", context=context)

        self.assertIsInstance(result, GuardedResult)
        self.assertFalse(result.blocked)
        self.assertIsNone(result.reason)
        self.assertEqual(result.final_response, "test prompt")

    @patch("af_client_sdk.client.requests.post")
    def test_evaluate_response(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "action": "ALLOW",
            "detections": [],
        }
        mock_post.return_value = mock_response

        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = self.client.evaluate_response_sync(response="test response", context=context)

        self.assertIsInstance(result, GuardedResult)
        self.assertFalse(result.blocked)
        self.assertIsNone(result.reason)
        self.assertEqual(result.final_response, "test response")

    @responses.activate
    def test_sync_internal_call_timeout(self):
        # Simulate a timeout exception
        responses.add(
            responses.POST,
            "https://apis.activefence.com/v1/evaluate/message",
            body=ConnectTimeout(),
        )

        with self.assertRaises(ConnectTimeout):
            self.client.sync_internal_call(
                text="test text",
                type="prompt",
                session_id="test_session",
                user_id="test_user",
                provider="test_provider",
                model="test_model",
                version="test_version",
                platform="test_platform",
            )
