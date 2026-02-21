#!/usr/bin/env python3
"""Omie Webhook Receiver.

Usage:
    python3 omie_webhook.py --port 8089

Configure in Omie:
    Configurações → Integrações → Webhooks
    URL: http://your-server:8089/webhook/omie
"""

import json
import os
import sys
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
EVENTS_FILE = os.path.join(LOG_DIR, "webhook_events.jsonl")


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming Omie webhook events."""

    def do_POST(self):
        if self.path not in ("/webhook/omie", "/webhook"):
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "invalid JSON"}')
            return

        # Log the event
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topic": data.get("topic", "unknown"),
            "event": data.get("event", {}),
            "ping": data.get("ping", False),
        }

        os.makedirs(LOG_DIR, exist_ok=True)
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        print(f"[{event['timestamp']}] {event['topic']}: {json.dumps(event['event'], ensure_ascii=False)[:200]}")

        # Process event
        self.process_event(event)

        # Respond OK
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "running",
                "service": "omie-webhook",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }).encode())
            return

        if self.path == "/events":
            """List recent events."""
            events = []
            if os.path.exists(EVENTS_FILE):
                with open(EVENTS_FILE) as f:
                    lines = f.readlines()
                    events = [json.loads(l) for l in lines[-50:]]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(events, indent=2, ensure_ascii=False).encode())
            return

        self.send_response(404)
        self.end_headers()

    def process_event(self, event):
        """Process webhook event — extend with custom logic."""
        topic = event.get("topic", "")

        # Example handlers (customize as needed):
        if topic == "Ordem de Servico":
            print(f"  → Ordem de serviço event received")
        elif topic == "Pedido de Venda":
            print(f"  → Pedido de venda event received")
        elif topic == "Nota Fiscal":
            print(f"  → NF event received")
        elif topic == "Financas":
            print(f"  → Finance event received")
        elif topic == "Clientes":
            print(f"  → Client event received")
        elif event.get("ping"):
            print(f"  → Ping received (webhook test)")

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    parser = argparse.ArgumentParser(description="Omie Webhook Receiver")
    parser.add_argument("--port", type=int, default=8089, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), WebhookHandler)
    print(f"🔗 Omie Webhook Receiver running on {args.host}:{args.port}")
    print(f"   Webhook URL: http://your-server:{args.port}/webhook/omie")
    print(f"   Health: http://localhost:{args.port}/health")
    print(f"   Events: http://localhost:{args.port}/events")
    print(f"   Logs: {EVENTS_FILE}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹ Webhook receiver stopped")
        server.server_close()


if __name__ == "__main__":
    main()
