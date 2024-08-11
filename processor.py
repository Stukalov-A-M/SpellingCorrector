from typing import Dict, List

import spacy
import enchant

nlp = spacy.load("en_core_web_sm")
dictionary = enchant.Dict("en_US")

# Spell-check processor
ErrorInfo = Dict[str, List[str]]


def spell_check(text):
    tokens = nlp(text)

    errors: List[ErrorInfo] = []

    for token in tokens:
        # Checking only word-tokens
        if not token.is_punct and not dictionary.check(token.text):
            # Suggest the right spelling not more than 5
            suggestions = dictionary.suggest(token.text)
            error_info = {
                'word': token.text,
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

