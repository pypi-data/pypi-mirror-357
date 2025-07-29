"""Integration tests for OrcidAPIClient."""

import unittest

import pytest
import requests

from papers_please.client.OrcidAPIClient import OrcidAPIClient


class TestOrcidAPIClientIntegration(unittest.TestCase):
    """Integration tests for OrcidAPIClient using real API calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = OrcidAPIClient()
        self.valid_orcid_id = "0000-0003-1574-0784"  # (Seiji Isotani)
        self.invalid_orcid_id = "0000-0000-0000-0000"
        self.malformed_orcid_id = "invalid-orcid"

    def test_get_researcher_data_success(self):
        """Test successful retrieval of researcher data with valid ORCID ID."""
        result = self.client.get_researcher_data(self.valid_orcid_id)

        self.assertIsInstance(result, dict)
        self.assertIn("orcid-identifier", result)
        self.assertEqual(result["orcid-identifier"]["path"], self.valid_orcid_id)
        self.assertIn("person", result)

    def test_get_researcher_data_with_different_valid_orcid(self):
        """Test with another
        known valid ORCID ID
        (Leonardo Tortoro)."""
        orcid_id = "0000-0003-3032-6653"
        result = self.client.get_researcher_data(orcid_id)

        self.assertIsInstance(result, dict)
        self.assertIn("orcid-identifier", result)
        self.assertEqual(result["orcid-identifier"]["path"], orcid_id)

    def test_get_researcher_data_invalid_orcid_raises_exception(self):
        """Test that invalid ORCID ID raises an exception."""
        with pytest.raises(Exception) as exc_info:
            self.client.get_researcher_data(self.invalid_orcid_id)

        self.assertIn("Request Error", str(exc_info.value))
        self.assertIn("404", str(exc_info.value))

    def test_get_researcher_data_malformed_orcid_raises_exception(self):
        """Test that malformed ORCID ID raises an exception."""
        with pytest.raises(Exception) as exc_info:
            self.client.get_researcher_data(self.malformed_orcid_id)

        self.assertIn("Request Error", str(exc_info.value))

    def test_get_researcher_data_response_structure(self):
        """Test that the response has expected structure."""
        result = self.client.get_researcher_data(self.valid_orcid_id)

        # Check main sections exist
        expected_sections = ["orcid-identifier", "person", "activities-summary"]
        for section in expected_sections:
            self.assertIn(section, result)

        # Check orcid-identifier structure
        orcid_id_section = result["orcid-identifier"]
        self.assertIn("uri", orcid_id_section)
        self.assertIn("path", orcid_id_section)
        self.assertIn("host", orcid_id_section)

    def test_get_researcher_data_timeout_handling(self):
        """Test that the client handles network timeouts appropriately."""
        # This test might take up to 30 seconds if the network is slow
        # but should not hang indefinitely
        try:
            result = self.client.get_researcher_data(self.valid_orcid_id)
            self.assertIsInstance(result, dict)
        except requests.exceptions.Timeout:
            pytest.fail("Request should not timeout with 30 second limit under normal conditions")

    def test_get_researcher_data_network_resilience(self):
        """Test multiple consecutive requests to ensure network resilience."""
        # Test that multiple requests work consistently
        results = []
        for _ in range(3):
            result = self.client.get_researcher_data(self.valid_orcid_id)
            results.append(result)

        # All results should be identical
        self.assertEqual(len({str(r) for r in results}), 1)

        # Each result should be valid
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn("orcid-identifier", result)

    def test_api_headers_acceptance(self):
        """Test that the API accepts our headers and returns JSON."""
        result = self.client.get_researcher_data(self.valid_orcid_id)

        # If we get a dict back, JSON parsing worked
        self.assertIsInstance(result, dict)

        # Should contain standard ORCID response fields
        self.assertIn("orcid-identifier", result)
        self.assertIn("person", result)

    def test_base_url_accessibility(self):
        """Test that the ORCID API base URL is accessible."""
        # Make a direct request to verify the API is available
        response = requests.get(
            f"{self.client._BASE_URL}/{self.valid_orcid_id}", headers=self.client._HEADERS, timeout=30
        )
        self.assertEqual(response.status_code, 200)

        # Should be able to parse as JSON
        data = response.json()
        self.assertIsInstance(data, dict)
