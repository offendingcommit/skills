#!/usr/bin/env python3
import requests
import json
import sys

def onboard(tenant_name=None):
    url = "https://api.thrd.email/v1/onboarding/instant"
    payload = {}
    if tenant_name:
        payload["tenant_name"] = tenant_name
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    t_name = sys.argv[1] if len(sys.argv) > 1 else None
    onboard(t_name)
