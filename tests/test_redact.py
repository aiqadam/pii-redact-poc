"""All names and numbers below are synthetic."""
import pytest

from pii_redact import redact_text


def test_masks_russian_name():
    result = redact_text("Заявитель Петрова Анна Сергеевна сообщила о проблеме.")
    assert "Петрова" not in result
    assert "[ФИО]" in result


def test_masks_uzbek_cyrillic_name_with_specific_letters():
    result = redact_text("Исполнитель Ғуломов Шерзод подготовил ответ.")
    assert "Ғуломов" not in result
    assert "[ФИО]" in result


def test_normalization_keeps_original_text_outside_names():
    result = redact_text("Масъул: Қодиров Азиз. Ҳужжат қабул қилинди.")
    assert "Ҳужжат қабул қилинди." in result


def test_masks_phone():
    result = redact_text("Контактный телефон: +998 90 000 00 00.")
    assert "000 00 00" not in result
    assert "[ТЕЛЕФОН]" in result


def test_masks_passport():
    result = redact_text("Паспорт серии AA0000000 выдан 01.01.2020.")
    assert "AA0000000" not in result
    assert "[ПАСПОРТ]" in result


def test_masks_pinfl():
    result = redact_text("ПИНФЛ 30000000000000 указан в заявлении.")
    assert "30000000000000" not in result
    assert "[ПИНФЛ]" in result


def test_masks_inn():
    result = redact_text("ИНН организации: 300000000.")
    assert "300000000" not in result
    assert "[ИНН]" in result


def test_masks_card_account():
    result = redact_text("Средства зачислены на карту 8600 0000 0000 0000.")
    assert "8600 0000 0000 0000" not in result
    assert "[СЧЁТ/КАРТА]" in result


def test_empty_text():
    assert redact_text("") == ""
    assert redact_text("   ") == "   "


def test_masks_name_that_raw_ner_misses_without_normalization():
    result = redact_text("Ариза берувчи Ўринбоева Ҳилола Ғайратовна.")
    assert "Ўринбоева" not in result
    assert "[ФИО]" in result


@pytest.mark.xfail(reason="Known limitation: Natasha does not recognize Latin-script names", strict=True)
def test_latin_uzbek_name_known_limitation():
    result = redact_text("Murojaatchi Karimova Nilufar Baxtiyorovna ariza berdi.")
    assert "Karimova" not in result
