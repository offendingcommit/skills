# Webhooks

Pamela sends webhooks for call lifecycle events and transcript updates.

## Events

- `call.queued`
- `call.started`
- `call.completed`
- `call.failed`
- `call.transcript_update`

## Signature Verification

Webhooks include a signature header: `X-Pamela-Signature`.

### JavaScript (Express)

```typescript
import { PamelaClient } from '@thisispamela/sdk';
import express from 'express';

const app = express();
const WEBHOOK_SECRET = 'your_webhook_secret';

app.post('/webhooks/pamela', express.json(), (req, res) => {
  const signature = req.headers['x-pamela-signature'] as string;
  const payload = req.body;

  if (!PamelaClient.verifyWebhookSignature(payload, signature, WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }

  // Handle event
  res.status(200).send('OK');
});
```

### Python (Flask)

```python
from flask import Flask, request
from pamela import verify_webhook_signature

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

@app.route("/webhooks/pamela", methods=["POST"])
def handle_webhook():
    signature = request.headers.get("X-Pamela-Signature")
    payload = request.json

    if not verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        return {"error": "Invalid signature"}, 401

    # Handle event
    return {"status": "ok"}, 200
```

## Payload Fields (Common)

- `event` (string)
- `call_id` (string)
- `status` (string)
- `timestamp` (ISO-8601 string)
- `transcript` (array, on `call.transcript_update` and `call.completed`)
