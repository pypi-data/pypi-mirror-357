"""Research group management module."""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from papers_please.core.Researcher import Researcher


class ResearchGroup:
    """Represents a research group containing multiple researchers."""

    def __init__(self, researchers: list["Researcher"]) -> None:
        """Initialize a research group with a list of researchers.

        Args:
            researchers: List of Researcher instances
        """
        self._researchers = researchers
        self._papers = None

    @property
    def papers(self) -> pd.DataFrame:
        """Get all papers from all researchers in the group, removing duplicates."""
        if self._papers is None:
            df = pd.DataFrame()
            for researcher in self.researchers:
                df = pd.concat([df, researcher.papers])

            self._papers = df.drop_duplicates(subset=["doi"])

        return self._papers

    @property
    def researchers(self) -> list["Researcher"]:
        """Get the list of researchers in the group."""
        return self._researchers
