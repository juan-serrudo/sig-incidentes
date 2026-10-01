"""Small text helpers for validation, duplicate checks and the keyword baseline."""

import re
import unicodedata


def normalize_text(text):
    characters = unicodedata.normalize("NFKD", text.lower())
    plain = "".join(character for character in characters if not unicodedata.combining(character))
    return " ".join(re.findall(r"[a-z0-9]+", plain))

