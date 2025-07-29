from typing import List
from pyvinorm import ViNormalizer


def assert_normalizing(texts: List[str], expected: List[str]):
    normalizer = ViNormalizer(downcase=False, keep_punctuation=True, regex_only=True)

    for text, exp in zip(texts, expected):
        assert normalizer.normalize(text) == exp


def test_time_patterns():
    assert_normalizing(
        [
            "bây giờ là 10 h30am",
            "bây giờ là 19h tèo teo téo teo tèo teo tèo",
            "23h",
            "24g",
            "09:30",
            "9h2m2s",
            "9:45",
            "21g26p",
            "01:20:30",
            "23h24m45s",
            "9h - 10h",
            "9h20p- 10h30",
            "9h2p - 9h5p",
        ],
        [
            "bây giờ là mười giờ ba mươi ây em",
            "bây giờ là mười chín giờ tèo teo téo teo tèo teo tèo",
            "hai mươi ba giờ",
            "hai mươi tư giờ",
            "chín giờ ba mươi",
            "chín giờ hai phút hai giây",
            "chín giờ bốn mươi lăm",
            "hai mươi mốt giờ hai mươi sáu phút",
            "một giờ hai mươi phút ba mươi giây",
            "hai mươi ba giờ hai mươi tư phút bốn mươi lăm giây",
            "chín giờ đến mười giờ",
            "chín giờ hai mươi phút đến mười giờ ba mươi",
            "chín giờ hai phút đến chín giờ năm phút",
        ],
    )


def test_date_patterns():
    assert_normalizing(
        ["ngày 10/3", "02/9 /1945", "5-09-1890", "20.6.2025", "24 - 7 - 2002"],
        [
            "ngày mười tháng ba",
            "hai tháng chín năm một nghìn chín trăm bốn mươi lăm",
            "năm tháng chín năm một nghìn tám trăm chín mươi",
            "hai mươi tháng sáu năm hai nghìn không trăm hai mươi lăm",
            "hai mươi tư tháng bảy năm hai nghìn không trăm linh hai",
        ],
    )


def test_date_from_to_patterns():
    assert_normalizing(
        [
            "từ 20 -   30/4",
            "ngày 4.5-5.6",
            "từ 20/4 - 30.6",
            "từ 01 -12/2025",
            "từ 02/ 2023 - 11 .2024",
        ],
        [
            "từ hai mươi đến ba mươi tháng tư",
            "ngày bốn tháng năm đến năm tháng sáu",
            "từ hai mươi tháng tư đến ba mươi tháng sáu",
            "từ tháng một đến tháng mười hai năm hai nghìn không trăm hai mươi lăm",
            "từ tháng hai năm hai nghìn không trăm hai mươi ba đến tháng mười một năm hai nghìn không trăm hai mươi tư",
        ],
    )


def test_month_patterns():
    assert_normalizing(
        [
            "tháng 01. 2025",
            "tháng   10 / 1998",
            "tháng 10  /1998",
        ],
        [
            "tháng một năm hai nghìn không trăm hai mươi lăm",
            "tháng mười năm một nghìn chín trăm chín mươi tám",
            "tháng mười năm một nghìn chín trăm chín mươi tám",
        ],
    )


def test_datetime_patterns():
    assert_normalizing(
        ["sáng mùng 8/ 3", "đêm 29-12", "rạng sáng 30/04"],
        [
            "sáng mùng tám tháng ba",
            "đêm hai mươi chín tháng mười hai",
            "rạng sáng ba mươi tháng tư",
        ],
    )
