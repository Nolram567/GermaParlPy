import matplotlib.pyplot as plt

import germaparlpy.utilities as utilities
from germaparlpy.corpus import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s") # configure output

if __name__ == "__main__":

    # Clone the GermaParl corpus from GitHub. We specify the parent directory as the target since we are one level below.
    utilities.clone_corpus(directory="..")

    # We deserialize the XML corpus without specifying a legislative period. The default value is range(1, 20), which
    # includes the entire corpus.
    corpus = Corpus.deserialize_from_xml(path="../GermaParlTEI")

    # Let's assume we want to calculate the type-token ratio of all German chancellors. The type-token ratio is a
    # simple statistical coefficient that quantifies the complexity of vocabulary.

    # We implement the TTR calculation as a function.
    def calculate_ttr(text: list[str]) -> float:
        text = [speech.split(" ") for speech in text] # tokenize speeches
        text = [token for speech in text for token in speech if token.isalnum()] # remove non-alphanumeric tokens from the speeches
        return len(set(text)) / len(text) # return ttr

    # We define all chancellors
    chancellor_list = [
        "Konrad Adenauer",
        "Ludwig Erhard",
        "Kurt Georg Kiesinger",
        "Willy Brandt",
        "Helmut Schmidt",
        "Helmut Kohl",
        "Gerhard Schröder",
        "Angela Merkel"
    ]

    # We calculate the TTR for all chancellors and collect the results in a dictionary.
    chancellor_ttr = {}

    for chancellor in chancellor_list:
        chancellor_parition = corpus.get_speeches_from_politician(person=chancellor)
        chancellor_speeches = utilities.get_paragraphs_from_corpus(chancellor_parition)
        chancellor_ttr[chancellor] = calculate_ttr(chancellor_speeches)

    # Output:
    # {'Konrad Adenauer': 0.06581790181141273, 'Ludwig Erhard': 0.07735575796964228,
    # 'Kurt Georg Kiesinger': 0.07238602465784993, 'Willy Brandt': 0.05436169529177415,
    # 'Helmut Schmidt': 0.04721755524197501, 'Gerhard Schröder': 0.0548574862993217,
    # 'Angela Merkel': 0.04755084983588955}
    print(chancellor_ttr)

    # sort and visualize results
    sorted_data = dict(sorted(chancellor_ttr.items(), key=lambda item: item[1], reverse=True))
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_data.keys(), sorted_data.values(), color='skyblue')
    plt.xlabel('Chancellor')
    plt.ylabel('TTR')
    plt.title('TTR of all german chancellors')
    plt.xticks(rotation=45)
    plt.show()