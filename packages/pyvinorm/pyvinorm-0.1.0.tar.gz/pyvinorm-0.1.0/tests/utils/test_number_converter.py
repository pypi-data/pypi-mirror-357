import pytest
from pyvinorm.utils.number_converter import NumberConverter


def test_convert_int_number():
    assert NumberConverter._convert_arbitrary_number("000") == ""

    assert NumberConverter.convert_number("0") == "không"
    assert NumberConverter.convert_number("05") == "năm"
    assert NumberConverter.convert_number("10") == "mười"
    assert NumberConverter.convert_number("21") == "hai mươi mốt"
    assert NumberConverter.convert_number("99") == "chín mươi chín"
    assert NumberConverter.convert_number("100") == "một trăm"
    assert NumberConverter.convert_number("105") == "một trăm linh lăm"
    assert NumberConverter.convert_number("124") == "một trăm hai mươi tư"
    assert NumberConverter.convert_number("999") == "chín trăm chín mươi chín"
    assert NumberConverter.convert_number("1000") == "một nghìn"
    assert NumberConverter.convert_number("1001") == "một nghìn không trăm linh một"
    assert NumberConverter.convert_number("1234") == "một nghìn hai trăm ba mươi tư"
    assert NumberConverter.convert_number("10000") == "mười nghìn"
    assert NumberConverter.convert_number("100009") == "một trăm nghìn không trăm linh chín"
    assert NumberConverter.convert_number("2000004") == "hai triệu không nghìn không trăm linh bốn"
    assert NumberConverter.convert_number("10000000") == "mười triệu"
    assert NumberConverter.convert_number("100000000") == "một trăm triệu"
    assert NumberConverter.convert_number("1000000000") == "một tỷ"
    assert NumberConverter.convert_number("10000000000") == "mười tỷ"
    assert NumberConverter.convert_number("100000000000") == "một trăm tỷ"
    assert NumberConverter.convert_number("1000000000000") == "một nghìn tỷ"
    assert NumberConverter.convert_number("10000000000000000000") == "một" + " không" * 19

def test_convert_number_with_sign():
    assert NumberConverter.convert_number("0") == "không"
    assert NumberConverter.convert_number("+0") == "dương không"
    assert NumberConverter.convert_number("-0") == "âm không"
    assert NumberConverter.convert_number("-5") == "âm năm"
    assert NumberConverter.convert_number("-10") == "âm mười"
    assert NumberConverter.convert_number("-21") == "âm hai mươi mốt"
    assert NumberConverter.convert_number("+99") == "dương chín mươi chín"
    assert NumberConverter.convert_number("-100") == "âm một trăm"
    assert NumberConverter.convert_number("-105") == "âm một trăm linh lăm"
    assert NumberConverter.convert_number("-124") == "âm một trăm hai mươi tư"
    assert NumberConverter.convert_number("-999") == "âm chín trăm chín mươi chín"
    assert NumberConverter.convert_number("-1000") == "âm một nghìn"
    assert NumberConverter.convert_number("-1001") == "âm một nghìn không trăm linh một"
    assert NumberConverter.convert_number("-1234") == "âm một nghìn hai trăm ba mươi tư"

def test_convert_invalid_number():
    with pytest.raises(ValueError):
        NumberConverter.convert_number("abc")
    with pytest.raises(ValueError):
        NumberConverter.convert_number("123a")
    with pytest.raises(ValueError):
        NumberConverter.convert_number("1.23")
    with pytest.raises(ValueError):
        NumberConverter.convert_number("1,000")
    with pytest.raises(ValueError):
        NumberConverter.convert_number("00") == "không"

def test_convert_roman_to_decimal():
    assert NumberConverter.roman_to_decimal("IV") == 4
    assert NumberConverter.roman_to_decimal("XII") == 12
    assert NumberConverter.roman_to_decimal("XXI") == 21
    assert NumberConverter.roman_to_decimal("XLII") == 42
    assert NumberConverter.roman_to_decimal("XCIX") == 99
    assert NumberConverter.roman_to_decimal("C") == 100
    assert NumberConverter.roman_to_decimal("CD") == 400
    assert NumberConverter.roman_to_decimal("CM") == 900
    assert NumberConverter.roman_to_decimal("M") == 1000
    assert NumberConverter.roman_to_decimal("MMXXIII") == 2023
    assert NumberConverter.roman_to_decimal("MMMCMXCIX") == 3999

def test_convert_decimal_to_roman():
    assert NumberConverter.decimal_to_roman(4) == "IV"
    assert NumberConverter.decimal_to_roman(12) == "XII"
    assert NumberConverter.decimal_to_roman(21) == "XXI"
    assert NumberConverter.decimal_to_roman(42) == "XLII"
    assert NumberConverter.decimal_to_roman(99) == "XCIX"
    assert NumberConverter.decimal_to_roman(100) == "C"
    assert NumberConverter.decimal_to_roman(400) == "CD"
    assert NumberConverter.decimal_to_roman(900) == "CM"
    assert NumberConverter.decimal_to_roman(1000) == "M"
    assert NumberConverter.decimal_to_roman(2023) == "MMXXIII"
    assert NumberConverter.decimal_to_roman(3999) == "MMMCMXCIX"

def test_convert_roman_invalid():
    with pytest.raises(ValueError):
        NumberConverter.roman_to_decimal("IIII")
    with pytest.raises(ValueError):
        NumberConverter.roman_to_decimal("VV")
    with pytest.raises(ValueError):
        NumberConverter.roman_to_decimal("XXXX")
    with pytest.raises(ValueError):
        NumberConverter.roman_to_decimal("LL")
    with pytest.raises(ValueError):
        NumberConverter.roman_to_decimal("DD")