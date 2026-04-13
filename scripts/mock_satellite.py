import asyncio
import json
import sys
from typing import Dict, Any
from src.core.schemas import HubRequest

# Mock settings
MOCK_SATELLITE_URL = "https://script.google.com/macros/s/AKfycb.../exec"
SHARED_SECRET = "test_secret"

async def mock_call_satellite(action: str, params: Dict[str, Any]):
    """
    Simulates the Hub calling a Satellite.
    In a real scenario, this would use httpx to call the GAS Web App.
    Here we just print the payload that WOULD be sent.
    """
    payload = HubRequest(
        auth_key=SHARED_SECRET,
        action=action,
        source="manual",
        params=params
    )
    
    print(f"🚀 MOCK HUB -> SATELLITE")
    print(f"URL: {MOCK_SATELLITE_URL}")
    print(f"Payload:\n{json.dumps(payload.model_dump(), indent=2)}")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "process_gym_receipts"
    
    asyncio.run(mock_call_satellite(
        action=action,
        params={"chat_id": 123456789, "text": "/test"}
    ))
