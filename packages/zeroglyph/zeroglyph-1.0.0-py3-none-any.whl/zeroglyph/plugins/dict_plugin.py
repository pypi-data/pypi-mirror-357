class StaticDictPlugin:
    """
    Static Dictionary Plugin (stub).

    Purpose:
      - Holds the path to a pre-trained dictionary file.
      - Dictionary loading and application is handled by the ZstdCodecPlugin.
    """

    def __init__(self, dict_path: str):
        """
        :param dict_path: Path to a .dict file generated for Zstandard.
        """
        self.dict_path = dict_path

    def process(self, data: bytes) -> bytes:
        """
        No-op here; the actual dictionary use is in ZstdCodecPlugin.
        """
        return data

    def reverse(self, data: bytes) -> bytes:
        """
        No-op here; the actual dictionary use is in ZstdCodecPlugin.
        """
        return data
