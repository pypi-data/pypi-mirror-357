from extractor.core import extract_letters_list, extract_letters


def test_extract_letters_list():
    text = "Привіт! Hello, world123!!!"
    result = extract_letters_list(text)
    assert result == ["П", "р", "и", "в", "і", "т", "H", "e", "l", "l", "o", "w", "o", "r", "l", "d"]


def test_extract_letters():
    text = "Привіт! Hello, world123!!!"
    result = extract_letters(text)
    assert result == "ПривітHelloworld"
