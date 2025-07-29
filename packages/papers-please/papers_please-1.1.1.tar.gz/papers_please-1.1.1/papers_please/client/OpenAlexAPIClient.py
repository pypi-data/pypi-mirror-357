"""Client for querying the OpenAlex API and obtaining publication metrics."""

import time

import pandas as pd
import requests


class OpenAlexAPIClient:
    """Client for querying the OpenAlex API and obtaining publication metrics."""

    _BASE_URL = "https://api.openalex.org"

    def __init__(self, email: str | None = None) -> None:
        """Initialize the OpenAlex client.

        Args:
            email: Optional email for API identification (polite pool)
        """
        self.email = email
        self._headers = {"Accept": "application/json"}

        if email:
            self._headers["User-Agent"] = f"Papers-Please ({email})"

    def get_author_by_orcid(self, orcid_id: str) -> dict:
        """Get author data directly by ORCID ID.

        Args:
            orcid_id: ORCID ID of the researcher.

        Returns:
            Dictionary with author data.

        Raises:
            Exception: If the request fails.
        """
        orcid_id = orcid_id.strip()

        url = f"{self._BASE_URL}/authors/https://orcid.org/{orcid_id}"

        response = requests.get(url, headers=self._headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data if isinstance(data, dict) else {}
        else:
            raise Exception(f"Error fetching author with ORCID {orcid_id}: {response.status_code}")

    def get_work_by_doi(self, doi: str) -> dict | None:
        """Get publication data through DOI.

        Args:
            doi: DOI of the publication.

        Returns:
            Dictionary with publication data or None if not found.

        Raises:
            Exception: If the request fails with error different from 404.
        """
        doi = doi.strip().lower()

        if doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        elif doi.startswith("doi:"):
            doi = doi.replace("doi:", "")

        url = f"{self._BASE_URL}/works/doi:{doi}"

        try:
            response = requests.get(url, headers=self._headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, dict):
                    return data
                else:
                    print(f"Empty or invalid response for DOI {doi}")
                    return None
            elif response.status_code == 404:
                print(f"DOI {doi} not found in OpenAlex")
                return None
            else:
                print(f"HTTP error {response.status_code} fetching DOI {doi}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching DOI {doi}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching DOI {doi}: {e}")
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
            avg_oa_percentage = 0.0
            top_concepts = []

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

                    if isinstance(metrics.get("open_access_percentage", 0.0), float):
                        avg_oa_percentage += metrics["open_access_percentage"]

                    if isinstance(metrics.get("publications_by_type", {}), dict):
                        for pub_type, count in metrics["publications_by_type"].items():
                            pt = str(pub_type)
                            if isinstance(count, int):
                                publications_by_type[pt] = publications_by_type.get(pt, 0) + count

                    if isinstance(metrics.get("top_concepts", []), list):
                        top_concepts.extend(metrics["top_concepts"])

                except Exception as e:
                    print(f"Error obtaining metrics for researcher {researcher.id}: {e}")

            total_publications += len(unique_dois)

            num_researchers = len(entity.researchers)
            if num_researchers > 0:
                avg_oa_percentage /= num_researchers

            concept_scores: dict[str, float] = {}
            for concept in top_concepts:
                name = concept.get("name", "")
                score = concept.get("score", 0)
                concept_scores[name] = concept_scores.get(name, 0) + score

            top_concepts = [
                {"name": name, "score": score / len(entity.researchers)} for name, score in concept_scores.items()
            ]
            top_concepts.sort(key=lambda x: float(x["score"]), reverse=True)
            top_concepts = top_concepts[:5]

            return {
                "total_publications": total_publications,
                "total_citations": total_citations,
                "publications_per_year": publications_per_year,
                "publications_by_type": publications_by_type,
                "avg_open_access_percentage": avg_oa_percentage,
                "top_concepts": top_concepts,
            }
        else:
            raise ValueError("Entity must be either a Researcher or a ResearchGroup")

    def get_author_metrics(self, orcid_id: str) -> dict:
        """Get metrics directly for a researcher by ORCID ID.

        Args:
            orcid_id: ORCID ID of the researcher.

        Returns:
            Dictionary with researcher metrics.
        """
        try:
            author = self.get_author_by_orcid(orcid_id)

            counts_by_year = author.get("counts_by_year", [])
            works_count = author.get("works_count", 0)
            cited_by_count = author.get("cited_by_count", 0)

            summary_stats = author.get("summary_stats", {})
            h_index = summary_stats.get("h_index", 0)
            i10_index = summary_stats.get("i10_index", 0)

            publications_per_year = {}
            for year_data in counts_by_year:
                year = year_data.get("year")
                works = year_data.get("works_count", 0)
                if year:
                    publications_per_year[str(year)] = works

            top_concepts = []
            for concept in author.get("x_concepts", []):
                top_concepts.append(
                    {
                        "name": concept.get("display_name", ""),
                        "score": concept.get("score", 0),
                    }
                )

            oa_percentage = 0.0
            publications_by_type: dict[str, int] = {}

            if author.get("works_api_url"):
                works_url = author.get("works_api_url") + "&per_page=100"
                works_response = requests.get(works_url, headers=self._headers, timeout=30)

                if works_response.status_code == 200:
                    works_data = works_response.json()
                    works_sample = works_data.get("results", [])

                    sample_size = len(works_sample)
                    if sample_size > 0:
                        oa_count = sum(1 for work in works_sample if work.get("open_access", {}).get("is_oa", False))
                        oa_percentage = (oa_count / sample_size) * 100

                        for work in works_sample:
                            work_type = work.get("type", "unknown")
                            publications_by_type[work_type] = publications_by_type.get(work_type, 0) + 1

            return {
                "total_publications": works_count,
                "total_citations": cited_by_count,
                "h_index": h_index,
                "i10_index": i10_index,
                "publications_per_year": publications_per_year,
                "open_access_percentage": oa_percentage,
                "top_concepts": top_concepts,
                "publications_by_type": publications_by_type,
                "metrics_source": ["OpenAlex"],
            }

        except Exception as e:
            print(f"Error obtaining author metrics with ORCID {orcid_id}: {e}")
            return {
                "error": str(e),
                "total_publications": 0,
                "total_citations": 0,
                "h_index": 0,
                "i10_index": 0,
                "publications_per_year": {},
                "open_access_percentage": 0,
                "top_concepts": [],
                "publications_by_type": {},
                "metrics_source": ["OpenAlex"],
            }

    def get_metrics_for_work(self, doi: str) -> dict:
        """Extract relevant metrics from a publication.

        Args:
            doi: DOI of the publication.

        Returns:
            Dictionary with publication metrics.
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
                    "open_access": False,
                    "journal_name": "",
                    "journal_issn": "",
                    "source": "OpenAlex",
                    "concepts": [],
                    "error": "DOI not found",
                }

            doi_clean = work.get("doi", "") if work else ""
            if doi_clean:
                doi_clean = doi_clean.replace("https://doi.org/", "")

            title = work.get("title", "") if work else ""
            cited_by_count = work.get("cited_by_count", 0) if work else 0
            publication_year = work.get("publication_year", None) if work else None
            publication_date = work.get("publication_date", None) if work else None
            work_type = work.get("type", "") if work else ""

            open_access_info = work.get("open_access", {}) if work else {}
            is_oa = open_access_info.get("is_oa", False) if open_access_info else False

            primary_location = work.get("primary_location", {}) if work else {}
            source_info = primary_location.get("source", {}) if primary_location else {}
            journal_name = source_info.get("display_name", "") if source_info else ""
            journal_issn = source_info.get("issn_l", "") if source_info else ""

            concepts_list = work.get("concepts", []) if work else []
            concepts = []
            for c in concepts_list[:5]:
                if c:
                    concepts.append(
                        {
                            "name": c.get("display_name", "") if c else "",
                            "score": c.get("score", 0) if c else 0,
                            "level": c.get("level", 0) if c else 0,
                        }
                    )

            metrics = {
                "doi": doi_clean,
                "title": title,
                "cited_by_count": cited_by_count,
                "publication_year": publication_year,
                "publication_date": publication_date,
                "type": work_type,
                "open_access": is_oa,
                "journal_name": journal_name,
                "journal_issn": journal_issn,
                "source": "OpenAlex",
                "concepts": concepts,
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
                "open_access": False,
                "journal_name": "",
                "journal_issn": "",
                "source": "OpenAlex",
                "concepts": [],
                "error": str(e),
            }

    def get_metrics_for_works(self, dois: list[str]) -> pd.DataFrame:
        """Extract relevant metrics for multiple publications.

        Args:
            dois: List of DOIs.

        Returns:
            DataFrame with publication metrics.
        """
        metrics_list = []

        max_dois = min(50, len(dois))
        sample_dois = dois[:max_dois]

        for doi in sample_dois:
            try:
                metrics = self.get_metrics_for_work(doi)
                metrics_list.append(metrics)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error extracting metrics for DOI {doi}: {e}")
                metrics_list.append({"doi": doi, "error": str(e), "source": "OpenAlex"})

        df = pd.DataFrame(metrics_list)

        return df
