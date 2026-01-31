# JavaScript/TypeScript SDK

Package: `@thisispamela/sdk`

## Install

```bash
npm install @thisispamela/sdk
```

## Client Setup

```typescript
import { PamelaClient } from '@thisispamela/sdk';

const client = new PamelaClient({
  apiKey: 'pk_live_...',
  baseUrl: 'https://api.thisispamela.com', // optional
});
```

## Calls

```typescript
const call = await client.createCall({
  to: '+1234567890',
  task: 'Schedule a meeting for next week',
  locale: 'en-US',
  max_duration_seconds: 299,
  voice: 'female',
  agent_name: 'Pamela',
  caller_name: 'John from Acme',
});

const status = await client.getCall(call.id);
const list = await client.listCalls({ status: 'completed', limit: 50 });
await client.cancelCall(call.id);
await client.hangupCall(call.id);
```

## Tools

```typescript
await client.registerTool({
  name: 'check_order_status',
  description: 'Look up an order by ID',
  input_schema: {
    type: 'object',
    properties: {
      order_id: { type: 'string' },
    },
    required: ['order_id'],
  },
  output_schema: {
    type: 'object',
    properties: {
      status: { type: 'string' },
      eta_days: { type: 'number' },
    },
  },
  timeout_seconds: 60,
});

const tools = await client.listTools();
await client.deleteTool(tools[0].id);
```

## Usage

```typescript
const usage = await client.usage.get(); // current month
const janUsage = await client.usage.get('2024-01');
```

## Webhook Signature Verification

```typescript
import { PamelaClient } from '@thisispamela/sdk';

const isValid = PamelaClient.verifyWebhookSignature(
  payload,
  signature, // from "X-Pamela-Signature"
  webhookSecret
);
```

## Errors

```typescript
import {
  PamelaError,
  AuthenticationError,
  SubscriptionError,
  RateLimitError,
  ValidationError,
  CallError,
} from '@thisispamela/sdk';

try {
  await client.createCall({ to: '+1234567890', task: 'Test' });
} catch (e) {
  if (e instanceof AuthenticationError) {
    // Invalid or missing API key
  } else if (e instanceof SubscriptionError) {
    // Billing or access issue
  } else if (e instanceof RateLimitError) {
    // Too many requests
  } else if (e instanceof ValidationError) {
    // Invalid input
  } else if (e instanceof CallError) {
    // Call-specific error
  } else if (e instanceof PamelaError) {
    // Other API errors
  }
}
```
