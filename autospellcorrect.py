import re
import phonetics
from rapidfuzz import fuzz
import csv  

def normalize_word(word: str) -> str:
    """Lowercase, remove extra vowels, strip spaces."""
    word = word.lower().strip()
    word = re.sub(r'(a|e|i|o|u)\1+', r'\1', word)
    return word

def load_reference_dict(filepath: str) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        words = [normalize_word(line.strip()) for line in f.readlines()]
    return list(set(words))

def match_casing(original: str, corrected: str) -> str:
    if original.isupper():
        return corrected.upper()
    elif original.istitle():
        return corrected.capitalize()
    else:
        return corrected

def get_best_match(word: str, dictionary: list) -> str:
    """Find the best correction using phonetic + fuzzy similarity."""
    if word in dictionary:
        return word

    word_code = phonetics.soundex(word)
    candidates = []

    for ref in dictionary:
        ref_code = phonetics.soundex(ref)
        score = 0
        if ref_code == word_code:
            score += 30
        score += fuzz.ratio(word, ref)
        candidates.append((ref, score))
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0] if candidates else word

if __name__ == "__main__":
    reference_file = "reference.txt"  
    errors_file = "errors.txt"        
    output_file = "corrected_output.txt"

    dictionary = load_reference_dict(reference_file)

    with open(errors_file, "r", encoding="utf-8") as f:
        errors = [line.strip() for line in f.readlines()]

    corrected_list = []
    for word in errors:
        normalized_word = normalize_word(word)
        best_match = get_best_match(normalized_word, dictionary)
        best_match = match_casing(word, best_match)
        corrected_list.append((word, best_match))

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t") 
        writer.writerow(["File_Error", "Corrected"])  
        writer.writerows(corrected_list)

    print(f" Correction complete. Output saved to {output_file}")

