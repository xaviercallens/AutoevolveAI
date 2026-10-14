import os
import httpx
from typing import Dict, Any

class LayaServerlessClient:
    """Client for the Serverless Laya Cloud Run Endpoint."""
    
    def __init__(self, endpoint_url: str = None, api_key: str = None):
        self.endpoint_url = endpoint_url or os.environ.get(
            "LAYA_ENDPOINT_URL", 
            "https://anse-serverless-laya-cfhmhmvv5a-uc.a.run.app"
        )
        self.api_key = api_key or os.environ.get(
            "LAYA_API_KEY", 
            "sk-anse-iJKO0vrEKroWRzDSDXJSRWbqkWepblp3"
        )
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def health_check(self) -> Dict[str, Any]:
        """Fetches the telemetry and health status of the endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.endpoint_url}/health", 
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()

    async def assist(self, prompt: str) -> Dict[str, Any]:
        """Sends a prompt to the Laya inference endpoint."""
        async with httpx.AsyncClient() as client:
            # We use a longer timeout here because cold starts can take up to 15s
            response = await client.post(
                f"{self.endpoint_url}/v1/assist",
                headers=self.headers,
                json={"prompt": prompt},
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()

if __name__ == "__main__":
    import asyncio
    
    async def main():
        client = LayaServerlessClient()
        print("Checking health...")
        health = await client.health_check()
        print("Health Status:", health)
        
        print("\nTesting inference...")
        result = await client.assist("Hello, Laya! Are you online?")
        print("Response:", result)
        
    asyncio.run(main())
