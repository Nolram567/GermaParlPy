"""
This module implements serves as a toolkit with functions to retrieve information from Corpus objects and to fetch the
TEI-Corpus from GitHub.
"""

import logging
import subprocess
from xml.etree.ElementTree import Element
import os

from germaparlpy.corpus import Corpus

logger = logging.getLogger("germaparlpy")

def clone_corpus(repo_url="https://github.com/PolMine/GermaParlTEI.git", directory=".") -> None:
    """
    Clones a GitHub repository into a specified directory.

    Args:
        repo_url: The repository URL.
        directory: The directory where the repository should be cloned.
    """
    destination = os.path.join(directory, "GermaParlTEI")

    if os.path.exists(destination):
        logger.info(f"The directory '{destination}' already exists and presumably contains the corpus. If you want"
                     f" to reload the corpus, please delete the directory beforehand.")
        return

    try:
        subprocess.run(["git", "clone", repo_url, destination], check=True)
        logger.info("The corpus was successfully loaded.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: Make sure that {repo_url} (still) exists and that it does not "
                      f"require authentication:\n{e}")

def get_paragraphs_from_element(element: Element) -> list[str]:
    """
    Extracts the text content from all <p> elements that are descendants of the given element.
    Text from nested elements inside <p> elements will not be included.

    Args:
        element: The parent element from which all descendant <p> elements should be extracted.

    Returns:
        A list of text content from all <p> elements found in the subtree.
    """
    return [paragraph.text for paragraph in element.findall(".//p")]

def get_interjections_from_element(element: Element) -> list[str]:
    """
    Extracts the text content from all <stage> elements that are descendants of the given element.
    Stage elements in the GermaParl corpus are always interjections.
    Text from nested elements inside <stage> elements will not be included.

    Args:
        element: The parent element from which all descendant <stage> elements should be extracted.

    Returns:
        A list of text content from all <stage> elements found in the subtree.
    """
    return [stage.text for stage in element.findall(".//stage")]

def get_paragraphs_from_corpus(corpus: Corpus) -> list[str]:
    """
    Extracts the text content from all <p> elements, who contain the speeches without interjections from the given
    Corpus object.

    Args:
        corpus: The Corpus object.
    Returns:
        The text from all <p> elements of the given corpus.
    """
    paragraphs = []
    for value in corpus.get_corpus().values():
        paragraphs.extend(get_paragraphs_from_element(value["body"]))
    return paragraphs

def get_interjections_from_corpus(corpus: Corpus) -> list[str]:
    """
    Extracts the text content from all <p> elements, who contain the interjections to speeches from the given Corpus
    object.

    Args:
        corpus: The Corpus object.
    Returns:
        The text from all <p> elements of the given corpus.
    """
    interjections = []
    for value in corpus.get_corpus().values():
        interjections.extend(get_interjections_from_element(value["body"]))
    return interjections

def extract_element_attributes(corpus: Corpus, tag: str) -> list[str]:
    """
    Extracts all unique attributes of a specified tag from all documents in the corpus.

    Args:
        corpus: The Corpus object containing the documents.
        tag: The name of the tag whose attributes should be retrieved.
    Returns:
        A list of unique attributes found in the specified tag.
    """
    attributes = set()

    for doc_name, doc_data in corpus.get_corpus().items():
        body = doc_data.get("body")
        if body is not None:
            for e in body.findall(f".//{tag}"):
                attributes.update(e.attrib.keys())

    return list(attributes)

def extract_attribute_values(corpus: Corpus,
                             tag: str,
                             attribute: str) -> list[str]:
    """
    Extracts the values of a specific attribute from the specified tag across all documents in the corpus.

    Args:
        corpus: The Corpus object containing the documents.
        tag: The tag whose attributes should be searched.
        attribute: The name of the attribute whose values should be extracted.
    Returns:
        A list of unique values for the specified attribute.
    """
    attribute_values = set()

    for doc_name, doc_data in corpus.get_corpus().items():
        body = doc_data.get("body")
        if body is not None:
            for sp in body.findall(f".//{tag}"):
                if attribute in sp.attrib:
                    attribute_values.add(sp.attrib[attribute])

    return list(attribute_values)
