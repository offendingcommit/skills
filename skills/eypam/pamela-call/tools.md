# Tool Execution

Pamela can call your custom tools during a live call. Tools are defined with JSON Schema and executed via webhooks.

## Register a Tool

```typescript
await client.registerTool({
  name: 'check_order_status',
  description: 'Look up an order by ID',
  input_schema: {
    type: 'object',
    properties: { order_id: { type: 'string' } },
    required: ['order_id'],
  },
  output_schema: {
    type: 'object',
    properties: {
      status: { type: 'string' },
      eta_days: { type: 'number' },
    },
  },
  timeout_seconds: 60, // 1-300
});
```

## Tool Webhook Payload

```json
{
  "tool_name": "check_order_status",
  "arguments": { "order_id": "A123" },
  "call_id": "call_123",
  "correlation_id": "tool_456"
}
```

## Tool Webhook Response

Return a JSON object with `result`:

```json
{
  "result": { "status": "shipped", "eta_days": 2 },
  "correlation_id": "tool_456"
}
```

## Tips

- Keep tool execution fast and reliable
- Use `correlation_id` to map requests to responses
- Validate input against your JSON Schema before execution
