"""Researcher management module."""

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from papers_please.client.OrcidAPIClient import OrcidAPIClient
    from papers_please.data.OrcidAPIDataParser import OrcidAPIDataParser


class Researcher:
    """Represents a researcher with ORCID data."""

    def __init__(self, id: str, api_client: "OrcidAPIClient | None" = None) -> None:
        """Initialize a Researcher instance.

        Args:
            id: The ORCID identifier for the researcher
            api_client: Optional API client instance. If not provided, a new one will be created.
        """
        from papers_please.client.OrcidAPIClient import OrcidAPIClient

        self._id = id
        self._api_client = api_client or OrcidAPIClient()
        self._data_parser: OrcidAPIDataParser | None = None

        # Cached data
        self._first_name: str | None = None
        self._last_name: str | None = None
        self._name: str | None = None
        self._biography: str | None = None
        self._emails: list[str] | None = None
        self._keywords: list[str] | None = None
        self._external_links: dict[str, str] | None = None
        self._education: dict[str, dict[str, Any]] | None = None
        self._employments: dict[str, dict[str, Any]] | None = None
        self._papers: pd.DataFrame | None = None

    def _ensure_data_parser(self) -> None:
        """Ensure the data parser is initialized with ORCID data."""
        if self._data_parser is None:
            from papers_please.data.OrcidAPIDataParser import OrcidAPIDataParser

            json_data = self._api_client.get_researcher_data(self._id)
            self._data_parser = OrcidAPIDataParser(json_data)

    @property
    def papers(self) -> pd.DataFrame:
        """Get papers information as a DataFrame."""
        if self._papers is None:
            self._ensure_data_parser()
            self._papers = self._data_parser.get_papers()
        return self._papers

    @property
    def employments(self) -> dict[str, dict[str, Any]]:
        """Get employment information."""
        if self._employments is None:
            self._ensure_data_parser()
            self._employments = self._data_parser.get_employments()
        return self._employments

    @property
    def education(self) -> dict[str, dict[str, Any]]:
        """Get education information."""
        if self._education is None:
            self._ensure_data_parser()
            self._education = self._data_parser.get_education()
        return self._education

    @property
    def external_links(self) -> dict[str, str]:
        """Get external links."""
        if self._external_links is None:
            self._ensure_data_parser()
            self._external_links = self._data_parser.get_external_links()
        return self._external_links

    @property
    def keywords(self) -> list[str]:
        """Get keywords."""
        if self._keywords is None:
            self._ensure_data_parser()
            self._keywords = self._data_parser.get_keywords()
        return self._keywords

    @property
    def emails(self) -> list[str]:
        """Get emails."""
        if self._emails is None:
            self._ensure_data_parser()
            self._emails = self._data_parser.get_emails()
        return self._emails

    @property
    def biography(self) -> str:
        """Get biography."""
        if self._biography is None:
            self._ensure_data_parser()
            self._biography = self._data_parser.get_biography()
        return self._biography

    @property
    def first_name(self) -> str:
        """Get first name."""
        if self._first_name is None:
            self._ensure_data_parser()
            self._first_name = self._data_parser.get_first_name()
        return self._first_name

    @property
    def last_name(self) -> str:
        """Get last name."""
        if self._last_name is None:
            self._ensure_data_parser()
            self._last_name = self._data_parser.get_last_name()
        return self._last_name

    @property
    def name(self) -> str:
        """Get full name."""
        if self._name is None:
            self._name = f"{self.first_name} {self.last_name}"
        return self._name

    @property
    def id(self) -> str:
        """Get the ORCID identifier."""
        return self._id
