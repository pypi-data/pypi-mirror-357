import os

os.environ["AF_RETRY_MAX"] = "2"
os.environ["AF_RETRY_BASE_DELAY"] = "0.1"
import pytest
from af_client_sdk.client import ActiveFenceClient
from af_client_sdk.types import AnalysisContext, GuardedResult
from aioresponses import aioresponses
from aiohttp import ClientConnectionError

pytestmark = pytest.mark.citest


@pytest.mark.asyncio
async def test_evaluate_prompt_async():
    with aioresponses() as mocker:
        mocker.post(
            url="https://apis.activefence.com/v1/evaluate/message",
            status=200,
            payload={
                "action": "ALLOW",
                "detections": [],
            },
        )

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = await client.evaluate_prompt(prompt="test prompt", context=context)

        assert isinstance(result, GuardedResult)
        assert not result.blocked
        assert result.reason is None
        assert result.final_response == "test prompt"


@pytest.mark.asyncio
async def test_evaluate_response_async():
    with aioresponses() as mocker:
        mocker.post(
            url="https://apis.activefence.com/v1/evaluate/message",
            status=200,
            payload={
                "action": "ALLOW",
                "detections": [],
            },
        )

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )
        result = await client.evaluate_response(response="test response", context=context)

        assert isinstance(result, GuardedResult)
        assert not result.blocked
        assert result.reason is None
        assert result.final_response == "test response"


@pytest.mark.asyncio
async def test_evaluate_response_timeout():
    with aioresponses() as mocker:
        mocker.post(url="https://apis.activefence.com/v1/evaluate/message", timeout=True)

        client = ActiveFenceClient(api_key="test_api_key", app_name="test_app")
        context = AnalysisContext(
            session_id="test_session",
            user_id="test_user",
            provider="test_provider",
            model_name="test_model",
            model_version="test_version",
            platform="test_platform",
        )

        with pytest.raises(ClientConnectionError):
            await client.evaluate_response(response="test response", context=context)
