import germaparlpy.utilities as utilities
from germaparlpy.corpus import *
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s") # configure output

if __name__ == "__main__":

    # Clone the GermaParl corpus from GitHub. We specify the parent directory as target since we are one level lower.
    utilities.clone_corpus(directory="..")

    # we deserialize the XML corpus and specify the legislative periods as intervals. The interval range(16,20) in python
    # comprises 16, 17, 18 and 19 because intervals in python are right-open. Integer representing singular legislative
    # terms are also a valid argument.
    corpus = Corpus.deserialize_from_xml(range(16,20), path="../GermaParlTEI")

    # Retrieval of all speeches from members affiliated with the party SPD:
    partition_spd = corpus.get_speeches_from_party(party="SPD")

    # All speeches are enclosed within a sp element that is annotated with metadata in element attributes. Print all
    # attributes to determine, what to search for.
    # Output: ['who_original', 'party', 'parliamentary_group', 'who', 'name', 'position', 'role']
    unique_element_attributes = utilities.extract_element_attributes(corpus, tag="sp")
    print(unique_element_attributes)

    # After retrieving the attribute names, we can search the corpus for unique values for a certain attribute. Let's
    # assume that you want to have a list of all annotated roles in the parliament.
    # Output: ['mp', 'presidency', 'parliamentary_commissioner', 'misc', 'government']
    unique_role_values = utilities.extract_attribute_values(corpus, tag="sp", attribute="role")
    print(unique_role_values)

    # Let's retrieve all speeches from all members of the cabinet in the corpus.
    partition_chancellor = corpus.get_speeches_from_role(role="goverment")

    # Retrieval methods can be chained. Let's assume that you want to retrieve all speeches from members of the CDU, which
    # are regular members of the parliament that contain the term "Wirtschaft" at least once. You can use the following
    # method chain for this:
    partition = (corpus.get_speeches_from_party(party="CDU")
               .get_speeches_from_role(role="mp")
               .get_speeches_from_keyword(keyword="Wirtschaft"))

    # You can get the actual content from the markup as a list of strings for further processing with toolkit methods:
    all_paragraphs = utilities.get_paragraphs_from_corpus(partition)
    all_interjections = utilities.get_interjections_from_corpus(partition)

    # You can use the built-in methods len() and bool() on corpus or partition objects.
    # Output: Our partition comprises 908 documents and 119462 paragraphs.
    print(f"Our partition comprises {len(partition)} documents and {len(all_paragraphs)} paragraphs.")

    # Partitions objects can be serialized as XML for human inspection, and Corpus and Partition instances can be
    # serialized in JSON for intermediate storage.
    partition.serialize_corpus_as_xml(path="../derived_corpus")

    # JSON serialization of a corpus object
    corpus.serialize(path="backup.json")

    # Deserialize a corpus:
    new_corpus = Corpus.deserialize_from_json(path="backup.json")