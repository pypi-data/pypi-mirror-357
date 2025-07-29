# src/zeroglyph/plugins/huffman_plugin.py

"""
HuffmanPlugin: Implements Huffman entropy coding for residual data.
Uses the `huffman` PyPI library to build a codebook and Python’s pickle
for saving/loading that table.
"""

import os
import pickle  # for persistence
from typing import Optional
from collections import Counter  # to derive symbol frequencies
import huffman  # pip install huffman

class HuffmanPlugin:
    def __init__(
        self,
        enabled: bool = True,
        table_path: Optional[str] = None,
        sample_corpus: Optional[str] = None
    ):
        """
        :param enabled: Whether to activate Huffman stage.
        :param table_path: Path to save/load the Huffman code table.
        :param sample_corpus: Path to a file for building frequency counts.
        """
        self.enabled = enabled
        self.table_path = table_path
        self.codebook = None

        if not enabled:
            return

        # 1. Load existing codebook if it exists
        if table_path and os.path.isfile(table_path):
            with open(table_path, 'rb') as f:
                self.codebook = pickle.load(f)  # pickle for persistence :contentReference[oaicite:0]{index=0}
        else:
            # 2. Read sample data (or fallback to common words)
            data = b''
            if sample_corpus and os.path.isfile(sample_corpus):
                with open(sample_corpus, 'rb') as f:
                    data = f.read()
            if not data:
                words = ['the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'I', 'it']
                data = b' '.join(word.encode('utf-8') for word in words)

            # 3. Build frequency map and codebook
            freq_map = Counter(data)  # {byte: count} :contentReference[oaicite:1]{index=1}
            items = list(freq_map.items())  # list of (symbol_byte, weight)
            self.codebook = huffman.codebook(items)  # {symbol: code} :contentReference[oaicite:2]{index=2}

            # 4. Persist the codebook if requested
            if table_path:
                with open(table_path, 'wb') as f:
                    pickle.dump(self.codebook, f)  # save via pickle :contentReference[oaicite:3]{index=3}

    def process(self, data: bytes) -> bytes:
        """
        Encode bytes to a packed bitstream using the codebook.
        """
        if not self.enabled or not self.codebook:
            return data

        # Convert each byte to its Huffman code, concatenate bits
        bitstr = ''.join(self.codebook[b] for b in data)
        # Pack every 8 bits into a byte (pad final byte with zeros)
        out = bytearray()
        for i in range(0, len(bitstr), 8):
            chunk = bitstr[i:i+8].ljust(8, '0')
            out.append(int(chunk, 2))
        return bytes(out)

    def reverse(self, data: bytes) -> bytes:
        """
        Decode the Huffman bitstream back to the original bytes.
        """
        if not self.enabled or not self.codebook:
            return data

        # Expand bytes to full bitstring
        bitstr = ''.join(f"{byte:08b}" for byte in data)
        # Invert codebook: {code: symbol}
        inv_map = {code: symbol for symbol, code in self.codebook.items()}

        decoded = []
        buffer = ''
        for bit in bitstr:
            buffer += bit
            if buffer in inv_map:
                decoded.append(inv_map[buffer])
                buffer = ''
        return bytes(decoded)
