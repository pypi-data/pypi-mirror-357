from typing import Protocol, Dict, Any

class Plugin(Protocol):
    """
    Compression pipeline plugin interface.
    Each plugin implements `process` for compression and `reverse` for decompression.
    """
    def process(self, data: bytes) -> bytes:
        ...
    def reverse(self, data: bytes) -> bytes:
        ...

class PipelineManager:
    """
    Executes plugins in sequence for compression, and in reverse for decompression.
    """
    def __init__(self, plugins: Dict[str, Plugin]):
        # plugins should be an ordered dict if order matters
        self.plugins = plugins

    def compress(self, raw: bytes) -> bytes:
        """
        Pass raw bytes through each plugin's `process` method.
        """
        data = raw
        for plugin in self.plugins.values():
            data = plugin.process(data)
        return data

    def decompress(self, data: bytes) -> bytes:
        """
        Pass data through each plugin's `reverse` method in reverse order.
        """
        result = data
        for plugin in reversed(list(self.plugins.values())):
            result = plugin.reverse(result)
        return result
