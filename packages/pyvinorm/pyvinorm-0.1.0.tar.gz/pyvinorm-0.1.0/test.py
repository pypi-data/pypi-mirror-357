import regex

if __name__ == "__main__":
    pattern = regex.compile(r"(?i)(từ|tháng) [01]?\d[.\/][12]\d{3}\s?(-|đến)\s?[01]?\d[.\/][12]\d{3}")
    text = "từ 02/ 2023 - 11/2024"

    print("Match:", [p.group() for p in pattern.finditer(text)])