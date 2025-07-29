"""Parser for ORCID JSON data."""

from datetime import date
from datetime import datetime as dt
from typing import Any

import pandas as pd


class OrcidAPIDataParser:
    """Parser for ORCID JSON data."""

    def __init__(self, json_data: dict[str, Any]) -> None:
        """Initialize the parser with ORCID JSON data.

        Args:
            json_data: The JSON data from ORCID API
        """
        self.json_data = json_data

    def get_first_name(self) -> str:
        """Extract first name from ORCID data."""
        value = self.json_data.get("person", {}).get("name", {}).get("given-names", {}).get("value")
        return str(value) if value is not None else ""

    def get_last_name(self) -> str:
        """Extract last name from ORCID data."""
        value = self.json_data.get("person", {}).get("name", {}).get("family-name", {}).get("value")
        return str(value) if value is not None else ""

    def get_biography(self) -> str:
        """Extract biography from ORCID data."""
        value = self.json_data.get("person", {}).get("biography", {}).get("content")
        return str(value) if value is not None else ""

    def get_emails(self) -> list[str]:
        """Extract emails from ORCID data."""
        emails = self.json_data.get("person", {}).get("emails", {}).get("email", [])
        return [str(email) for email in emails] if emails else []

    def get_keywords(self) -> list[str]:
        """Extract keywords from ORCID data."""
        keywords = []
        for keyword in self.json_data.get("person", {}).get("keywords", {}).get("keyword", []):
            keywords.append(keyword.get("content", ""))
        return keywords

    def get_external_links(self) -> dict[str, str]:
        """Extract external links from ORCID data."""
        external_links = {}
        for identifier in (
            self.json_data.get("person", {}).get("external-identifiers", {}).get("external-identifier", [])
        ):
            source_name = identifier.get("source", {}).get("source-name", {}).get("value", "")
            link = identifier.get("external-id-url", {}).get("value", "")
            external_links[source_name] = link
        return external_links

    def get_education(self) -> dict[str, dict[str, Any]]:
        """Extract education information from ORCID data."""
        educations = {}
        educations_list = (
            self.json_data.get("activities-summary", {}).get("educations", {}).get("affiliation-group", [])
        )

        for education in educations_list:
            summaries = education.get("summaries", [])

            for summary in summaries:
                role_title = summary.get("education-summary", {}).get("role-title", "")

                department_name = summary.get("education-summary", {}).get("department-name", "")
                if department_name is None:
                    department_name = ""

                organization = summary.get("education-summary", {}).get("organization", {}).get("name", "")
                if organization is None:
                    organization = ""

                start_date = self.extract_date_from_json(summary.get("education-summary", {}).get("start-date"))
                end_date = self.extract_date_from_json(summary.get("education-summary", {}).get("end-date"))

                educations[role_title] = {
                    "institution": f"{organization} - {department_name}",
                    "start_date": start_date,
                    "end_date": end_date,
                }

        return educations

    def get_employments(self) -> dict[str, dict[str, Any]]:
        """Extract employment information from ORCID data."""
        employments = {}
        employments_list = (
            self.json_data.get("activities-summary", {}).get("employments", {}).get("affiliation-group", [])
        )

        for employment in employments_list:
            summaries = employment.get("summaries", [])

            for summary in summaries:
                role_title = summary.get("employment-summary", {}).get("role-title", "")

                department_name = summary.get("employment-summary", {}).get("department-name", "")
                if department_name is None:
                    department_name = ""

                organization = summary.get("employment-summary", {}).get("organization", {}).get("name", "")
                if organization is None:
                    organization = ""

                start_date = self.extract_date_from_json(summary.get("employment-summary", {}).get("start-date"))
                end_date = self.extract_date_from_json(summary.get("employment-summary", {}).get("end-date"))

                employments[role_title] = {
                    "institution": f"{organization} - {department_name}",
                    "start_date": start_date,
                    "end_date": end_date,
                }

        return employments

    def get_papers(self) -> pd.DataFrame:
        """Extract papers information from ORCID data."""
        df = pd.DataFrame(columns=["doi", "title", "url", "type", "publication_date", "journal"])

        papers = self.json_data.get("activities-summary", {}).get("works", {}).get("group", [])

        for paper in papers:
            data = {}
            summaries = paper.get("work-summary", [])

            for summary in summaries:
                data["title"] = summary.get("title", {}).get("title", {}).get("value", "")
                external_ids = summary.get("external-ids", {}).get("external-id", [])
                for external_id in external_ids:
                    data["doi"] = external_id.get("external-id-value", "")

                url = summary.get("url", {})
                if url is None:
                    data["url"] = None
                else:
                    data["url"] = url.get("value", "")

                data["type"] = summary.get("type", "")
                data["publication_date"] = self.extract_date_from_json(summary.get("publication-date"))

                jornal = summary.get("journal-title", {})
                if jornal is None:
                    data["journal"] = None
                else:
                    data["journal"] = jornal.get("value", "")

            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

        return df

    @staticmethod
    def extract_date_from_json(date_dict: dict[str, Any] | None) -> date | None:
        """Extract date from ORCID JSON date structure."""
        if date_dict is None:
            return None

        year_data = date_dict.get("year", {})
        if not year_data or "value" not in year_data:
            return None

        try:
            year = int(year_data["value"])
        except (ValueError, TypeError):
            return None

        month_data = date_dict.get("month", {})
        month = 1
        if month_data and "value" in month_data:
            try:
                month = int(month_data["value"])
            except (ValueError, TypeError):
                month = 1

        day_data = date_dict.get("day", {})
        day = 1
        if day_data and "value" in day_data:
            try:
                day = int(day_data["value"])
            except (ValueError, TypeError):
                day = 1

        try:
            return dt(year=year, month=month, day=day).date()
        except ValueError:
            return None
