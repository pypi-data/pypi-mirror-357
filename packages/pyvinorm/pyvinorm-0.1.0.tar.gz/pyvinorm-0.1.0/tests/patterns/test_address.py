from pyvinorm import ViNormalizer


def test_address_patterns():
    normalizer = ViNormalizer(keep_punctuation=True, downcase=False)

    # Test case 1: Basic address with street and house number
    text = "Số nhà 123, đường Nguyễn Văn Cừ, quận 1"
    expected = "Số nhà một trăm hai mươi ba , đường Nguyễn Văn Cừ , quận một"
    assert normalizer.normalize(text) == expected

    # Test case 2: Address with complex street name and district
    text = "Đường Trần Hưng Đạo, phường Bến Thành, quận 1"
    expected = "Đường Trần Hưng Đạo , phường Bến Thành , quận một"
    assert normalizer.normalize(text) == expected

    # Test case 3: Address with multiple components
    text = "Số nhà 456, khu phố 5, thị trấn Thạnh Mỹ Lợi, huyện Nhà Bè"
    expected = "Số nhà bốn trăm năm mươi sáu , khu phố năm , thị trấn Thạnh Mỹ Lợi , huyện Nhà Bè"
    assert normalizer.normalize(text) == expected

    # Test case 4: Address with postal code
    text = "Số nhà 789, đường Lê Lợi, tp. Hồ Chí Minh, mã bưu chính 700000"
    expected = "Số nhà bảy trăm tám mươi chín , đường Lê Lợi , thành phố Hồ Chí Minh , mã bưu chính bảy không không không không không"
    assert normalizer.normalize(text) == expected

    # Test case 5: Address with special characters
    text = "Số nhà 101-102A, đường Nguyễn Thị Minh Khai (gần chợ Bến Thành)"
    expected = "Số nhà một trăm linh một - một trăm linh hai A , đường Nguyễn Thị Minh Khai gần chợ Bến Thành"
    assert normalizer.normalize(text) == expected


    # Test case 6: Address with abbreviations
    text = "số 202, Dịch Vọng, q.Cầu Giấy, tp.Hà Nội"
    expected = "số hai trăm linh hai , Dịch Vọng , quận Cầu Giấy , thành phố Hà Nội"
    assert normalizer.normalize(text) == expected

    # Test case 7: Office address format
    text = "phòng 301, tòa nhà Vincom Center, 171 Đường Đồng Khởi, quận 1"
    expected = "phòng ba trăm linh một , tòa nhà Vincom Center , một trăm bảy mươi mốt Đường Đồng Khởi , quận một"
    assert normalizer.normalize(text) == expected

    text = "lớp 6A1, trường THCS Nguyễn Du, 123 Đường Lê Lai, phường Bến Nghé, quận 1"
    expected = "lớp sáu A một , trường trung học cơ sở Nguyễn Du , một trăm hai mươi ba Đường Lê Lai , phường Bến Nghé , quận một"
    assert normalizer.normalize(text) == expected
