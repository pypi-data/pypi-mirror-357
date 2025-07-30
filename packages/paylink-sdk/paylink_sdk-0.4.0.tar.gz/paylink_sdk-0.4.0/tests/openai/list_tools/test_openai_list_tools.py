import pytest
from paylink_sdk.openai_adapter.toolkit import PayLinkClient
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_list_openai_tools_returns_tools():
    client = PayLinkClient()
    tools = await client.list_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert all("name" in tool for tool in tools) 
