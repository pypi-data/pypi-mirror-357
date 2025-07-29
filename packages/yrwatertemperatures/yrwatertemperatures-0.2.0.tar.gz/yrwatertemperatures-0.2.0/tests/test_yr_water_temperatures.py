import unittest
import aiohttp
from aioresponses import aioresponses
import pytest
from yrwatertemperatures import WaterTemperatures, WaterTemperatureData

class TestWaterTemperatures(unittest.IsolatedAsyncioTestCase):

    @pytest.mark.asyncio
    async def test_init_requires_api_key(self):
        """Test that the constructor raises ValueError if no API key is provided."""
        session = aiohttp.ClientSession()

        with aioresponses() as session_mock:
            session_mock.get(
                'https://badetemperaturer.yr.no/api/watertemperatures',
                status=200,
                payload=[]
            )
            with pytest.raises(ValueError, match="API key must be provided."):
                WaterTemperatures("", session)
        await session.close()

    @pytest.mark.asyncio
    async def test_get_all_water_temperatures_success(self):
        """Test fetching water temperatures successfully."""
        session = aiohttp.ClientSession()

        with aioresponses() as session_mock:
            session_mock.get(
                'https://badetemperaturer.yr.no/api/watertemperatures',
                payload=[
                    {
                        "locationName": "Storøyodden",
                        "locationId": "0-10014",
                        "position": {
                            "lat": 59.88819,
                            "lon": 10.59302
                        },
                        "elevation": 1,
                        "county": "Akershus",
                        "municipality": "Bærum kommune",
                        "temperature": 13.6,
                        "time": "2025-05-30T04:00:46+02:00",
                        "sourceDisplayName": "Badevann.no"
                    },
                    {
                        "locationName": "Årvolldammen",
                        "locationId": "0-10027",
                        "position": {
                            "lat": 59.94768,
                            "lon": 10.82012
                        },
                        "elevation": 181,
                        "county": "Oslo fylke",
                        "municipality": "Oslo kommune",
                        "temperature": 10,
                        "time": "2025-05-26T08:40:00+02:00"
                    }
                ]
            )

            client = WaterTemperatures("test_api_key", session)
            temperatures = await client.async_get_all_water_temperatures()
        await session.close()

        assert len(temperatures) == 2
        assert isinstance(temperatures[0], WaterTemperatureData)
        assert temperatures[0].name == "Storøyodden"
        assert temperatures[0].temperature == 13.6
        assert temperatures[1].source == ""


    @pytest.mark.asyncio
    async def test_get_all_water_temperatures_unauthorized(self):
        """Test handling unauthorized access."""

        session = aiohttp.ClientSession()
        with aioresponses() as session_mock:
            session_mock.get(
                'https://badetemperaturer.yr.no/api/watertemperatures',
                status=401,
            )

            with pytest.raises(PermissionError):
                client = WaterTemperatures("test_api_key", session)
                await client.async_get_all_water_temperatures()
        await session.close()


    @pytest.mark.asyncio
    async def test_get_all_water_temperatures_invalid_response(self):
        """Test handling invalid response format."""
        session = aiohttp.ClientSession()

        with aioresponses() as session_mock:
            session_mock.get(
                'https://badetemperaturer.yr.no/api/watertemperatures',
                payload="This is not a valid response"
            )
            with pytest.raises(ValueError):
                client = WaterTemperatures("test_api_key", session)
                await client.async_get_all_water_temperatures()

        await session.close()


    @pytest.mark.asyncio
    async def test_malformed_data(self):
        """Test that the parser can handle missing keys or incorrect types."""
        session = aiohttp.ClientSession()

        with aioresponses() as session_mock:
            session_mock.get(
                'https://badetemperaturer.yr.no/api/watertemperatures',
                payload=[
                    {
                        "locationName": "Test Location",
                        "locationId": "0-12345",
                        "position": {
                            "lat": 59.88819,
                            "lon": 10.59302
                        },
                        # Missing elevation, county, municipality, temperature, time
                    }
                ]
            )

            client = WaterTemperatures("test_api_key", session)
            temperatures = await client.async_get_all_water_temperatures()

        await session.close()

        assert len(temperatures) == 0
