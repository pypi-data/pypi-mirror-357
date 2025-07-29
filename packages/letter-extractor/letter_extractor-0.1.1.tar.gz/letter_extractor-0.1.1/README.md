# Створи віртуальне оточення
python -m venv venv

source venv/bin/activate      # для Mac/Linux

.\venv\Scripts\activate       # для Windows

# .gitignore
не забудь додати віртуальне оточення до файлу .gitignore


# Встанови пакет командою
pip install letter-extractor

# Extractor

📌 Python-бібліотека обробляє 2 випадки:
1. виділення лише літер з тексту(працює з латиницею, кирилицею та іншими Unicode-символами).
Гнучкість: зібрати в рядок, порахувати частоту, згрупувати тощо.
Підходить для unit-тестів та NLP задач.
2. Працює у звʼязці з першою функцією та повертає рядок, який складається лише з літер.


## Example

```python
from extractor import extract_letters_list

text = "Привіт! Hello, world123!!!"
print(extract_letters_list(text))
# ["П", "р", "и", "в", "і", "т", "H", "e", "l", "l", "o", "w", "o", "r", "l", "d"]


from extractor import extract_letters
text = "Привіт! Hello, world123!!!"
return "".join(extract_letters_list(text))
"ПривітHelloworld"


