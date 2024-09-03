import aiohttp
import asyncio


async def check_index():
    url = "http://elasticsearch:9200/documents/_search"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                print(result)
    except Exception as e:
        print(f"Failed to query ElasticSearch: {e}")


if __name__ == "__main__":
    asyncio.run(check_index())
