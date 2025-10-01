"""
This module implements the classes Corpus and Partition to deserialize, manage and query corpus objects.
"""

from __future__ import annotations

import json
import logging
import os
import re
import xml.etree.ElementTree as ElementTree
from collections.abc import Callable
from copy import deepcopy
from xml.etree.ElementTree import Element
from datetime import datetime
from pathlib import Path
from typing import Any
from germaparlpy import __version__

logger = logging.getLogger("germaparlpy")

class Corpus:
    """
    This class implements the corpus as a Python object. It provides methods to deserialize and manage corpora as well
    as the retrieval of corpus partitions and metadata.
    """
    def __init__(self, corpus: dict =None):
        if corpus is None:
            corpus = {}

        self.corpus = corpus

    @staticmethod
    def deserialize_from_json(path: str) -> Corpus:
        """
        Factory Method for creating Corpus objects from a JSON file. The JSON file should have been created by the
        object method serialize().

        Args:
            path: The path and the name of the JSON file.
        Returns:
            A Corpus object built from the specified JSON file.
        """
        new_corpus = Corpus()
        new_corpus.corpus = {}

        try:
            with open(Path(path), "r", encoding='utf-8') as f:
                new_corpus.corpus = json.load(f)

            for key in new_corpus.get_corpus().keys():
                xml_string = new_corpus.corpus[key]["body"]
                try:
                    new_corpus.corpus[key]["body"] = ElementTree.fromstring(xml_string)
                except ElementTree.ParseError as e:
                    logger.error(f"Invalid XML format in {key}:\n{e}")

            logger.info(f"The object was successfully loaded from {path}.")
        except FileNotFoundError as e:
            logger.error(f"No file at {path}:\n{e}")
        except json.decoder.JSONDecodeError as e:
            logger.error(f"The file {path} is no valid JSON file:\n{e}")
        except Exception as e:
            logger.error(f"An unexpected exception occurred:\n{e}")
        finally:
            return new_corpus

    @staticmethod
    def deserialize_from_xml(lp: range | int = range(1, 20),
                             path: str = "GermaParlTEI") -> Corpus:
        """
        Factory Method for creating Corpus objects from an XML corpus. The XML corpus should comply with the structure
        of the original GermaParlTEI Corpus that is fetched with utilities.clone_corpus() or created with
        Partition.serialize_corpus_as_xml.

        Args:
            lp: The legislative term(s) as range or integer. Please note that the corpus comprises 19 terms.
            path: The path to the corpus can be adjusted in the case of a custom corpus.
        Returns:
            A Corpus object built from a xml corpus.
        """
        new_corpus = Corpus()
        if isinstance(lp, range):
            for i in lp:
                if i == 20:
                    logger.warning("The corpus comprises 19 legislative terms. Aborting...")
                    break
                new_corpus.__load_xml_for_legislative_period(i, path)
        elif lp > 19:
            logger.warning("The corpus comprises 19 legislative terms. An empty corpus object is given back.")
        else:
            new_corpus.__load_xml_for_legislative_period(lp, path)

        return new_corpus

    def __load_xml_for_legislative_period(self, lp: int, path: str) -> None:
        """
        Loads all protocols, including metadata of a legislative period, into the object variable corpus.

        Args:
            lp: The legislative period.
        """

        try:
            for entry in Path(f"{path}/0{lp}" if lp < 10 else f"{path}/{lp}").iterdir():
                try:
                    tree = ElementTree.parse(entry)
                except ElementTree.ParseError as e:
                    logger.error(f"Error parsing XML file {entry}. Continue with next file:\n {e}")
                    continue
                key = entry.name[3:-4]
                self.corpus[key] = {}
                self.corpus[key]["body"] = tree.getroot().find(".//text/body")
                self.corpus[key].update(Corpus.__extract_metadata(tree))
        except FileNotFoundError as e:
            logger.error(f"Make sure that the directory {path} exists and contains a well structured corpus."
                         "Call the function utilities.clone_corpus() to fetch the corpus from github\n"
                          f"{e}")
        except Exception as e:
            logger.error(f"An unexpected exception occurred:\n{e}")
            return

    def serialize(self, path: str) -> None:
        """
        Serialize a Corpus object as JSON file, that you can deserialize with Corpus.deserialize_from_json().

        Args:
            path: The path and name of the JSON file.
        """
        corpus_json = self.get_corpus(deep = True)

        for key in corpus_json.keys():
            corpus_json[key]["body"] = ElementTree.tostring(corpus_json[key]["body"], encoding='utf-8').decode('utf-8')
        try:
            with open(Path(path), "w", encoding='utf-8') as f:
                json.dump(corpus_json, f, indent=4, ensure_ascii=False)
        except FileNotFoundError as e:
            logger.error(f"A directory in {path} does not exist: {e}")
            return
        except PermissionError:
            logger.error(f"Permission denied when trying to create the directory {path}.")
            return

        logger.info(f"The corpus object was successfully serialized in {path}.")

    def get_corpus(self, deep: bool = False) -> dict[str, dict[str, Any]]:
        """
        Getter Method for a copy of the object variable corpus.

        Args:
            deep: If true, a deep copy of the object corpus is created.
        Returns:
            A copy of the object variable corpus.
        """
        return self.corpus.copy() if not deep else deepcopy(self.corpus)

    def get_metadata(self, key: str) -> dict[str, str]:
        """
        Gets the metadata for a specified session.

        Args:
            key: The corpus entry (#legislativePeriod_#sessionNumber).
        Returns:
            The metadata on the corpus entry, i.e., the document.
        """
        metadata = {}
        try:
            metadata = self.corpus[key].copy()
            metadata.pop("body", None)
        except KeyError as e:
            logger.error(f"Make sure, that key {key} exists in the objects corpus:\n"
                         f"{e}")
        except Exception as e:
            logger.error(f"An unexpected exception occurred:\n"
                         f"{e}")
        finally:
            return metadata

    def get_partition_by_sp_attribute(self,
                                      attribute: str,
                                      value: str) -> Partition:
        """
        Collects all div-elements and their matching child elements in the corpus, if a children sp-element matches a
        specified attribute and value pair. The div-element containing the matched sp-element is collected, plus all
        child elements of sp. All sp-elements within the parent div-element that do not fulfill the condition, are not
        collected. All collected elements are assembled within a new ElementTree with a <body>-element as the root. The
        new corpus is indexed with the old key and the old metadata within a Partition Object.

        Args:
            attribute: The attribute of the sp-elements to look for.
            value: The value of the specified attribute to look for.
        Returns:
              An Object from the class Partition containing only the specified elements plus metadata.
        """

        partition_corpus = {}

        corpus_copy = self.get_corpus(deep=True)

        for entry in corpus_copy.keys():

            entry_value = corpus_copy.get(entry, {})
            root = entry_value.get("body")

            new_body = ElementTree.Element("body")

            for div_element in root.findall(f".//div"):
                speeches = []
                for sp_element in div_element.findall(f".//sp[@{attribute}='{value}']"):
                    speeches.append(sp_element)

                if speeches:

                    metadata = entry_value
                    metadata.pop("body", None)
                    new_div = ElementTree.Element("div", attrib=div_element.attrib)

                    for elem in speeches:
                        new_div.append(elem)

                    new_body.append(new_div)

                    partition_corpus[entry] = {**metadata, "body": new_body}
                else:
                    continue

        return Partition(partition_corpus)

    def get_speeches_from_politician(self,
                                     person: str,
                                     attribute_name: str = "name") -> Partition:
        """
        Collects all speeches of a specified politician (sp-elements plus children and parent div-element) in the corpus
        and returns a new partition object.
        Args:
            person: The person's name to search for.
            attribute_name: The sp-elements attribute name to search for.
        Returns:
            An object from the class Partition containing only the specified elements plus metadata.
        """
        return self.get_partition_by_sp_attribute(attribute=attribute_name, value=person)

    def get_speeches_from_party(self, party: str) -> Partition:
        """
        Collects all speeches from persons of a specified party (sp-elements plus children and parent div-element) in
        the corpus and returns a new partition object.
        Args:
            party: The party's name to search for.
        Returns:
              An object from the class Partition containing only the specified elements plus metadata.
        """
        return self.get_partition_by_sp_attribute(attribute="party", value=party)

    def get_speeches_from_role(self,
                               role: str,
                               attribute_name: str = "role") -> Partition:
        """
        Collects all speeches from persons in a specified role (sp-elements plus children and parent div-element) in the
        corpus and returns a new partition object.
        Args:
            role: The role to search for.
            attribute_name: The sp-element attribute name to match.
        Returns:
              An object from the class Partition containing only the specified elements plus metadata.
        """
        return self.get_partition_by_sp_attribute(attribute=attribute_name, value=role)

    def _get_speeches_from_condition(self, condition: Callable[[str], bool]) -> Partition:
        """
        Collects all speeches (sp-element plus children and parent div-element), whose content match a condition.

        Args:
            condition: A function that takes a string (p.text) and returns a boolean.

        Returns:
            A Partition object containing only the matching elements plus metadata.
        """
        partition_corpus = {}

        corpus_copy = self.get_corpus(deep=True)

        for entry in corpus_copy.keys():

            entry_value = corpus_copy.get(entry, {})
            root = entry_value.get("body")

            new_body = ElementTree.Element("body")
            for div_element in root.findall(f".//div"):
                speeches = []
                for sp_element in div_element.findall(f".//sp"):
                    for p in sp_element.findall(".//p"):
                        if p.text and condition(p.text):
                            speeches.append(sp_element)
                            break

                if speeches:

                    metadata = entry_value
                    metadata.pop("body", None)
                    new_div = ElementTree.Element("div", attrib=div_element.attrib)

                    for elem in speeches:
                        new_div.append(elem)

                    new_body.append(new_div)

                    partition_corpus[entry] = {**metadata, "body": new_body}
                else:
                    continue

        return Partition(partition_corpus)

    def get_speeches_from_keyword(self,
                                  keyword: str,
                                  case_sensitive: bool = False) -> Partition:
        """
        Collects all speeches (sp-element plus children and parent div-element), whose content contains a keyword.

        Args:
            keyword: The keyword to search for.
            case_sensitive: If True, the method will conduct a case-sensitive search.

        Returns:
            A Partition object containing only the matching elements plus metadata.
        """
        if case_sensitive:
            condition = lambda text: keyword in text
        else:
            condition = lambda text: keyword.lower() in text.lower()

        return self._get_speeches_from_condition(condition=condition)

    def get_speeches_from_word_list(self,
                                    word_list: list[str],
                                    case_sensitive: bool = False) -> Partition:
        """
        Collects all speeches (sp-element plus children and parent div-element), whose content contains any of the
        keywords in the specified word list.

        Args:
            word_list: The keywords to search for.
            case_sensitive: If True, the method will conduct a case-sensitive search.

        Returns:
            A Partition object containing only the matching elements plus metadata.
        """
        if case_sensitive:
            condition = lambda text: any(word in text for word in word_list)
        else:
            condition = lambda text: any(word.lower() in text.lower() for word in word_list)

        return self._get_speeches_from_condition(condition=condition)

    def get_speeches_from_regex(self, pattern: str) -> Partition:
        """
        Collects all speeches (sp-element plus children and parent div-element), whose content contains pattern
        specified by a regular expression.

        Args:
            pattern: The pattern to search for as a raw string.
        Returns:
            A Partition object containing only the matching elements plus metadata.
        """
        return self._get_speeches_from_condition(condition = lambda text: bool(re.search(pattern, text)))

    def __len__(self) -> int:
        """
        Returns the number of elements in the corpus.

        Returns:
            The number of elements, based on the length of the instance variable corpus.
        """
        return len(self.corpus)

    def __bool__(self) -> bool:
        """
        Determines whether the corpus is non-empty.

        Returns:
            `True` if the instance variable corpus is not empty, otherwise `False`.
        """
        return bool(self.corpus)

    @staticmethod
    def __extract_metadata(tree: ElementTree) -> dict[str, str]:
        """
        Extracts all metadata about a document from the <teiHeader> element.

        Args:
            tree: The document's element tree.
        Returns:
            The metadata as a dictionary.
        """
        root = tree.getroot()
        header = root.find(".//teiHeader")

        metadata = {
            "title": Corpus.__get_text(header, ".//titleStmt/title"),
            "legislative_period": Corpus.__get_text(header, ".//titleStmt/legislativePeriod"),
            "session_no": Corpus.__get_text(header, ".//titleStmt/sessionNo"),
            "publisher": Corpus.__get_text(header, ".//publicationStmt/publisher"),
            "publication_date": Corpus.__get_text(header, ".//publicationStmt/date"),
            "filetype": Corpus.__get_text(header, ".//sourceDesc/filetype"),
            "url": Corpus.__get_text(header, ".//sourceDesc/url"),
            "source_date": Corpus.__get_text(header, ".//sourceDesc/date"),
            "project": Corpus.__get_text(header, ".//encodingDesc/projectDesc"),
            "edition_package": Corpus.__get_text(header, ".//editionStmt/edition/package"),
            "edition_version": Corpus.__get_text(header, ".//editionStmt/edition/version"),
            "edition_birthday": Corpus.__get_text(header, ".//editionStmt/edition/birthday"),
        }
        return metadata
    
    @staticmethod
    def __get_text(element: Element, path: str) -> str:
        """
        Extracts the text from an element's child.

        Args:
            element: The element.
            path: The path to the child element.
        Returns:
            The content of the specified element.
        """
        found = element.find(path)
        return found.text.strip() if found is not None and found.text else ""

class Partition(Corpus):
    """
    This class implements a partition of a corpus as objects. Objects of this class are created by the retrieval methods
    of the parent class Corpus.
    """

    def __init__(self, corpus: dict = None):
        super().__init__(corpus)

    def serialize_corpus_as_xml(self, path: str = "derived_corpus") -> None:
        """
        Serializes the corpus as a set of XML files. Generates an XML file for every entry in the corpus in a specified folder
        that is created during runtime under "path".

        Args:
            path: The path and name of the folder to be created.
        """
        try:
            os.mkdir(path)
        except FileExistsError:
            logger.warning(f"The directory or file {path} already exists. Aborting...")
            return
        except PermissionError:
            logger.error(f"Permission denied when trying to create the directory {path}.")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return

        corpus_copy = self.get_corpus(deep=True)
        existing_dirs = set()
        for key in corpus_copy.keys():

            lp = key[:2]
            if lp not in existing_dirs:
                os.mkdir(f"{path}/{lp}")
                existing_dirs.add(lp)

            new_root = ElementTree.Element("TEI")
            new_root.append(Partition.__create_tei_header(self.get_metadata(key)))
            text_element = ElementTree.Element("text")
            text_element.append(corpus_copy[key]["body"])
            new_root.append(text_element)

            with open(Path(f"{path}/{lp}/BT_{key}.xml"), "wb") as f:
                tree = ElementTree.ElementTree(new_root)
                tree.write(f, encoding="utf-8", xml_declaration=True)

        logger.info(f"The corpus was successfully serialized as XML document collection in {path}.")

    @staticmethod
    def __create_tei_header(metadata: dict) -> Element:
        """
        Creates a <teiHeader> element from the given metadata dictionary.

        Args:
            metadata: The metadata dictionary.
        Returns:
            The <teiHeader> element as an Element object.
        """
        tei_header = ElementTree.Element("teiHeader")
        file_desc = ElementTree.SubElement(tei_header, "fileDesc")
        title_stmt = ElementTree.SubElement(file_desc, "titleStmt")
        ElementTree.SubElement(title_stmt, "title").text = metadata.get("title", "")
        ElementTree.SubElement(title_stmt, "legislativePeriod").text = metadata.get("legislative_period", "")
        ElementTree.SubElement(title_stmt, "sessionNo").text = metadata.get("session_no", "")

        publication_stmt = ElementTree.SubElement(file_desc, "publicationStmt")
        ElementTree.SubElement(publication_stmt, "publisher").text = metadata.get("publisher", "")
        ElementTree.SubElement(publication_stmt, "date").text = metadata.get("publication_date", "")

        source_desc = ElementTree.SubElement(file_desc, "sourceDesc")
        ElementTree.SubElement(source_desc, "filetype").text = metadata.get("filetype", "")
        ElementTree.SubElement(source_desc, "url").text = metadata.get("url", "")
        ElementTree.SubElement(source_desc, "date").text = metadata.get("source_date", "")
        ElementTree.SubElement(source_desc, "secondaryDataSource").text = ("Blaette, A.and C. Leonhardt. Germaparl corpus"
                                                                  " of plenary protocols. v2.2.0-rc1, Zenodo, 22 July"
                                                                  " 2024, doi:10.5281/zenodo.12795193")
        ElementTree.SubElement(source_desc, "secondaryDataSourceLicense").text = "CLARIN PUB+BY+NC+SA license"

        encoding_desc = ElementTree.SubElement(tei_header, "encodingDesc")
        ElementTree.SubElement(encoding_desc, "projectDesc").text = "GermaParlPy"

        edition_stmt = ElementTree.SubElement(tei_header, "editionStmt")
        edition = ElementTree.SubElement(edition_stmt, "edition")
        ElementTree.SubElement(edition, "package").text = "GermaParlPy"
        ElementTree.SubElement(edition, "version").text = __version__
        ElementTree.SubElement(edition, "birthday").text = datetime.today().strftime("%Y-%m-%d")

        return tei_header