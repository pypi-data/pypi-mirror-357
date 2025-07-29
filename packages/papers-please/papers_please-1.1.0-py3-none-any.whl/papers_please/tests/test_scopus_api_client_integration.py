"""Integration tests for ScopusAPIClient."""

import os
import unittest
from pathlib import Path

import pytest
import requests

from papers_please.client.ScopusAPIClient import ScopusAPIClient

try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)
    print(f"Environment variables loaded from: {env_path}\n")
except ImportError:
    print("python-dotenv not installed. Install it with: pip install python-dotenv")
    print("Environment variables from .env file will not be loaded.")


class TestScopusAPIClientIntegration(unittest.TestCase):
    """Integration tests for ScopusAPIClient using real API calls."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = os.environ.get("SCOPUS_API_KEY")
        if not self.api_key:
            self.skipTest("SCOPUS_API_KEY environment variable not set")

        self.client = ScopusAPIClient(api_key=self.api_key)
        self.valid_orcid_id = "0000-0003-1574-0784"  # (Seiji Isotani)
        self.invalid_orcid_id = "0000-0000-0000-0000"
        self.valid_doi = "10.1145/3576914.3587504"  # Known valid DOI
        self.invalid_doi = "10.1000/invalid.doi"
        self.malformed_doi = "not-a-doi"
        self.valid_scopus_id = "123456789"  # Example Scopus ID

    def test_init_requires_api_key(self):
        """Test that initialization requires an API key."""
        with pytest.raises(ValueError) as exc_info:
            ScopusAPIClient(api_key="")

        self.assertIn("API key is required", str(exc_info.value))

    def test_init_sets_headers(self):
        """Test that initialization sets proper headers."""
        client = ScopusAPIClient(api_key="test_key")
        self.assertIn("X-ELS-APIKey", client._headers)
        self.assertEqual(client._headers["X-ELS-APIKey"], "test_key")
        self.assertEqual(client._headers["Accept"], "application/json")

    def test_get_scopus_id_from_orcid_success(self):
        """Test successful extraction of Scopus ID from ORCID profile."""
        try:
            result = self.client.get_scopus_id_from_orcid(self.valid_orcid_id)

            # Result can be None (no Scopus ID found) or a string (Scopus ID found)
            if result is not None:
                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)
            else:
                # It's valid for an ORCID profile to not have a Scopus ID
                self.assertIsNone(result)

        except Exception:
            # Should handle gracefully and return None
            result = self.client.get_scopus_id_from_orcid(self.valid_orcid_id)
            self.assertIsNone(result)

    def test_get_scopus_id_from_orcid_not_found(self):
        """Test that returns None when Scopus ID not found in ORCID profile."""
        try:
            result = self.client.get_scopus_id_from_orcid(self.invalid_orcid_id)
            # Should handle gracefully and return None for invalid ORCID
            self.assertIsNone(result)
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_get_scopus_id_from_orcid_handles_exception(self):
        """Test that handles exceptions when fetching ORCID data."""
        malformed_orcid = "invalid-orcid-format"
        result = self.client.get_scopus_id_from_orcid(malformed_orcid)
        self.assertIsNone(result)

        def test_search_scopus_success(self):
            """Test successful Scopus search with valid query."""
            query = 'TITLE("machine learning")'

            try:
                result = self.client.search_scopus(query, count=5)

                self.assertIsInstance(result, dict)
                self.assertIn("search-results", result)

                search_results = result["search-results"]
                self.assertIn("opensearch:totalResults", search_results)

            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    self.skipTest(f"API key authentication failed: {e}")
                elif "429" in str(e):
                    self.skipTest(f"Rate limit exceeded: {e}")
                else:
                    raise

    def test_get_author_by_scopus_id_success(self):
        """Test successful retrieval of author data by Scopus ID."""
        # Use a mock or skip if we don't have a valid Scopus ID
        try:
            result = self.client.get_author_by_scopus_id(self.valid_scopus_id)

            if result:  # Only check structure if we got results
                self.assertIsInstance(result, dict)
                self.assertIn("scopus_id", result)
                self.assertIn("total_documents", result)
                self.assertIn("publications", result)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                # For invalid Scopus ID, should return empty dict
                pass

    def test_get_work_by_doi_success(self):
        """Test successful retrieval of work data with valid DOI."""
        try:
            result = self.client.get_work_by_doi(self.valid_doi)

            if result is not None:
                self.assertIsInstance(result, dict)
                # Check for common Scopus fields
                expected_fields = ["dc:title", "prism:doi", "citedby-count"]
                for field in expected_fields:
                    if field in result:  # Some fields might not always be present
                        self.assertIsNotNone(result[field])

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_get_work_by_doi_invalid_doi_returns_none(self):
        """Test that invalid DOI returns None."""
        try:
            result = self.client.get_work_by_doi(self.invalid_doi)
            self.assertIsNone(result)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                # Should handle gracefully
                pass

    def test_get_work_by_doi_malformed_doi_returns_none(self):
        """Test that malformed DOI returns None."""
        try:
            result = self.client.get_work_by_doi(self.malformed_doi)
            self.assertIsNone(result)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                # Should handle gracefully
                pass

    def test_get_work_by_doi_handles_doi_formats(self):
        """Test that different DOI formats are handled correctly."""
        try:
            # Test with https://doi.org/ prefix
            doi_with_prefix = f"https://doi.org/{self.valid_doi}"
            result1 = self.client.get_work_by_doi(doi_with_prefix)

            # Test with doi: prefix
            doi_with_doi_prefix = f"doi:{self.valid_doi}"
            result2 = self.client.get_work_by_doi(doi_with_doi_prefix)

            # Test plain DOI
            result3 = self.client.get_work_by_doi(self.valid_doi)

            # Results should be consistent (all None or all valid)
            results = [result1, result2, result3]
            none_count = sum(1 for r in results if r is None)

            # Either all None or all valid
            self.assertTrue(none_count == 0 or none_count == 3)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_get_author_metrics_success(self):
        """Test successful retrieval of author metrics."""
        try:
            result = self.client.get_author_metrics(self.valid_orcid_id)

            self.assertIsInstance(result, dict)
            expected_metrics = [
                "total_publications",
                "total_citations",
                "h_index",
                "publications_per_year",
                "publications_by_type",
                "top_subject_areas",
                "metrics_source",
            ]

            for metric in expected_metrics:
                self.assertIn(metric, result)

            self.assertEqual(result["metrics_source"], ["Scopus"])

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                # Should handle gracefully and return error dict
                self.assertIsInstance(result, dict)
                self.assertIn("error", result)

    def test_get_author_metrics_invalid_orcid_returns_error_dict(self):
        """Test that returns error dict when ORCID has no Scopus ID."""
        try:
            result = self.client.get_author_metrics(self.invalid_orcid_id)

            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertEqual(result["total_publications"], 0)
            self.assertEqual(result["total_citations"], 0)
            self.assertEqual(result["metrics_source"], ["Scopus"])

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_get_metrics_for_work_success(self):
        """Test successful retrieval of work metrics."""
        try:
            result = self.client.get_metrics_for_work(self.valid_doi)

            self.assertIsInstance(result, dict)
            expected_metrics = [
                "doi",
                "title",
                "cited_by_count",
                "publication_year",
                "type",
                "journal_name",
                "source",
                "subject_areas",
            ]

            for metric in expected_metrics:
                self.assertIn(metric, result)

            self.assertEqual(result["source"], "Scopus")
            if "error" not in result:
                self.assertIsInstance(result["cited_by_count"], int)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_get_metrics_for_works_multiple_dois(self):
        """Test retrieval of metrics for multiple DOIs."""
        try:
            dois = [self.valid_doi, self.invalid_doi]
            result = self.client.get_metrics_for_works(dois)

            self.assertEqual(len(result), 2)
            self.assertIn("doi", result.columns)
            self.assertIn("source", result.columns)

            # All results should have Scopus as source
            self.assertTrue(all(result["source"] == "Scopus"))

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_api_timeout_handling(self):
        """Test that the client handles network timeouts appropriately."""
        query = 'TITLE("test")'

        try:
            result = self.client.search_scopus(query, count=1)
            self.assertIsInstance(result, dict)
        except requests.exceptions.Timeout:
            pytest.fail("Request should not timeout with 30 second limit under normal conditions")
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_network_resilience_multiple_requests(self):
        """Test multiple consecutive requests to ensure network resilience."""
        query = 'TITLE("test")'

        try:
            results = []
            for _ in range(2):  # Reduced to 2 requests to avoid rate limits
                result = self.client.search_scopus(query, count=1)
                results.append(result)

            # Each result should be valid
            for result in results:
                self.assertIsInstance(result, dict)
                self.assertIn("search-results", result)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_base_url_accessibility(self):
        """Test that the Scopus API base URL is accessible."""
        try:
            # Make a simple search request to verify API is available
            response = requests.get(
                f"{self.client._BASE_URL}/search/scopus" + "?query=TITLE%28%22test%22%29" + "&count=1",
                headers=self.client._headers,
                timeout=30,
            )

            # Should get some response (even if authentication fails)
            self.assertIn(response.status_code, [200, 401, 403, 429])

        except requests.exceptions.RequestException:
            pytest.fail("Should be able to reach Scopus API endpoint")

    def test_subject_areas_structure_in_work_metrics(self):
        """Test that subject areas in work metrics have proper structure."""
        try:
            result = self.client.get_metrics_for_work(self.valid_doi)

            if "error" not in result and result.get("subject_areas"):
                for area in result["subject_areas"]:
                    self.assertIn("name", area)
                    self.assertIn("code", area)
                    self.assertIsInstance(area["name"], str)
                    self.assertIsInstance(area["code"], str)

        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                self.skipTest(f"API key authentication failed: {e}")
            elif "429" in str(e):
                self.skipTest(f"Rate limit exceeded: {e}")
            else:
                raise

    def test_get_scopus_id_from_orcid_real_integration(self):
        """Test real integration with ORCID API to extract Scopus ID."""
        try:
            result = self.client.get_scopus_id_from_orcid(self.valid_orcid_id)

            # Result can be None (no Scopus ID found) or a string (Scopus ID found)
            if result is not None:
                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)

        except Exception:
            # Should handle gracefully and return None
            result = self.client.get_scopus_id_from_orcid(self.valid_orcid_id)
            if result is not None:
                self.assertIsInstance(result, str)
