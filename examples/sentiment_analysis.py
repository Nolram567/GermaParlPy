import germaparlpy.utilities as utilities
from germaparlpy.corpus import *
from germansentiment import SentimentModel
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s") # configure output

if __name__ == "__main__":

    # Clone the GermaParl corpus from GitHub. We specify the parent directory as target since we are one level lower.
    utilities.clone_corpus(directory="..")

    # We deserialize the corpus and specify the 19. legislative term.
    corpus = Corpus.deserialize_from_xml(lp=19, path="../GermaParlTEI")

    # We load a BERT Model trained fpr german sentiment classification "german-sentiment-bert" by Guhr et al. (2020)
    sentiment_model = SentimentModel()

    # We retrieve all speeches from the party CDU that contain the keyword "Asyl" or the keywords "Migration"
    corpus_cdu = corpus.get_speeches_from_party("CDU").get_speeches_from_word_list(["Asyl", "Migration"])

    # We retrieve all speeches from the party AfD that contain the keyword "Asyl" or the keywords "Migration"
    corpus_afd = corpus.get_speeches_from_party("AfD").get_speeches_from_word_list(["Asyl", "Migration"])

    # We extract the text from the markup for further processing
    corpus_cdu_paragraphs = utilities.get_paragraphs_from_corpus(corpus_cdu)
    corpus_afd_paragraphs = utilities.get_paragraphs_from_corpus(corpus_afd)

    # Output:
    # The corpus partition containing the speeches of the cdu comprises 7560 paragraphs.
    # The corpus partition containing the speeches of the cdu comprises 8218 paragraphs.
    print(f"The corpus partition containing the speeches of the cdu comprises {len(corpus_cdu_paragraphs)} paragraphs.")
    print(f"The corpus partition containing the speeches of the cdu comprises {len(corpus_afd_paragraphs)} paragraphs.")

    # we implement the polarity calculation as a function since the library returns a string that we need to transform.
    # We also have to break our data sets into chunks to cause no memory overflow since our partitions are quite big.

    def calculate_polarity(p: list[str]) -> float:
        model = SentimentModel()
        chunk_size = 100
        chunks = [p[i:i + chunk_size] for i in range(0, len(p), chunk_size)]
        total_polarity = 0

        for chunk in chunks:
            chunk_result = model.predict_sentiment(chunk)

            for s in chunk_result:
                if s == 'neutral':
                    continue
                elif s == 'negative':
                    total_polarity -= 1
                else:
                    total_polarity += 1

        return total_polarity / len(p)

    # We calculate the polarity for both data sets.
    corpus_cdu_polarity = calculate_polarity(corpus_cdu_paragraphs)
    corpus_afd_polarity = calculate_polarity(corpus_afd_paragraphs)

    # Output:
    # The mean polarity of speeches in the 19. legislative period of the german parliament from the party CDU
    # containing the word 'asyl' or 'migration' is -0.022389875882209784.
    # The mean polarity of speeches in the 19. legislative period of the german parliament from the party AFD
    # containing the word 'asyl' or 'migration' is -0.11084656084656085.

    print("The mean polarity of speeches in the 19. legislative period of the german parliament from the party CDU "
          f"containing the word 'asyl' or 'migration' is {corpus_cdu_polarity}.")

    print("The mean polarity of speeches in the 19. legislative period of the german parliament from the party AFD "
          f"containing the word 'asyl' or 'migration' is {corpus_afd_polarity}.")

