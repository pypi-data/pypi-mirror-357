import unittest
from unittest.mock import patch, Mock
from datetime import datetime

from yrwatertemperatures import WaterTemperatures, WaterTemperatureData

class TestWaterTemperatures(unittest.TestCase):

    def setUp(self):
        """Set up the test case with a mock API key and the WaterTemperatures instance."""
        self.api_key = "test_api_key"
        self.client = WaterTemperatures(self.api_key)

    def test_init_requires_api_key(self):
        """Test that the constructor raises ValueError if no API key is provided."""
        with self.assertRaises(ValueError):
            WaterTemperatures(api_key="")

    @patch('yrwatertemperatures.requests.get')
    def test_get_all_water_temperatures_success(self, mock_get):
        """Test fetching water temperatures successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
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
            },

        ]
        mock_get.return_value = mock_response

        temperatures = self.client.get_all_water_temperatures()
        self.assertEqual(len(temperatures), 2)
        self.assertIsInstance(temperatures[0], WaterTemperatureData)
        self.assertEqual(temperatures[0].name, "Storøyodden")
        self.assertEqual(temperatures[1].source, "")

    @patch('yrwatertemperatures.requests.get')
    def test_get_all_water_temperatures_unauthorized(self, mock_get):
        """Test handling unauthorized access."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(PermissionError):
            self.client.get_all_water_temperatures()

    @patch('yrwatertemperatures.requests.get')
    def test_get_all_water_temperatures_invalid_response(self, mock_get):
        """Test handling invalid response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = "Invalid data format"
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            self.client.get_all_water_temperatures()


    def test_malformed_data(self):
        """Test that the parser can handle missing keys or incorrect types."""
        # This data is missing the 'temperature' key in the first item
        malformed_data = [
            {
                "locationName": "Incomplete Beach",
                "locationId": "0-99999",
                "position": {"lat": 60.0, "lon": 10.0},
                "elevation": 5,
                "county": "Test County",
                "municipality": "Test Municipality",
                # "temperature": 10.0,  <-- Missing
                "time": "2025-05-30T05:00:00+02:00",
                "sourceDisplayName": "Test Source"
            }
        ]
        with self.assertLogs('yrwatertemperatures', level='ERROR'):
            # The parser should skip the bad item and return an empty list
            parsed_data = self.client._parse_water_temperatures(malformed_data)
            self.assertEqual(len(parsed_data), 0)

