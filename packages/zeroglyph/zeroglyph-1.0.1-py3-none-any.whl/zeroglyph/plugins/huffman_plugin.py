import os
import pickle
from collections import Counter
from typing import Optional
import huffman


class HuffmanPlugin:
    """
    Huffman entropy coding plugin using the `huffman` library.
    """

    def __init__(
        self,
        enabled: bool = True,
        table_path: Optional[str] = None,
        sample_corpus: Optional[str] = None,
    ):
        self.enabled = enabled
        self.table_path = table_path
        self.codebook = None

        if not enabled:
            return

        if table_path and os.path.isfile(table_path):
            with open(table_path, "rb") as f:
                self.codebook = pickle.load(f)
        else:
            data = b""
            if sample_corpus and os.path.isfile(sample_corpus):
                with open(sample_corpus, "rb") as f:
                    data = f.read()
            if not data:
                words = ["the", "and", "to", "of", "a", "in", "that", "is", "I", "it"]
                data = b" ".join(w.encode() for w in words)

            freq_map = Counter(data)
            items = list(freq_map.items())
            self.codebook = huffman.codebook(items)

            if table_path:
                with open(table_path, "wb") as f:
                    pickle.dump(self.codebook, f)

    def process(self, data: bytes) -> bytes:
        if not self.enabled or not self.codebook:
            return data

        bitstr = "".join(self.codebook[b] for b in data)
        out = bytearray()
        for i in range(0, len(bitstr), 8):
            byte = bitstr[i : i + 8].ljust(8, "0")
            out.append(int(byte, 2))
        return bytes(out)

    def reverse(self, data: bytes) -> bytes:
        if not self.enabled or not self.codebook:
            return data

        bitstr = "".join(f"{byte:08b}" for byte in data)
        inv_map = {code: sym for sym, code in self.codebook.items()}

        decoded = []
        buf = ""
        for bit in bitstr:
            buf += bit
            if buf in inv_map:
                decoded.append(inv_map[buf])
                buf = ""
        return bytes(decoded)
