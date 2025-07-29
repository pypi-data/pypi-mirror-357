"""Module for calculating metrics for researchers and research groups."""

import pandas as pd


class Metrics:
    """Class for calculating metrics for researchers and research groups."""

    def __init__(self, scopus_api_key: str | None = None, openalex_email: str | None = None):
        """Initialize the metrics calculator.

        Args:
            scopus_api_key: Scopus API key (optional)
            openalex_email: Email for identification in the OpenAlex API (optional)
        """
        from papers_please.client.OpenAlexAPIClient import OpenAlexAPIClient
        from papers_please.client.ScopusAPIClient import ScopusAPIClient

        self.scopus_client = ScopusAPIClient(api_key=scopus_api_key) if scopus_api_key else None
        self.openalex_client = OpenAlexAPIClient(email=openalex_email)

    def get_metrics_for_entity(
        self,
        entity,
        use_scopus: bool = True,
        use_openalex: bool = True,
    ) -> dict:
        """Calculate metrics for a researcher or research group.

        Args:
            entity: Researcher or research group
            use_scopus: If True, uses the Scopus API to obtain metrics
            use_openalex: If True, uses the OpenAlex API to obtain metrics

        Returns:
            Dictionary with aggregated metrics
        """
        total_publications = 0
        total_citations = 0
        h_index = 0
        i10_index = 0
        publications_per_year = {}
        publications_by_type = {}
        metrics_source = []
        open_access_percentage = 0.0
        top_concepts = []
        top_subject_areas = []
        scopus_author_id = None

        if use_openalex and self.openalex_client:
            try:
                openalex_metrics = self.openalex_client.get_metrics_for_entity(entity)

                if not openalex_metrics.get("error"):
                    total_publications = openalex_metrics.get("total_publications", 0)
                    total_citations = openalex_metrics.get("total_citations", 0)
                    h_index = openalex_metrics.get("h_index", 0)
                    i10_index = openalex_metrics.get("i10_index", 0)
                    publications_per_year = openalex_metrics.get("publications_per_year", {})
                    publications_by_type = openalex_metrics.get("publications_by_type", {})
                    open_access_percentage = openalex_metrics.get(
                        "open_access_percentage", 0.0
                    ) or openalex_metrics.get("avg_open_access_percentage", 0.0)
                    top_concepts = openalex_metrics.get("top_concepts", [])

                    metrics_source.append("OpenAlex")

            except Exception as e:
                print(f"Error obtaining metrics from OpenAlex: {e}")

        if use_scopus and self.scopus_client:
            try:
                scopus_metrics = self.scopus_client.get_metrics_for_entity(entity)

                if not scopus_metrics.get("error"):
                    # If OpenAlex failed or wasn't used, use Scopus values
                    if "OpenAlex" not in metrics_source:
                        total_publications = scopus_metrics.get("total_publications", 0)
                        total_citations = scopus_metrics.get("total_citations", 0)
                        h_index = scopus_metrics.get("h_index", 0)
                        publications_per_year = scopus_metrics.get("publications_per_year", {})
                        publications_by_type = scopus_metrics.get("publications_by_type", {})

                    # Always get Scopus-specific data
                    scopus_author_id = scopus_metrics.get("scopus_author_id")
                    top_subject_areas = scopus_metrics.get("top_subject_areas", [])

                    # Use avg_h_index from research groups
                    if hasattr(entity, "researchers") and len(getattr(entity, "researchers", [])) > 1:
                        avg_h_index = scopus_metrics.get("avg_h_index", 0)
                        if avg_h_index > 0:
                            h_index = avg_h_index

                    metrics_source.append("Scopus")

            except Exception as e:
                print(f"Error obtaining metrics from Scopus: {e}")

        return {
            "total_publications": total_publications,
            "total_citations": total_citations,
            "h_index": h_index,
            "i10_index": i10_index,
            "publications_per_year": publications_per_year,
            "publications_by_type": publications_by_type,
            "metrics_source": metrics_source,
            "open_access_percentage": open_access_percentage,
            "top_concepts": top_concepts,
            "top_subject_areas": top_subject_areas,
            "scopus_author_id": scopus_author_id,
        }

    def get_metrics_for_works(
        self,
        entity,
        use_scopus: bool = True,
        use_openalex: bool = True,
    ) -> pd.DataFrame:
        """Get detailed metrics for each publication of a researcher or group.

        Args:
            entity: Researcher or research group
            use_scopus: If True, uses the Scopus API to obtain metrics
            use_openalex: If True, uses the OpenAlex API to obtain metrics

        Returns:
            DataFrame with detailed metrics for each publication
        """
        dois = self._get_dois(entity)

        if not dois:
            return pd.DataFrame()

        metrics_dfs = []

        if use_openalex and self.openalex_client:
            try:
                openalex_df = self.openalex_client.get_metrics_for_works(dois)
                if not openalex_df.empty:
                    metrics_dfs.append(openalex_df)
            except Exception as e:
                print(f"Error obtaining detailed metrics from OpenAlex: {e}")

        if use_scopus and self.scopus_client:
            try:
                scopus_df = self.scopus_client.get_metrics_for_works(dois)
                if not scopus_df.empty:
                    metrics_dfs.append(scopus_df)
            except Exception as e:
                print(f"Error obtaining detailed metrics from Scopus: {e}")

        if not metrics_dfs:
            return pd.DataFrame()

        combined_df = pd.concat(metrics_dfs, ignore_index=True)

        return combined_df

    def _get_dois(self, entity) -> list[str]:
        """Get the DOIs of publications from a researcher or group.

        Args:
            entity: Researcher or research group

        Returns:
            List of DOIs
        """
        papers_df = entity.papers

        dois_series = papers_df[papers_df["doi"].notna() & (papers_df["doi"] != "")]["doi"]
        dois: list[str] = [str(doi) for doi in dois_series.tolist()]

        return dois
