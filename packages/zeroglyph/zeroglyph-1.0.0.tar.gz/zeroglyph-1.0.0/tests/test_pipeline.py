import pytest
from zeroglyph.pipeline import PipelineManager, Plugin

class DummyPlugin:
    def __init__(self, suffix: bytes):
        self.suffix = suffix
    def process(self, data: bytes) -> bytes:
        return data + self.suffix
    def reverse(self, data: bytes) -> bytes:
        assert data.endswith(self.suffix)
        return data[:-len(self.suffix)]

@pytest.fixture
def pipeline():
    # Two dummy plugins that append b'A' then b'B'
    plugins = {
        'a': DummyPlugin(b'A'),
        'b': DummyPlugin(b'B'),
    }
    return PipelineManager(plugins)

def test_pipeline_compress_decompress(pipeline):
    raw = b"data"
    compressed = pipeline.compress(raw)
    assert compressed == b"dataAB"
    recovered = pipeline.decompress(compressed)
    assert recovered == raw
