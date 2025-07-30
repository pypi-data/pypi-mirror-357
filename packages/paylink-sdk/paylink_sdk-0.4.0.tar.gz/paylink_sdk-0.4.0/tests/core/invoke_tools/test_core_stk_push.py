import pytest
from paylink_sdk import PayLinkClient
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_stk_push_invokes_successfully():
    client = PayLinkClient()

    tool_args = {
        "phone_number": "254797357665",
        "amount": 1,
        "account_reference": "invoice",
        "transaction_desc": "invoice-123",
        "transaction_type": "CustomerBuyGoodsOnline",
    }

    result = await client.call_tool("stk_push", tool_args)

    assert result is not None
    assert hasattr(result, "content")
    assert not result.isError
