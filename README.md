# pii-redact-poc

Proof of concept: masking personal data in Russian / Uzbek business correspondence
**locally**, before text leaves the trusted perimeter (e.g. is sent to an external
AI service or a messenger).

No LLM and no network calls: a small NER model (Natasha / Slovnet, runs on CPU)
plus regular expressions.

```
Заявитель Каримова Нилуфар Бахтияровна обратилась по вопросу перерасчёта.
Контактный телефон: +998 90 000 00 00.
Паспорт серии AA0000000, ПИНФЛ 30000000000000.
```
↓
```
Заявитель [ФИО] обратилась по вопросу перерасчёта.
Контактный телефон: [ТЕЛЕФОН].
Паспорт серии [ПАСПОРТ], ПИНФЛ [ПИНФЛ].
```

All names and numbers in this repository are synthetic.

## What it masks

| Data | Method | Placeholder |
|------|--------|-------------|
| Person names (Russian, Uzbek Cyrillic) | NER, Natasha / Slovnet | `[ФИО]` |
| Phone numbers `+998 …` | regex | `[ТЕЛЕФОН]` |
| Passport `AA1234567` | regex | `[ПАСПОРТ]` |
| PINFL (14 digits) | regex | `[ПИНФЛ]` |
| INN / TIN (9 digits) | regex | `[ИНН]` |
| Card / account numbers (16–20 digits) | regex | `[СЧЁТ/КАРТА]` |

Natasha is trained on Russian news and misses names containing Uzbek-specific
Cyrillic letters (`ғ қ ҳ ў`). Before NER these letters are replaced one-to-one
with their closest Russian counterparts; offsets do not change, so the found
spans are applied to the original text. Example: `Ўринбоева Ҳилола Ғайратовна`
is not detected without normalization and is fully masked with it.

## Known limitations

- **Latin-script names are not detected** (`Karimova Nilufar`). This is pinned by
  an `xfail` test. Our experiments with stop-lists and open Uzbek NER models gave
  roughly 60–80% recall on small samples — not production-grade yet.
- The INN pattern masks any standalone 9-digit number, so false positives are possible.
- This is a PoC: no evaluation on a large labeled corpus has been done.

## Usage

Tested on Python 3.10 and 3.11.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pii_redact examples/sample_letter.txt
echo "Телефон: +998 90 000 00 00" | python -m pii_redact
```

```python
from pii_redact import redact_text

redact_text("Исполнитель Ғуломов Шерзод, тел. +998 90 000 00 00")
# 'Исполнитель [ФИО], тел. [ТЕЛЕФОН]'
```

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Кратко по-русски

PoC локального маскирования персональных данных (ФИО, телефон, паспорт, ПИНФЛ,
ИНН, карта/счёт) в русских и узбекских текстах перед передачей во внешние
AI-сервисы. Работает без LLM и без сети. Узбекская кириллица поддерживается
через нормализацию букв, ФИО на латинице пока не распознаются.

## License

[MIT](LICENSE)
