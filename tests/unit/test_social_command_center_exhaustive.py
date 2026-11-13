import pytest
import asyncio
from unittest.mock import patch, MagicMock
from scripts.social_command_center import StitchMCPClient, SocialMediaCommandCenter

@pytest.fixture
def api_key():
    return "TEST_KEY_EXHAUSTIVE"

@pytest.fixture
def smccc(api_key):
    return SocialMediaCommandCenter(api_key=api_key)

@pytest.mark.asyncio
async def test_stitch_mcp_client_init(api_key):
    client = StitchMCPClient(api_key)
    assert client.api_key == api_key
    assert client.server_url == "https://stitch.googleapis.com/mcp"
    assert client.headers["X-Goog-Api-Key"] == api_key

@pytest.mark.asyncio
async def test_stitch_mcp_client_connect(api_key):
    client = StitchMCPClient(api_key)
    assert await client.connect() is True

@pytest.mark.asyncio
async def test_stitch_mcp_client_broadcast(api_key):
    client = StitchMCPClient(api_key)
    assert await client.broadcast_post("Test Content", ["r/Test"]) is True

@pytest.mark.asyncio
async def test_stitch_mcp_client_fetch_analytics(api_key):
    client = StitchMCPClient(api_key)
    analytics = await client.fetch_analytics()
    assert analytics["views"] == 1024
    assert analytics["karma_delta"] == 15

@pytest.mark.asyncio
async def test_smccc_init(api_key):
    smccc = SocialMediaCommandCenter(api_key=api_key)
    assert smccc.stitch_client.api_key == api_key
    assert smccc.orchestrator is not None

@pytest.mark.asyncio
async def test_run_reputation_repair_protocol(smccc):
    with patch.object(smccc.stitch_client, 'broadcast_post', return_value=True) as mock_broadcast:
        with patch.object(smccc.stitch_client, 'fetch_analytics', return_value={"karma_delta": 25}) as mock_fetch:
            karma = await smccc.run_reputation_repair_protocol()
            assert karma == 25
            mock_broadcast.assert_called_once()
            mock_fetch.assert_called_once()

@pytest.mark.asyncio
async def test_run_dissemination_campaign(smccc):
    with patch.object(smccc.stitch_client, 'broadcast_post', return_value=True) as mock_broadcast:
        success = await smccc.run_dissemination_campaign()
        assert success is True
        mock_broadcast.assert_called_once()
