from typing import Dict, List

import spacy
import enchant
import gensim.downloader as api

nlp = spacy.load("en_core_web_sm")
dictionary = enchant.Dict("en_US")
model = api.load("word2vec-google-news-300")

ErrorInfo = Dict[str, List[str]]


# Spell-check processor


def get_word_vector(word: str):
    """
    Get a vector representations for the word.
    If word doesn't exist in the model return None.
    """
    try:
        return model[word]
    except KeyError:
        return None


def spell_check(text: str) -> List[ErrorInfo]:
    tokens = nlp(text)

    errors: List[ErrorInfo] = []

    for token in tokens:
        # Checking words only
        if not token.is_punct:
            word = token.text

            # Checking spelling
            if not dictionary.check(word):
                # Get the vector representation of the word
                word_vector = get_word_vector(word)

                # Checking the context if the word exists in the word2vec
                if word_vector is not None:
                    # Compute cosines similarity with the average context vector
                    context_vectors = [get_word_vector(tok.text) for tok in tokens if get_word_vector(tok.text) is not None]

                    if context_vectors:
                        context_mean = sum(context_vectors) / len(context_vectors)
                        similarity = model.cosine_similarities(word_vector, [context_mean])[0]

                        # If the similarity is low, add an error
                        if similarity < 0.7:
                            suggestions = dictionary.suggest(word)
                            error_info = {
                                'word': word,
                                'suggestions': suggestions[:5]
                            }
                            errors.append(error_info)
                else:
                    # If the word wasn't found in the word2vec, add an error
                    suggestions = dictionary.suggest(word)
                    error_info = {
                        'word': word,
                        'suggestions': suggestions[:5]
                    }
                    errors.append(error_info)

    return errors


# For debug purposes only
def display_errors(text):
    for error in spell_check(text):
        print(f"Incorrect word: {error['word']}")
        print(f"Suggestions: {error['suggestions']}")
        print('-' * 40)
