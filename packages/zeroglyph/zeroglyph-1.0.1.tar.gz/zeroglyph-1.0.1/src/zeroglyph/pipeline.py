# src/zeroglyph/pipeline.py

from typing import Dict, Any


class PipelineManager:
    """
    Manages a sequence of compression plugins.
    """

    def __init__(self, cfg: Dict[str, Any]):
        """
        Two modes:
        1) Plugin-map mode: if cfg’s values are plugin instances (with process & reverse),
           we just use them in the given order.
        2) Config-dict mode: build Zstd and optional Huffman stages based on config keys:
            - zstd_level: int
            - huffman: bool
            - dict_path: Optional[str]
            - huffman_table: Optional[str]
            - sample_corpus: Optional[str]
        """
        # Detect plugin-map mode by checking if all values look like plugins
        if isinstance(cfg, dict) and cfg:
            values = list(cfg.values())
            if all(hasattr(p, "process") and hasattr(p, "reverse") for p in values):
                self.plugins = values
                return

        # Otherwise, treat cfg as configuration dict
        from .plugins.zstd_plugin import ZstdCodecPlugin
        from .plugins.huffman_plugin import HuffmanPlugin

        self.plugins = []

        # Zstd stage
        zstd_level = cfg.get("zstd_level", 3)
        dict_path = cfg.get("dict_path")
        self.plugins.append(ZstdCodecPlugin(level=zstd_level, dict_path=dict_path))

        # Huffman stage (optional)
        if cfg.get("huffman", False):
            self.plugins.append(
                HuffmanPlugin(
                    enabled=True,
                    table_path=cfg.get("huffman_table"),
                    sample_corpus=cfg.get("sample_corpus"),
                )
            )

    def compress(self, data: bytes) -> bytes:
        """
        Sequentially apply each plugin.process() to the data.
        """
        for plugin in self.plugins:
            data = plugin.process(data)
        return data

    def decompress(self, data: bytes) -> bytes:
        """
        Apply each plugin.reverse() in reverse order.
        """
        for plugin in reversed(self.plugins):
            data = plugin.reverse(data)
        return data
