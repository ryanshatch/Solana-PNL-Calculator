import requests
import sys
import asyncio
import aiohttp
import time

async def fetch_floor_price(session, collection_name):
    """
    Asynchronously fetches the floor price for a given collection.
    """
    url = f'https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/stats'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get('floorPrice')
    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
        print(f"Error fetching floor price for {collection_name}: {e}")
        return None

async def fetch_top_traded(session, limit=10):
    """
    Asynchronously fetches the top traded collections.
    """
    url = f'https://api-mainnet.magiceden.dev/v2/collections/top?limit={limit}'
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return [(item['symbol'], item['volumeAllTime']) for item in data]
    except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
        print(f"Error fetching top traded collections: {e}")
        return []

async def main_async(collection_names, sleep_duration=600):
    """
    Main asynchronous loop for fetching and displaying data.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            print("\nFetching latest data...")

            # Fetching and displaying floor prices asynchronously
            floor_price_tasks = [fetch_floor_price(session, name) for name in collection_names]
            floor_prices = await asyncio.gather(*floor_price_tasks)
            for name, price in zip(collection_names, floor_prices):
                if price is not None:
                    print(f'Current floor price for {name}: {price}')
                else:
                    print(f'Failed to fetch data for {name}')

            # Fetching and displaying top traded collections asynchronously
            top_traded = await fetch_top_traded(session)
            if top_traded:
                print("\nTop 10 Traded Collections on Solana:")
                for symbol, volume in top_traded:
                    print(f'{symbol}: {volume}')
            else:
                print("Failed to fetch top traded collections")

            await asyncio.sleep(sleep_duration)  # Sleep for specified duration

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py collection_name1 [collection_name2 ...]")
        sys.exit(1)

    collection_names = sys.argv[1:]
    asyncio.run(main_async(collection_names))

if __name__ == "__main__":
    main()