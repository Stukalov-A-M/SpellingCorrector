import nltk
from nltk.corpus import brown
import string
from difflib import get_close_matches

#bypass SSL certificate verification
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Download necessary data
nltk.download('brown')
nltk.download('punkt')

# Load the Brown Corpus
brown_words = brown.words()

# Preprocess the Brown Corpus: convert to lowercase and remove punctuation
def preprocess_word(word):
    word = word.lower()
    return word.translate(str.maketrans('', '', string.punctuation))

vocabulary = set(preprocess_word(word) for word in brown_words if word.isalpha())

print(f"Total words in Brown Corpus: {len(brown_words)}")
print(f"Unique words in the vocabulary: {len(vocabulary)}")

# NON-WORD ERROR CORRECTION WITH LEVENSHTEIN DISTANCE

def correct_non_word_error(word, vocabulary, n=3):
    """
    Suggest corrections for non-word errors using closest matches from the Brown Corpus.
    """
    word = preprocess_word(word)
    suggestions = get_close_matches(word, vocabulary, n=n)
    return suggestions

#TRIGRAM LANGUAGE MODEL FOR REAL-WORD ERROR DETECTION

from nltk import trigrams, bigrams
from collections import Counter, defaultdict

# Build trigram model from the Brown Corpus
def build_trigram_model(words):
    model = defaultdict(lambda: defaultdict(lambda: 0))
    
    # Generate trigrams from the words
    for w1, w2, w3 in trigrams(words, pad_left=True, pad_right=True):
        model[(w1, w2)][w3] += 1
    
    return model

# Create the trigram model from the preprocessed Brown Corpus words
trigram_model = build_trigram_model([preprocess_word(word) for word in brown_words if word.isalpha()])

# Function to suggest real-word corrections based on trigram context
def suggest_real_word_error(prev_word, curr_word, next_word, trigram_model):
    """
    Suggest corrections for real-word errors using trigram context.
    """
    if (prev_word, curr_word) in trigram_model:
        possible_words = trigram_model[(prev_word, curr_word)]
        suggestions = sorted(possible_words, key=lambda x: -possible_words[x])[:3]
        return suggestions
    return []

#SPELL CHECK SYSTEM

def spell_check_text(text, vocabulary, trigram_model):
    tokens = nltk.word_tokenize(text)
    errors = []

    # Iterate over tokens and check for errors
    for i in range(1, len(tokens) - 1):  # We need context for trigrams
        word = tokens[i]
        prev_word = preprocess_word(tokens[i - 1])
        next_word = preprocess_word(tokens[i + 1])
        
        # Check for non-word errors
        if preprocess_word(word) not in vocabulary:
            suggestions = correct_non_word_error(word, vocabulary)
            if suggestions:
                errors.append((word, suggestions))
        
        # Check for real-word errors
        else:
            real_word_suggestions = suggest_real_word_error(prev_word, word, next_word, trigram_model)
            if real_word_suggestions:
                errors.append((word, real_word_suggestions))
    
    return errors

#TKINTER GUI
import tkinter as tk
from tkinter import messagebox

class SpellCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spell Checker")
        
        # Text input widget
        self.text = tk.Text(self.root, height=15, width=80)
        self.text.pack(padx=10, pady=10)
        
        # Check Spelling button
        self.check_button = tk.Button(self.root, text="Check Spelling", command=self.check_spelling)
        self.check_button.pack(pady=5)
    
    def check_spelling(self):
        # Get input text
        input_text = self.text.get("1.0", "end-1c")
        
        # Run spell check
        errors = spell_check_text(input_text, vocabulary, trigram_model)
        
        # Highlight errors in the text
        if errors:
            for word, suggestions in errors:
                messagebox.showinfo("Spelling Error", f"Word: {word}\nSuggestions: {', '.join(suggestions)}")
        else:
            messagebox.showinfo("No Errors", "No spelling errors found!")
        
# Initialize Tkinter window
root = tk.Tk()
gui = SpellCheckerGUI(root)
root.mainloop()
