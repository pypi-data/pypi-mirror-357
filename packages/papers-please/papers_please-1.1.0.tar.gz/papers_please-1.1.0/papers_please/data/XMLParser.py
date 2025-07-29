"""XML parser module for handling research data safely."""

try:
    from defusedxml import ElementTree  # noqa: N811
except ImportError:
    # Fallback to standard library with warning
    import warnings
    from xml.etree import ElementTree  # noqa: N811  # nosec B405

    warnings.warn(
        "defusedxml not available, using xml.etree.ElementTree. "
        "Install defusedxml for safer XML parsing: pip install defusedxml",
        UserWarning,
        stacklevel=2,
    )


class XMLParser:
    """XML parser for extracting research article data."""

    def __init__(self, xml_path: str) -> None:
        """Initialize XML parser with file path.

        Args:
            xml_path: Path to the XML file
        """
        self.xml_path = xml_path

    def extract_articles_bibtex(self) -> list[str]:
        """Extract articles and convert to BibTeX format."""
        tree = ElementTree.parse(self.xml_path)  # nosec B314
        root = tree.getroot()

        articles_bibtex = []
        for article in root.findall(".//ARTIGO-PUBLICADO"):
            basic_data = article.find("DADOS-BASICOS-DO-ARTIGO")
            details = article.find("DETALHAMENTO-DO-ARTIGO")
            if basic_data is None or details is None:
                continue

            title = basic_data.attrib.get("TITULO-DO-ARTIGO", "")
            year = basic_data.attrib.get("ANO-DO-ARTIGO", "")
            language = basic_data.attrib.get("IDIOMA", "")
            doi = basic_data.attrib.get("DOI", "")
            journal = details.attrib.get("TITULO-DO-PERIODICO-OU-REVISTA", "")
            volume = details.attrib.get("VOLUME", "")
            start_page = details.attrib.get("PAGINA-INICIAL", "")
            end_page = details.attrib.get("PAGINA-FINAL", "")
            issn = details.attrib.get("ISSN", "")

            authors = article.findall("AUTORES")
            names = [a.attrib.get("NOME-COMPLETO-DO-AUTOR") for a in authors]
            # Filter out None values and create author string
            names = [name for name in names if name is not None]
            author_bibtex = " and ".join(names) if names else "Unknown Author"

            # Create a safe key for the BibTeX entry
            entry_key = f"{names[0].split()[0].lower()}{year}" if names else f"unknown{year}"

            bibtex = f"""@article{{{entry_key},
  author = {{{author_bibtex}}},
  title = {{{title}}},
  journal = {{{journal}}},
  year = {{{year}}},
  volume = {{{volume}}},
  pages = {{{start_page}--{end_page}}},
  doi = {{{doi}}},
  issn = {{{issn}}},
  language = {{{language}}}
}}"""
            articles_bibtex.append(bibtex)

        return articles_bibtex

    def generate_bibtex(self, output_path: str) -> None:
        """Generate BibTeX file from extracted articles.

        Args:
            output_path: Path where the BibTeX file will be saved
        """
        articles_bibtex = self.extract_articles_bibtex()
        with open(output_path, "w", encoding="utf-8") as f:
            for article in articles_bibtex:
                f.write(article + "\n\n")
        print(f"BibTeX file generated successfully at: {output_path}")
