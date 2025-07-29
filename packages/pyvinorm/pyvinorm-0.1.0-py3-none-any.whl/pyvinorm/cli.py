import importlib.resources as pkg_resources
from argparse import ArgumentParser
import logging

from pyvinorm.vinorm import ViNormalizer

logging.basicConfig(filename="siu.log", level=logging.FATAL)
logger = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description="Normalize Vietnamese text.")
    parser.add_argument(
        "text",
        type=str,
        help="Text to normalize.",
    )
    parser.add_argument(
        "--regex-only",
        action="store_true",
        help="Return only regex matches without normalization.",
    )
    parser.add_argument(
        "--keep-oov",
        action="store_true",
        help="Keep out-of-vocabulary words in the output.",
    )
    parser.add_argument(
        "--keep-punct",
        action="store_true",
        help="Keep punctuation in the output.",
    )

    args = parser.parse_args()

    # Do normalization ^_^
    normalizer = ViNormalizer(
        regex_only=args.regex_only,
        keep_oov=args.keep_oov,
        keep_punctuation=args.keep_punct,
    )
    text = args.text.strip()
    normalized_text = normalizer.normalize(text)
    print(normalized_text + "|")


# def main() -> None:
#     init_resources()

#     test_cases = [
#         "ngày 18/06/2025 xảy ra vụ án tại số nhà ECF-001",
#         " đơn vị ka.10/3 đường 108 , số nhà 46C tx. Bỉm Sơn",
#         "Khu vực này sẽ bị phong tỏa từ 18-30.6 hoặc từ 10/6 - 20/7",
#         "tháng 12/2024 là tháng cuối cùng của năm",
#         "đêm mùng    4/6",
#         "hoangvu1808@gmail.com | 123@vnpay.com.vn",
#         "https://example.com.net",
#         "sftp://192.0.2.1:22/file.txt",
#         "u12, U23, u.22",
#         "đội hình 3-4-3/",
#         "đội hình 4-2-3-1/",
#         "-1.234,06789", "-1,234.56",
#         "-1,2", "-98.6",
#         "đại hội Đảng lần thứ XIII đã diễn ra vào ngày 25/1/2021",
#         "thế kỷ    XXI đánh dấu nhiều bước tiến quan trọng trong công nghệ",
#         "40°C 40.1cm , 40.1cm2 1.234,56km3",
#         "giá vàng hôm nay là 1.234.567,89vnd, 2.000,4$",
#     ]

#     p = PatternHandler()
#     for text in test_cases:
#         normalized_text = p.normalize(text)
#         print(f"Original: {text}")
#         print(f"Normalized: {normalized_text}\n")


if __name__ == "__main__":
    main()
