import httpx
import asyncio

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        if response.status_code == 200:
            print(response.json())

if __name__ == "__main__":
    asyncio.run(fetch_data())