"""Client for interacting with the ORCID API."""

from typing import Any

import requests


class OrcidAPIClient:
    """Client for interacting with the ORCID API."""

    _BASE_URL = "https://pub.orcid.org/v3.0"
    _HEADERS = {"Accept": "application/json"}

    def __init__(self) -> None:
        """Initialize the ORCID API client."""
        pass

    def get_researcher_data(self, orcid_id: str) -> dict[str, Any]:
        """Fetch researcher data from ORCID API.

        Args:
            orcid_id: The ORCID identifier for the researcher

        Returns:
            Dict containing the researcher's data from ORCID

        Raises:
            Exception: If the API request fails
        """
        url = f"{self._BASE_URL}/{orcid_id}"

        response = requests.get(url, headers=self._HEADERS, timeout=30)

        if response.status_code == 200:
            return response.json()  # type: ignore[no-any-return]
        else:
            raise Exception(f"Request Error. Status code: {response.status_code}")
