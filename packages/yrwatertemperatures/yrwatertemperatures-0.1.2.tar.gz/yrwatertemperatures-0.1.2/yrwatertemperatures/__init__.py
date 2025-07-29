import requests
from datetime import datetime
from dataclasses import dataclass
import logging

_LOGGER = logging.getLogger(__name__)


@dataclass
class WaterTemperatureData:
    """Represents the water temperature data for a single location."""
    name: str
    location_id: str
    latitude: float
    longitude: float
    elevation: int
    county: str
    municipality: str
    temperature: float
    time: datetime
    source: str


class WaterTemperatures:
    """Class to fetch and parse water temperature data from Yr API."""

    def __init__(self, api_key: str):
        """
        Initialize the WaterTemperatures class with the API key.

        :param api_key: The API key for accessing the Yr API.
        """
        if not api_key:
            raise ValueError("API key must be provided.")
        self.base_url = "https://badetemperaturer.yr.no/api"
        self.headers = {
            "apikey": api_key
        }

    def get_all_water_temperatures(self) -> list[WaterTemperatureData]:
        """Fetch all water temperatures from the Yr API."""

        url = self.base_url + "/watertemperatures"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 401:
                raise PermissionError("Unauthorized: Invalid API key or insufficient permissions.")
            response.raise_for_status()
            data = response.json()
            return self._parse_water_temperatures(data)

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from Yr API: {e}")

    @staticmethod
    def _parse_water_temperatures(data: list) -> list[WaterTemperatureData]:
        """Parse the JSON data from the Yr API into a list of WaterTemperature objects."""

        if not isinstance(data, list):
            raise ValueError("API response is not a list.")

        temperatures = []
        for item in data:
            try:
                temp = WaterTemperatureData(
                    name=item["locationName"],
                    location_id=item["locationId"],
                    latitude=item["position"]["lat"],
                    longitude=item["position"]["lon"],
                    elevation=item["elevation"],
                    county=item["county"],
                    municipality=item["municipality"],
                    temperature=item["temperature"],
                    # Parse the ISO 8601 timestamp string into a datetime object
                    time=datetime.fromisoformat(item["time"]),
                    source=item.get("sourceDisplayName", "")
                )
                temperatures.append(temp)
            except (KeyError, TypeError) as e:
                _LOGGER.error(f"Error parsing item {item}: {e}")
                continue

        return temperatures