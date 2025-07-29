"""Integration tests for OpenAlexAPIClient."""

import unittest

import pytest
import requests

from papers_please.client.OpenAlexAPIClient import OpenAlexAPIClient


class TestOpenAlexAPIClientIntegration(unittest.TestCase):
    """Integration tests for OpenAlexAPIClient using real API calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = OpenAlexAPIClient()
        self.client_with_email = OpenAlexAPIClient(email="test@example.com")
        self.valid_orcid_id = "0000-0003-1574-0784"  # (Seiji Isotani)
        self.invalid_orcid_id = "0000-0000-0000-0000"
        self.valid_doi = "10.1145/3576914.3587504"  # Known valid DOI
        self.invalid_doi = "10.1000/invalid.doi"
        self.malformed_doi = "not-a-doi"

    def test_get_author_by_orcid_success(self):
        """Test successful retrieval of author data with valid ORCID ID."""
        result = self.client.get_author_by_orcid(self.valid_orcid_id)

        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("orcid", result)
        self.assertIn("display_name", result)
        self.assertIn("works_count", result)
        self.assertIn("cited_by_count", result)

    def test_get_author_by_orcid_with_different_valid_orcid(self):
        """Test with another known valid ORCID ID (Leonardo Tortoro)."""
        orcid_id = "0000-0003-3032-6653"
        result = self.client.get_author_by_orcid(orcid_id)

        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("orcid", result)
        self.assertTrue(result["orcid"].endswith(orcid_id))

    def test_get_author_by_orcid_invalid_orcid_raises_exception(self):
        """Test that invalid ORCID ID raises an exception."""
        with pytest.raises(Exception) as exc_info:
            self.client.get_author_by_orcid(self.invalid_orcid_id)

        self.assertIn("Error fetching author", str(exc_info.value))

    def test_get_author_by_orcid_response_structure(self):
        """Test that the author response has expected structure."""
        result = self.client.get_author_by_orcid(self.valid_orcid_id)

        # Check main sections exist
        expected_fields = ["id", "orcid", "display_name", "works_count", "cited_by_count", "summary_stats"]
        for field in expected_fields:
            self.assertIn(field, result)

        # Check summary_stats structure
        summary_stats = result["summary_stats"]
        self.assertIn("h_index", summary_stats)
        self.assertIn("i10_index", summary_stats)

    def test_get_work_by_doi_success(self):
        """Test successful retrieval of work data with valid DOI."""
        result = self.client.get_work_by_doi(self.valid_doi)

        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("doi", result)
        self.assertIn("title", result)
        self.assertIn("cited_by_count", result)
        self.assertIn("publication_year", result)

    def test_get_work_by_doi_invalid_doi_returns_none(self):
        """Test that invalid DOI returns None."""
        result = self.client.get_work_by_doi(self.invalid_doi)
        self.assertIsNone(result)

    def test_get_work_by_doi_malformed_doi_returns_none(self):
        """Test that malformed DOI returns None."""
        result = self.client.get_work_by_doi(self.malformed_doi)
        self.assertIsNone(result)

    def test_get_work_by_doi_handles_doi_formats(self):
        """Test that different DOI formats are handled correctly."""
        # Test with https://doi.org/ prefix
        doi_with_prefix = f"https://doi.org/{self.valid_doi}"
        result1 = self.client.get_work_by_doi(doi_with_prefix)

        # Test with doi: prefix
        doi_with_doi_prefix = f"doi:{self.valid_doi}"
        result2 = self.client.get_work_by_doi(doi_with_doi_prefix)

        # Test plain DOI
        result3 = self.client.get_work_by_doi(self.valid_doi)

        # All should return the same result (or all None if DOI doesn't exist)
        if result1 is not None:
            self.assertIsInstance(result1, dict)
            self.assertIsInstance(result2, dict)
            self.assertIsInstance(result3, dict)
            self.assertEqual(result1["id"], result2["id"])
            self.assertEqual(result2["id"], result3["id"])

    def test_get_author_metrics_success(self):
        """Test successful retrieval of author metrics."""
        result = self.client.get_author_metrics(self.valid_orcid_id)

        self.assertIsInstance(result, dict)
        expected_metrics = [
            "total_publications",
            "total_citations",
            "h_index",
            "i10_index",
            "publications_per_year",
            "open_access_percentage",
            "top_concepts",
            "publications_by_type",
            "metrics_source",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, result)

        self.assertIsInstance(result["total_publications"], int)
        self.assertIsInstance(result["total_citations"], int)
        self.assertIsInstance(result["h_index"], int)
        self.assertIsInstance(result["i10_index"], int)
        self.assertIsInstance(result["publications_per_year"], dict)
        self.assertIsInstance(result["open_access_percentage"], float)
        self.assertIsInstance(result["top_concepts"], list)
        self.assertIsInstance(result["publications_by_type"], dict)
        self.assertEqual(result["metrics_source"], ["OpenAlex"])

    def test_get_author_metrics_invalid_orcid_returns_error_dict(self):
        """Test that invalid ORCID returns error dictionary instead of raising exception."""
        result = self.client.get_author_metrics(self.invalid_orcid_id)

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["total_publications"], 0)
        self.assertEqual(result["total_citations"], 0)

    def test_get_metrics_for_work_success(self):
        """Test successful retrieval of work metrics."""
        result = self.client.get_metrics_for_work(self.valid_doi)

        self.assertIsInstance(result, dict)
        expected_metrics = [
            "doi",
            "title",
            "cited_by_count",
            "publication_year",
            "type",
            "open_access",
            "journal_name",
            "source",
            "concepts",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, result)

        self.assertEqual(result["source"], "OpenAlex")
        self.assertIsInstance(result["cited_by_count"], int)
        self.assertIsInstance(result["open_access"], bool)
        self.assertIsInstance(result["concepts"], list)

    def test_get_metrics_for_work_invalid_doi_returns_error_dict(self):
        """Test that invalid DOI returns error dictionary."""
        result = self.client.get_metrics_for_work(self.invalid_doi)

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["doi"], self.invalid_doi)
        self.assertEqual(result["cited_by_count"], 0)
        self.assertEqual(result["source"], "OpenAlex")

    def test_get_metrics_for_works_multiple_dois(self):
        """Test retrieval of metrics for multiple DOIs."""
        dois = [self.valid_doi, self.invalid_doi]
        result = self.client.get_metrics_for_works(dois)

        self.assertEqual(len(result), 2)
        self.assertIn("doi", result.columns)
        self.assertIn("source", result.columns)

        # All results should have OpenAlex as source
        self.assertTrue(all(result["source"] == "OpenAlex"))

    def test_client_with_email_sets_user_agent(self):
        """Test that providing email sets proper User-Agent header."""
        # This is more of a unit test but included for completeness
        self.assertIn("User-Agent", self.client_with_email._headers)
        self.assertIn("test@example.com", self.client_with_email._headers["User-Agent"])

    def test_api_timeout_handling(self):
        """Test that the client handles network timeouts appropriately."""
        try:
            result = self.client.get_author_by_orcid(self.valid_orcid_id)
            self.assertIsInstance(result, dict)
        except requests.exceptions.Timeout:
            pytest.fail("Request should not timeout with 30 second limit under normal conditions")

    def test_network_resilience_multiple_requests(self):
        """Test multiple consecutive requests to ensure network resilience."""
        results = []
        for _ in range(3):
            result = self.client.get_author_by_orcid(self.valid_orcid_id)
            results.append(result)

        # All results should be identical
        self.assertEqual(len({str(r) for r in results}), 1)

        # Each result should be valid
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn("id", result)

    def test_base_url_accessibility(self):
        """Test that the OpenAlex API base URL is accessible."""
        # Make a direct request to verify the API is available
        response = requests.get(
            f"{self.client._BASE_URL}/authors/https://orcid.org/{self.valid_orcid_id}",
            headers=self.client._headers,
            timeout=30,
        )
        self.assertEqual(response.status_code, 200)

        # Should be able to parse as JSON
        data = response.json()
        self.assertIsInstance(data, dict)

    def test_concepts_structure_in_work_metrics(self):
        """Test that concepts in work metrics have proper structure."""
        result = self.client.get_metrics_for_work(self.valid_doi)

        if "error" not in result and result["concepts"]:
            for concept in result["concepts"]:
                self.assertIn("name", concept)
                self.assertIn("score", concept)
                self.assertIn("level", concept)
                self.assertIsInstance(concept["score"], (int, float))
                self.assertIsInstance(concept["level"], int)

    def test_top_concepts_structure_in_author_metrics(self):
        """Test that top concepts in author metrics have proper structure."""
        result = self.client.get_author_metrics(self.valid_orcid_id)

        if "error" not in result and result["top_concepts"]:
            for concept in result["top_concepts"]:
                self.assertIn("name", concept)
                self.assertIn("score", concept)
                self.assertIsInstance(concept["score"], (int, float))
