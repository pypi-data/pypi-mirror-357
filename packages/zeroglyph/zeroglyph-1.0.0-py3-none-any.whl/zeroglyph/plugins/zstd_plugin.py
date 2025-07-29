import zstandard as zstd
from typing import Optional

class ZstdCodecPlugin:
    """
    Zstandard compressor/decompressor stage with optional static dictionary support.
    """
    def __init__(self, level: int = 1, dict_path: Optional[str] = None):
        """
        :param level: Zstd compression level (1–22).
        :param dict_path: Path to a pre-trained Zstandard dictionary (.dict file).
        """
        if dict_path:
            # Load and apply pre-trained dictionary
            with open(dict_path, 'rb') as f:
                dict_data = f.read()
            zd_dict = zstd.ZstdCompressionDict(dict_data)
            self.compressor = zstd.ZstdCompressor(level=level, dict_data=zd_dict)
            self.decompressor = zstd.ZstdDecompressor(dict_data=zd_dict)
        else:
            # No dictionary
            self.compressor = zstd.ZstdCompressor(level=level)
            self.decompressor = zstd.ZstdDecompressor()

    def process(self, data: bytes) -> bytes:
        """
        Compress the input bytes using Zstandard.
        """
        return self.compressor.compress(data)

    def reverse(self, data: bytes) -> bytes:
        """
        Decompress the input bytes using Zstandard.
        """
        return self.decompressor.decompress(data)
