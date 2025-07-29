import pytest
from zeroglyph.plugins.huffman_plugin import HuffmanPlugin


@pytest.fixture
def sample_data(tmp_path):
    # create a repetitive corpus file
    corpus = (b"spam eggs " * 100) + (b"foo bar " * 50)
    file = tmp_path / "corpus.txt"
    file.write_bytes(corpus)
    return corpus, str(file)


def test_huffman_roundtrip(sample_data, tmp_path):
    corpus, corpus_path = sample_data
    table_path = tmp_path / "codebook.huff"
    plugin = HuffmanPlugin(
        enabled=True, table_path=str(table_path), sample_corpus=corpus_path
    )
    # First encode/decode
    encoded = plugin.process(corpus)
    assert encoded != corpus  # some compression
    decoded = plugin.reverse(encoded)
    assert decoded == corpus
    # Reload from persisted table
    plugin2 = HuffmanPlugin(enabled=True, table_path=str(table_path))
    re_encoded = plugin2.process(corpus)
    re_decoded = plugin2.reverse(re_encoded)
    assert re_decoded == corpus


def test_huffman_noop_when_disabled():
    plugin = HuffmanPlugin(enabled=False)
    data = b"any data here"
    assert plugin.process(data) == data
    assert plugin.reverse(data) == data
