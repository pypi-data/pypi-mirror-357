"""Client for querying the Scopus API and obtaining publication metrics."""

import time

import pandas as pd
import requests


class ScopusAPIClient:
    """Client for querying the Scopus API and obtaining publication metrics."""

    _BASE_URL = "https://api.elsevier.com/content"

    def __init__(self, api_key: str) -> None:
        """Initialize the Scopus client.

        Args:
            api_key: Scopus API key (required)
        """
        if not api_key:
            raise ValueError("API key is required to use the Scopus API")

        self.api_key = api_key
        self._headers = {"X-ELS-APIKey": api_key, "Accept": "application/json"}

    def get_scopus_id_from_orcid(self, orcid_id: str) -> str | None:
        """Extract Scopus Author ID from ORCID external identifiers.

        Args:
            orcid_id: ORCID ID of the researcher

        Returns:
            Scopus Author ID if found, None otherwise
        """
        from papers_please.client.OrcidAPIClient import OrcidAPIClient

        try:
            orcid_client = OrcidAPIClient()
            data = orcid_client.get_researcher_data(orcid_id)

            # Look for external identifiers
            person = data.get("person", {})
            external_ids = person.get("external-identifiers", {}).get("external-identifier", [])

            for ext_id in external_ids:
                if (
                    isinstance(ext_id, dict)
                    and "external-id-type" in ext_id
                    and ext_id.get("external-id-type", "").lower() == "scopus author id"
                ):
                    return ext_id.get("external-id-value", None)

            return None

        except Exception as e:
            print(f"Error extracting Scopus ID from ORCID {orcid_id}: {e}")
            return None

    def search_scopus(self, query: str, count: int = 25, start: int = 0) -> dict:
        """Perform a search using the Scopus Search API.

        Args:
            query: Search query (e.g., 'AU-ID(123456)', 'DOI("10.1000/example")')
            count: Number of results to return (default 25, max 200)
            start: Starting index for results (default 0)

        Returns:
            Dictionary with search results

        Raises:
            Exception: If the request fails
        """
        url = f"{self._BASE_URL}/search/scopus" + f"?query={query}" + f"&count={count}" + f"&start={start}"

        response = requests.get(url, headers=self._headers, timeout=30)

        if response.status_code == 200:
            return dict(response.json())
        else:
            raise Exception(f"Scopus search failed: {response.status_code} - {response.text}")

    def get_author_by_scopus_id(self, scopus_id: str) -> dict:
        """Get author data by Scopus Author ID using search API.

        Args:
            scopus_id: Scopus Author ID

        Returns:
            Dictionary with author data

        Raises:
            Exception: If the request fails
        """
        # Use search API with AU-ID query instead of direct author endpoint
        query = f"AU-ID({scopus_id})"

        try:
            search_result = self.search_scopus(query)
            search_results = search_result.get("search-results", {})
            entries = search_results.get("entry", [])

            if entries:
                # Return aggregated author info from search results
                return {
                    "scopus_id": scopus_id,
                    "total_documents": search_results.get("opensearch:totalResults", "0"),
                    "publications": entries,
                }
            else:
                return {}

        except Exception as e:
            print(f"Error fetching author by Scopus ID {scopus_id}: {e}")
            return {}

    def get_work_by_doi(self, doi: str) -> dict | None:
        """Get publication data through DOI.

        Args:
            doi: DOI of the publication

        Returns:
            Dictionary with publication data or None if not found

        Raises:
            Exception: If the request fails with error different from 404
        """
        doi = doi.strip().lower()

        if doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        elif doi.startswith("doi:"):
            doi = doi.replace("doi:", "")

        query = f'DOI("{doi}")'

        try:
            result = self.search_scopus(query)

            search_results = result.get("search-results", {})
            entries = search_results.get("entry", [])

            if entries and len(entries) > 0:
                return dict(entries[0])
            else:
                print(f"DOI {doi} not found in Scopus")
                return None

        except Exception as e:
            print(f"Error fetching DOI {doi}: {e}")
            return None

    def get_metrics_for_entity(self, entity) -> dict:
        """Get metrics for a researcher or research group.

        Args:
            entity: Researcher or research group

        Returns:
            Dictionary with aggregated metrics
        """
        from papers_please.core.Researcher import Researcher
        from papers_please.core.ResearchGroup import ResearchGroup

        if isinstance(entity, Researcher):
            return self.get_author_metrics(entity.id)
        elif isinstance(entity, ResearchGroup):
            total_publications = 0
            total_citations = 0
            publications_per_year: dict[str, int] = {}
            publications_by_type: dict[str, int] = {}
            h_index_sum = 0
            avg_h_index = 0.0
            top_subject_areas = []

            unique_dois = set()

            for researcher in entity.researchers:
                try:
                    metrics = self.get_author_metrics(researcher.id)

                    researcher_papers = researcher.papers
                    unique_dois.update(researcher_papers[researcher_papers["doi"].notna()]["doi"].tolist())

                    if isinstance(metrics.get("publications_per_year", {}), dict):
                        for year, count in metrics["publications_per_year"].items():
                            y = str(year)
                            if isinstance(count, int):
                                publications_per_year[y] = publications_per_year.get(y, 0) + count

                    if isinstance(metrics.get("total_citations", 0), int):
                        total_citations += metrics["total_citations"]

                    if isinstance(metrics.get("h_index", 0), int):
                        h_index_sum += metrics["h_index"]

                    if isinstance(metrics.get("publications_by_type", {}), dict):
                        for pub_type, count in metrics["publications_by_type"].items():
                            pt = str(pub_type)
                            if isinstance(count, int):
                                publications_by_type[pt] = publications_by_type.get(pt, 0) + count

                    if isinstance(metrics.get("top_subject_areas", []), list):
                        top_subject_areas.extend(metrics["top_subject_areas"])

                except Exception as e:
                    print(f"Error obtaining metrics for researcher {researcher.id}: {e}")

            total_publications += len(unique_dois)

            num_researchers = len(entity.researchers)
            if num_researchers > 0:
                avg_h_index = h_index_sum / num_researchers

            # Aggregate subject areas
            area_counts: dict[str, int] = {}
            for area in top_subject_areas:
                area_name = area.get("name", "")
                area_counts[area_name] = area_counts.get(area_name, 0) + 1

            top_subject_areas = [{"name": name, "count": count} for name, count in area_counts.items()]
            top_subject_areas.sort(key=lambda x: x["count"], reverse=True)
            top_subject_areas = top_subject_areas[:5]

            return {
                "total_publications": total_publications,
                "total_citations": total_citations,
                "publications_per_year": publications_per_year,
                "publications_by_type": publications_by_type,
                "avg_h_index": avg_h_index,
                "top_subject_areas": top_subject_areas,
            }
        else:
            raise ValueError("Entity must be either a Researcher or a ResearchGroup")

    def get_author_metrics(self, orcid_id: str) -> dict:
        """Get metrics directly for a researcher by ORCID ID.

        Args:
            orcid_id: ORCID ID of the researcher

        Returns:
            Dictionary with researcher metrics
        """
        try:
            # First, get Scopus Author ID from ORCID
            scopus_id = self.get_scopus_id_from_orcid(orcid_id)

            if not scopus_id:
                return {
                    "error": "Scopus Author ID not found in ORCID profile",
                    "total_publications": 0,
                    "total_citations": 0,
                    "h_index": 0,
                    "publications_per_year": {},
                    "publications_by_type": {},
                    "top_subject_areas": [],
                    "metrics_source": ["Scopus"],
                }

            # Get all publications for this author using search API
            author_query = f"AU-ID({scopus_id})"
            search_results = self.search_scopus(author_query, count=25)  # Get more results for metrics

            search_data = search_results.get("search-results", {})
            total_publications = int(search_data.get("opensearch:totalResults", 0))
            entries = search_data.get("entry", [])

            # Calculate metrics from search results
            total_citations = 0
            publications_per_year: dict = {}
            publications_by_type: dict = {}
            subject_areas_count: dict = {}

            for entry in entries:
                # Citations
                citations = int(entry.get("citedby-count", 0))
                total_citations += citations

                # Publication year
                pub_date = entry.get("prism:coverDate", "")
                if pub_date:
                    year = pub_date.split("-")[0]
                    publications_per_year[year] = publications_per_year.get(year, 0) + 1

                # Publication type
                doc_type = entry.get("prism:aggregationType", "unknown")
                publications_by_type[doc_type] = publications_by_type.get(doc_type, 0) + 1

                # Subject areas (if available)
                if "subject-areas" in entry:
                    areas = entry.get("subject-areas", {}).get("subject-area", [])
                    if isinstance(areas, list):
                        for area in areas:
                            if isinstance(area, dict):
                                area_name = area.get("$", "")
                                if area_name:
                                    subject_areas_count[area_name] = subject_areas_count.get(area_name, 0) + 1
                    elif isinstance(areas, dict):
                        area_name = areas.get("$", "")
                        if area_name:
                            subject_areas_count[area_name] = subject_areas_count.get(area_name, 0) + 1

            # Calculate h-index (simplified - would need citation counts per paper for exact calculation)
            # For now, use a rough estimation based on total citations and publications
            h_index = min(total_publications, int(total_citations**0.5)) if total_citations > 0 else 0

            # Top subject areas
            top_subject_areas = [
                {"name": name, "count": count}
                for name, count in sorted(subject_areas_count.items(), key=lambda x: x[1], reverse=True)[:5]
            ]

            return {
                "total_publications": total_publications,
                "total_citations": total_citations,
                "h_index": h_index,
                "publications_per_year": publications_per_year,
                "publications_by_type": publications_by_type,
                "top_subject_areas": top_subject_areas,
                "scopus_author_id": scopus_id,
                "metrics_source": ["Scopus"],
            }

        except Exception as e:
            print(f"Error obtaining author metrics with ORCID {orcid_id}: {e}")
            return {
                "error": str(e),
                "total_publications": 0,
                "total_citations": 0,
                "h_index": 0,
                "publications_per_year": {},
                "publications_by_type": {},
                "top_subject_areas": [],
                "metrics_source": ["Scopus"],
            }

    def get_metrics_for_work(self, doi: str) -> dict:
        """Extract relevant metrics from a publication.

        Args:
            doi: DOI of the publication

        Returns:
            Dictionary with publication metrics
        """
        try:
            work = self.get_work_by_doi(doi)

            if work is None:
                return {
                    "doi": doi,
                    "title": "",
                    "cited_by_count": 0,
                    "publication_year": None,
                    "publication_date": None,
                    "type": "",
                    "journal_name": "",
                    "journal_issn": "",
                    "source": "Scopus",
                    "subject_areas": [],
                    "error": "DOI not found",
                }

            # Extract metrics from Scopus work data
            title = work.get("dc:title", "")
            cited_by_count = int(work.get("citedby-count", 0))

            # Publication date
            cover_date = work.get("prism:coverDate", "")
            publication_year = None
            publication_date = cover_date

            if cover_date:
                try:
                    publication_year = int(cover_date.split("-")[0])
                except (ValueError, IndexError):
                    print(f"Invalid cover date format for DOI {doi}: {cover_date}")
                    pass

            # Document type
            doc_type = work.get("prism:aggregationType", "")

            # Journal information
            journal_name = work.get("prism:publicationName", "")
            journal_issn = work.get("prism:issn", "")

            # DOI cleaning
            doi_clean = work.get("prism:doi", doi)
            if doi_clean and doi_clean.startswith("10."):
                pass  # Already clean
            else:
                doi_clean = doi

            # Subject areas (if available in search results)
            subject_areas = []
            if "subject-areas" in work:
                areas = work.get("subject-areas", {}).get("subject-area", [])
                if isinstance(areas, list):
                    for area in areas:
                        if isinstance(area, dict):
                            subject_areas.append({"name": area.get("$", ""), "code": area.get("@code", "")})
                elif isinstance(areas, dict):
                    subject_areas.append({"name": areas.get("$", ""), "code": areas.get("@code", "")})

            metrics = {
                "doi": doi_clean,
                "title": title,
                "cited_by_count": cited_by_count,
                "publication_year": publication_year,
                "publication_date": publication_date,
                "type": doc_type,
                "journal_name": journal_name,
                "journal_issn": journal_issn,
                "source": "Scopus",
                "subject_areas": subject_areas,
            }

            return metrics

        except Exception as e:
            print(f"Error extracting metrics for DOI {doi}: {e}")
            return {
                "doi": doi,
                "title": "",
                "cited_by_count": 0,
                "publication_year": None,
                "publication_date": None,
                "type": "",
                "journal_name": "",
                "journal_issn": "",
                "source": "Scopus",
                "subject_areas": [],
                "error": str(e),
            }

    def get_metrics_for_works(self, dois: list[str]) -> pd.DataFrame:
        """Extract relevant metrics for multiple publications.

        Args:
            dois: List of DOIs

        Returns:
            DataFrame with publication metrics
        """
        metrics_list = []

        max_dois = min(50, len(dois))
        sample_dois = dois[:max_dois]

        for doi in sample_dois:
            try:
                metrics = self.get_metrics_for_work(doi)
                metrics_list.append(metrics)
                time.sleep(0.5)  # Scopus has stricter rate limits
            except Exception as e:
                print(f"Error extracting metrics for DOI {doi}: {e}")
                metrics_list.append({"doi": doi, "error": str(e), "source": "Scopus"})

        df = pd.DataFrame(metrics_list)

        return df
