# Norway Water Temperature API Client
A Python package to fetch water temperature data from various locations in Norway.

## Installation
```
pip install yrwatertemperatures
```

## API key
To use this package, you need an API key from yr.no, see https://hjelp.yr.no/hc/no/articles/5949243432850-API-for-badetemperaturer for more info. 

## Usage
First, you'll need to get an API key from the provider of the water temperature data.

Then, you can use the package like this:

```python
"""Example script to fetch and display water temperatures using the yrwatertemperatures package."""
import asyncio
from aiohttp import ClientSession, ClientError
from yrwatertemperatures import WaterTemperatures

API_KEY = "your_api_key_here"  # Replace with your actual API key

async def main() -> None:
    """Main function to fetch and display water temperatures."""
    async with ClientSession() as session:
        try:
            client = WaterTemperatures(API_KEY, session)
            temperatures = await client.async_get_all_water_temperatures()

            # Print the location and temperature
            for temp in temperatures:
                print(f"Location: {temp.name}, Temperature: {temp.temperature}°C")

        except (ClientError, Exception) as e:
            print(f"An error occurred: {e}")

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
```

## Data Structure
The `get_temperatures` method returns a list of `LocationData` objects. Each object has the following attributes:

`name` (str): The name of the location.

`location_id` (str): A unique identifier for the location.

`latitude` (float): The latitude of the location.

`longitude` (float): The longitude of the location.

`elevation` (int): The elevation of the location in meters.

`county` (str): The county where the location is.

`municipality` (str): The municipality where the location is.

`temperature` (float): The water temperature in Celsius.

`time` (datetime): The timestamp of the reading.

`source` (str): The source of the data (not always present).