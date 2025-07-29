from pyvinorm.utils.string_utils import (
    replace_nonvoice_symbols,
    contain_only_letters,
    read_letter_by_letter,
    remove_white_space,
)


def assert_replace_nonvoice_symbols(text: str, expected: str, repl: str = ""):
    result = replace_nonvoice_symbols(text, repl=repl)
    assert result == expected, f"Expected: {expected}, but got: {result}"


def test_replace_nonvoice_symbols():
    assert_replace_nonvoice_symbols(
        'Cơn ""mưa" " {ngang} qua (cơn mưa ngang qua)',
        "Cơn mưa  ngang qua cơn mưa ngang qua",
    )

    assert_replace_nonvoice_symbols(
        "Hôm nay là ngày đẹp trời! (Chúc bạn vui vẻ!)",
        "Hôm nay là ngày đẹp trời! ,Chúc bạn vui vẻ!,",
        repl=",",
    )

    assert_replace_nonvoice_symbols(
        "Em hãy là em của ngày hôm qua...(Ú u u ù)",
        "Em hãy là em của ngày hôm qua<><>Ú u u ù<>",
        repl="<>",
    )


def assert_remove_white_space(text: str, expected: str):
    result = remove_white_space(text)
    assert result == expected, f"Expected: {expected}, but got: {result}"


def test_remove_white_space():
    assert_remove_white_space("  Hello   World!  ", "Hello World!")
    assert_remove_white_space("  Multiple   spaces   here.  ", "Multiple spaces here.")
    assert_remove_white_space("NoSpacesHere", "NoSpacesHere")
    assert_remove_white_space(
        "  Leading and trailing spaces.  ", "Leading and trailing spaces."
    )
    assert_remove_white_space("   ", "")
    assert_remove_white_space("", "")
    assert_remove_white_space("  \n  \t  ", "")
