from typing import Optional
import zstandard as zstd


class ZstdCodecPlugin:
    """
    Zstd compression plugin with optional static dictionary support.
    """

    def __init__(self, level: int = 3, dict_path: Optional[str] = None):
        self.level = level
        self.dict = None
        if dict_path:
            with open(dict_path, "rb") as f:
                self.dict = zstd.ZstdCompressionDict(f.read())
        self.compressor = zstd.ZstdCompressor(level=level, dict_data=self.dict)
        self.decompressor = zstd.ZstdDecompressor(dict_data=self.dict)

    def process(self, data: bytes) -> bytes:
        return self.compressor.compress(data)

    def reverse(self, data: bytes) -> bytes:
        return self.decompressor.decompress(data)
