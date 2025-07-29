import yaml
from typing import Dict, Any, Optional, Protocol
from .pipeline import PipelineManager, Plugin
from .framer import Framer
from .plugins.dict_plugin import StaticDictPlugin
from .plugins.zstd_plugin import ZstdCodecPlugin
from .plugins.huffman_plugin import HuffmanPlugin

class CompressorClient:
    """
    Public API for ZeroGlyph:
      - compress(text: str) -> bytes
      - decompress(packet: bytes) -> str
    """
    def __init__(self, config: Optional[Any] = None):
        # Load configuration from dict or YAML file
        self.config: Dict[str, Any] = self._load_config(config)
        # Initialize the TLV framer
        self.framer = Framer()
        # Build compression pipeline
        self.plugins: Dict[str, Plugin] = self._init_plugins()
        self.pipeline = PipelineManager(self.plugins)

    def _load_config(self, config: Optional[Any]) -> Dict[str, Any]:
        """
        Accepts either:
          - a dict of options, or
          - a path to a YAML file containing the options.
        Returns a dict of configuration values.
        """
        if isinstance(config, str):
            with open(config, 'r') as f:
                return yaml.safe_load(f)
        return config if config is not None else {}

    def _init_plugins(self) -> Dict[str, Plugin]:
        """
        Instantiate and order plugins based on config keys
