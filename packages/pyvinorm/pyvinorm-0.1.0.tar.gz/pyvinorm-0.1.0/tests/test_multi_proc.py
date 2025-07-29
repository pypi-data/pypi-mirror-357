import multiprocessing

# https://github.com/pytest-dev/pytest/issues/11174
multiprocessing.set_start_method("spawn", force=True)

from pyvinorm import ViNormalizer


def normalize_text(text, queue):
    normalizer = ViNormalizer(keep_punctuation=True, downcase=False)
    # print(f"Normalizing text: {text}")
    result = normalizer.normalize(text)
    # print(f"Normalized result: {result}")
    queue.put(result)


def test_multiprocess_vinormalizer():
    texts = [
        "18/08/2004 là ngày sinh của tôi.",
        "dự báo thời tiết hôm nay là 18°C.",
        "Cộng hòa Xã hội Chủ nghĩa Việt Nam.",
    ] * 10
    expected = [
        "mười tám tháng tám năm hai nghìn không trăm linh bốn là ngày sinh của tôi .",
        "dự báo thời tiết hôm nay là mười tám độ xê .",
        "Cộng hòa Xã hội Chủ nghĩa Việt Nam .",
    ] * 10
    queue = multiprocessing.Queue()
    processes = []
    for text in texts:
        p = multiprocessing.Process(target=normalize_text, args=(text, queue))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    results = [queue.get() for _ in texts]
    results = sorted(set(results))
    expected = sorted(set(expected))

    print("Expected:", *expected, sep="\n")
    print("Results:", *results, sep="\n")

    assert all(
        result == expected_result for result, expected_result in zip(results, expected)
    ), f"Expected {expected}, but got {results}"
