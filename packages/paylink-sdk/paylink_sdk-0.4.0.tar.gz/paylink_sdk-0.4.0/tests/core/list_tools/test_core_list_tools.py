import pytest
from paylink_sdk import PayLinkClient
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_list_tools_returns_tools():
    client = PayLinkClient()
    tools = await client.list_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert all(hasattr(tool, "name") for tool in tools)
