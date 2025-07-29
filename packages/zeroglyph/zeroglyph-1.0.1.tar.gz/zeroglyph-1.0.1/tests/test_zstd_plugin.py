import pytest
from zeroglyph.plugins.zstd_plugin import ZstdCodecPlugin


@pytest.mark.parametrize("level", [1, 3, 10])
def test_zstd_roundtrip(tmp_path, level):
    plugin = ZstdCodecPlugin(level=level)
    data = b"The quick brown fox jumps over the lazy dog" * 20
    compressed = plugin.process(data)
    assert compressed != data  # some compression occurs
    recovered = plugin.reverse(compressed)
    assert recovered == data


def test_zstd_with_dictionary(tmp_path):
    # Create a small sample dict file
    sample = b"a" * 100 + b"b" * 100
    dict_path = tmp_path / "sample.dict"
    dict_path.write_bytes(sample)
    plugin = ZstdCodecPlugin(level=1, dict_path=str(dict_path))
    data = sample + b"c" * 50
    compressed = plugin.process(data)
    recovered = plugin.reverse(compressed)
    assert recovered == data
