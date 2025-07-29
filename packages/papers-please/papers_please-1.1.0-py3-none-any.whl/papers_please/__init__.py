"""Papers Please - A tool for analyzing researcher and research group metrics."""

__version__ = "1.1.0"
__author__ = "Henrique Marques, Gabriel Barbosa, Renato Spessoto, Henrique Gomes, Eduardo Neves"

from .client.OpenAlexAPIClient import OpenAlexAPIClient
from .client.OrcidAPIClient import OrcidAPIClient
from .client.ScopusAPIClient import ScopusAPIClient
from .core.Metrics import Metrics
from .core.Researcher import Researcher
from .core.ResearchGroup import ResearchGroup
from .data.OrcidAPIDataParser import OrcidAPIDataParser
from .data.XMLParser import XMLParser

__all__ = [
    "Researcher",
    "ResearchGroup",
    "XMLParser",
    "OrcidAPIClient",
    "OrcidAPIDataParser",
    "Metrics",
    "OpenAlexAPIClient",
    "ScopusAPIClient",
]
