import germaparlpy.utilities as utilities
from germaparlpy.corpus import *
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s") # configure output

if __name__ == "__main__":

    # Clone the GermaParl corpus from GitHub. We specify the parent directory as target since we are one level lower.
    utilities.clone_corpus(directory="..")

    # We deserialize the XML corpus and specify the legislative periods as intervals. The interval range(19,20) in python
    # comprises only 19 because intervals in python are right-open.
    corpus = Corpus.deserialize_from_xml(lp=range(19,20), path="../GermaParlTEI")

    # Let's search speeches in our corpus that match a pattern. Let's assume that we're interested in data politics.
    # For that purpose, we define a regular expression that matches all speeches containing "Daten".
    data_regex = r".*[Dd]aten.*"

    partition_daten = corpus.get_speeches_from_regex(pattern=data_regex)

    # Let's assume that we are interested in interjections that people utter in the context of data.
    partition_daten_interjections = utilities.get_interjections_from_corpus(partition_daten)

    # Output: There are 26167 interjections to speeches containing the term 'Daten'.
    # That's quite a lot, since we have also matched unwanted terms like "Soldaten".
    # Regular expressions are computationally intensive and prone to producing false positives if you are not
    # conscientious enough.
    print(f"There are {len(partition_daten_interjections)} interjections to speeches containing the term 'Daten'")
    print(partition_daten_interjections)

    # Serialize for human inspection.
    partition_daten.serialize_corpus_as_xml(path="../corpus_daten")