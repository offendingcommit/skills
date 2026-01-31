# Python SDK

Package: `thisispamela`

## Install

```bash
pip install thisispamela
```

## Client Setup

```python
from pamela import PamelaClient

client = PamelaClient(
    api_key="pk_live_...",
    base_url="https://api.thisispamela.com",  # optional
)
```

## Calls

```python
call = client.create_call(
    to="+1234567890",
    task="Schedule a meeting for next week",
    locale="en-US",
    max_duration_seconds=299,
    voice="female",
    agent_name="Pamela",
    caller_name="John from Acme",
)

status = client.get_call(call["id"])
calls = client.list_calls(status="completed", limit=50)
client.cancel_call(call["id"])
client.hangup_call(call["id"])
```

## Tools

```python
client.register_tool(
    name="check_order_status",
    description="Look up an order by ID",
    input_schema={
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"],
    },
    output_schema={
        "type": "object",
        "properties": {"status": {"type": "string"}, "eta_days": {"type": "number"}},
    },
    timeout_seconds=60,
)

tools = client.list_tools()
client.delete_tool(tools[0]["id"])
```

## Usage

```python
usage = client.usage.get()        # current month
jan_usage = client.usage.get("2024-01")
```

## Webhook Signature Verification

```python
from pamela import verify_webhook_signature

is_valid = verify_webhook_signature(payload, signature, webhook_secret)
```

## Tool Webhook Handler (Example)

```python
from flask import Flask, request
from pamela import verify_webhook_signature

app = Flask(__name__)

@app.route("/webhooks/pamela/tools", methods=["POST"])
def handle_tool_webhook():
    signature = request.headers.get("X-Pamela-Signature")
    payload = request.json

    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return {"error": "Invalid signature"}, 401

    tool_name = payload["tool_name"]
    arguments = payload["arguments"]
    correlation_id = payload["correlation_id"]

    if tool_name == "check_order_status":
        result = check_order_status(arguments.get("order_id"))
        return {"result": result, "correlation_id": correlation_id}

    return {"error": "Unknown tool"}, 400
```

## Errors

```python
from pamela import (
    PamelaError,
    AuthenticationError,
    SubscriptionError,
    RateLimitError,
    ValidationError,
    CallError,
)

try:
    client.create_call(to="+1234567890", task="Test call")
except AuthenticationError:
    pass
except SubscriptionError:
    pass
except RateLimitError:
    pass
except ValidationError:
    pass
except CallError:
    pass
except PamelaError:
    pass
```
