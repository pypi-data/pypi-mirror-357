import re
from typing import List


def extract_letters_list(text: str) -> List[str]:
    """
    Виділяє всі літери (без цифр, розділових знаків, символів).

    Підтримує Unicode, тож працює з будь-якими мовами.

    Повертає список усіх літер з тексту.

    """
    return re.findall(r"[^\W\d_]", text, re.UNICODE)


def extract_letters(text: str) -> str:
    """
    Повертає рядок, який складається лише з літер.
    """
    return "".join(extract_letters_list(text))
