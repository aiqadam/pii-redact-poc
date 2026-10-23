"""
PII redaction for Russian / Uzbek business correspondence.

Two independent layers, no LLM involved:
  1. NER (Natasha / Slovnet) masks person names (PER entities).
     Uzbek-specific Cyrillic letters are normalized before NER, because
     the model is trained on Russian news and stumbles on them.
  2. Regex masks structured identifiers: phones (+998), passports,
     PINFL, INN (TIN), card / account numbers.
"""
from __future__ import annotations

import re

_segmenter = None
_morph_tagger = None
_ner_tagger = None


def _load_natasha() -> None:
    global _segmenter, _morph_tagger, _ner_tagger
    if _ner_tagger is not None:
        return
    from natasha import NewsEmbedding, NewsMorphTagger, NewsNERTagger, Segmenter

    emb = NewsEmbedding()
    _segmenter = Segmenter()
    _morph_tagger = NewsMorphTagger(emb)
    _ner_tagger = NewsNERTagger(emb)


# ── Layer 1: names (NER) ──────────────────────────────────────────────────────

# One-to-one letter replacements: string length and offsets stay the same,
# so spans found in the normalized text apply to the original text as is.
_UZ_CYRL_TO_RU = str.maketrans("ғқҳўҒҚҲЎ", "гкхуГКХУ")


def _normalize_uz_cyrillic(text: str) -> str:
    return text.translate(_UZ_CYRL_TO_RU)


def find_names(text: str) -> list[tuple[int, int]]:
    """Returns (start, stop) spans of person names found by NER."""
    from natasha import Doc

    _load_natasha()
    doc = Doc(_normalize_uz_cyrillic(text))
    doc.segment(_segmenter)
    doc.tag_morph(_morph_tagger)
    doc.tag_ner(_ner_tagger)
    return [(s.start, s.stop) for s in doc.spans if s.type == "PER"]


def _mask_names(text: str) -> str:
    # Replace right to left so earlier spans keep their offsets.
    for start, stop in sorted(find_names(text), reverse=True):
        text = text[:start] + "[ФИО]" + text[stop:]
    return text


# ── Layer 2: structured identifiers (regex) ───────────────────────────────────

_PATTERNS = [
    # Order matters: longer digit sequences first.
    ("[СЧЁТ/КАРТА]", re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4,8}\b")),
    ("[ТЕЛЕФОН]", re.compile(r"\+?998[\s\-]?\(?\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b")),
    ("[ПАСПОРТ]", re.compile(r"\b[A-ZА-Я]{2}\s?\d{7}\b")),
    ("[ПИНФЛ]", re.compile(r"\b\d{14}\b")),
    ("[ИНН]", re.compile(r"\b\d{9}\b")),
]


def _mask_regex(text: str) -> str:
    for label, pattern in _PATTERNS:
        text = pattern.sub(label, text)
    return text


def redact_text(text: str) -> str:
    """Masks person names (NER) and structured identifiers (regex)."""
    if not text or not text.strip():
        return text
    return _mask_regex(_mask_names(text))
