import pytest
import asyncio
from scripts.social_command_center import StitchMCPClient, SocialMediaCommandCenter

@pytest.fixture
def smccc():
    return SocialMediaCommandCenter(api_key="TEST_KEY")

@pytest.mark.asyncio
async def test_stitch_mcp_client_connect():
    client = StitchMCPClient("TEST_KEY")
    result = await client.connect()
    assert result is True
    assert client.headers["X-Goog-Api-Key"] == "TEST_KEY"

@pytest.mark.asyncio
async def test_reputation_repair_protocol(smccc):
    karma_gained = await smccc.run_reputation_repair_protocol()
    assert karma_gained == 15

@pytest.mark.asyncio
async def test_dissemination_campaign(smccc):
    success = await smccc.run_dissemination_campaign()
    assert success is True
