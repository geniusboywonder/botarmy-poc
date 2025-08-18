#!/usr/bin/env python3
"""
Quick API Test Script for BotArmy POC
Tests all the new global endpoints to ensure they work
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/health",
        "/api/agents", 
        "/api/tasks",
        "/api/artifacts",
        "/api/messages", 
        "/api/logs"
    ]
    
    async with aiohttp.ClientSession() as session:
        print(f"🧪 Testing BotArmy POC API Endpoints - {datetime.now()}")
        print("=" * 60)
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url) as response:
                    status = response.status
                    data = await response.json()
                    
                    if status == 200:
                        print(f"✅ {endpoint}")
                        if endpoint == "/api/agents":
                            print(f"   Agents found: {len(data.get('agents', []))}")
                        elif endpoint == "/api/tasks":
                            print(f"   Tasks found: {len(data.get('tasks', []))}")
                        elif endpoint == "/api/messages":
                            print(f"   Messages found: {len(data.get('messages', []))}")
                        elif endpoint == "/api/logs":
                            print(f"   Log entries: {len(data.get('logs', []))}")
                    else:
                        print(f"❌ {endpoint} - Status {status}")
                        print(f"   Error: {data}")
                        
            except Exception as e:
                print(f"❌ {endpoint} - Connection failed: {e}")
        
        print("=" * 60)
        print("🏁 API Tests Complete")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
