from typing import Union, Dict, Any
import yaml

from .pipeline import PipelineManager
from .framer import Framer


class CompressorClient:
    """
    CompressorClient: High-level interface for compressing and decompressing text.
    It wraps the framing, pipeline, and codec plugins behind a simple API.
    """

    def __init__(self, config: Union[str, Dict[str, Any]]):
        """
        :param config: Path to a YAML config file or a dict with keys:
            - zstd_level: int
            - huffman: bool
            - dict_path: Optional[str]
        """
        if isinstance(config, str):
            with open(config, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
        else:
            cfg = config

        self.pipeline = PipelineManager(cfg)
        self.framer = Framer()

    def compress(self, text: str) -> bytes:
        """
        Compress a UTF-8 string into a ZeroGlyph packet.
        """
        payload = text.encode("utf-8")
        processed = self.pipeline.compress(payload)
        return self.framer.pack(processed)

    def decompress(self, packet: bytes) -> str:
        """
        Decompress a ZeroGlyph packet back into a UTF-8 string.
        """
        processed = self.framer.unpack(packet)
        raw = self.pipeline.decompress(processed)
        return raw.decode("utf-8")
