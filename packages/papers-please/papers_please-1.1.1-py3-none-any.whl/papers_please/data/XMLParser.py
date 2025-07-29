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

import html


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
        articles_bibtex = []
        tree = ElementTree.parse(self.xml_path)  # nosec B314
        root = tree.getroot()

        # Extract conference papers
        for article in root.findall(".//TRABALHO-EM-EVENTOS"):
            basic_data = article.find("DADOS-BASICOS-DO-TRABALHO")
            details = article.find("DETALHAMENTO-DO-TRABALHO")
            authors = article.findall("AUTORES")

            title = html.unescape(basic_data.attrib.get("TITULO-DO-TRABALHO", "").strip())
            year = basic_data.attrib.get("ANO-DO-TRABALHO", "").strip()
            booktitle = html.unescape(details.attrib.get("TITULO-DOS-ANAIS-OU-PROCEEDINGS", "").strip())
            publisher = html.unescape(details.attrib.get("NOME-DA-EDITORA", "").strip())
            pages_start = details.attrib.get("PAGINA-INICIAL", "").strip()
            pages_end = details.attrib.get("PAGINA-FINAL", "").strip()
            pages = f"{pages_start}-{pages_end}"  # Adjusted line length
            doi = basic_data.attrib.get("DOI", "").strip()  # Adjusted DOI extraction

            # Extract authors
            names = [html.unescape(a.attrib.get("NOME-COMPLETO-DO-AUTOR", "").strip()) for a in authors]
            names = [name for name in names if name]
            author_bibtex = " and ".join(names) if names else ""

            # Generate a unique key for the BibTeX entry
            entry_key = f"inproceedings{hash(title + year)}"

            # Skip entries with missing critical data
            if not title or not year or not booktitle:
                continue

            bibtex = f"""@inproceedings{{{entry_key},
  title   = {{{title}}},
  booktitle   = {{{booktitle}}},
  author = {{{author_bibtex}}},
  year = {{{year}}},
  publisher = {{{publisher}}},
  pages = {{{pages}}},
  doi = {{{doi}}}
}}"""
            articles_bibtex.append(bibtex)

        # Extract published articles
        for article in root.findall(".//ARTIGO-PUBLICADO"):
            basic_data = article.find("DADOS-BASICOS-DO-ARTIGO")
            details = article.find("DETALHAMENTO-DO-ARTIGO")
            authors = article.findall("AUTORES")

            title = html.unescape(basic_data.attrib.get("TITULO-DO-ARTIGO", "").strip())
            year = basic_data.attrib.get("ANO-DO-ARTIGO", "").strip()
            journal = html.unescape(details.attrib.get("TITULO-DO-PERIODICO-OU-REVISTA", "").strip())
            volume = details.attrib.get("VOLUME", "").strip()
            pages_start = details.attrib.get("PAGINA-INICIAL", "").strip()
            pages_end = details.attrib.get("PAGINA-FINAL", "").strip()
            pages = f"{pages_start}-{pages_end}"  # Adjusted line length
            doi = basic_data.attrib.get("DOI", "").strip()

            # Extract authors
            names = [html.unescape(a.attrib.get("NOME-COMPLETO-DO-AUTOR", "").strip()) for a in authors]
            names = [name for name in names if name]
            author_bibtex = " and ".join(names) if names else ""

            # Generate a unique key for the BibTeX entry
            entry_key = f"article{hash(title + year)}"

            # Skip entries with missing critical data
            if not title or not year or not journal:
                continue

            bibtex = f"""@article{{{entry_key},
  title   = {{{title}}},
  author  = {{{author_bibtex}}},
  year    = {{{year}}},
  journal = {{{journal}}},
  volume  = {{{volume}}},
  pages   = {{{pages}}},
  doi     = {{{doi}}}
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
        articles_bibtex = self.extract_articles_bibtex()
        with open(output_path, "w", encoding="utf-8") as f:
            for article in articles_bibtex:
                f.write(article + "\n\n")
        print(f"BibTeX file generated successfully at: {output_path}")
