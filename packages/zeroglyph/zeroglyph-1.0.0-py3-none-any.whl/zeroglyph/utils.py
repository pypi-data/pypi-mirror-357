"""
Utility functions: varint (LEB128) encoding/decoding and other helpers.
"""

def encode_varint(number: int) -> bytes:
    """Encode an integer as unsigned LEB128 (little-endian)."""
    result = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            result.append(byte | 0x80)
        else:
            result.append(byte)
            break
    return bytes(result)

def decode_varint(buffer: bytes, offset: int = 0) -> (int, int):
    """Decode an unsigned LEB128 varint from buffer starting at offset.
    Returns a tuple (value, new_offset)."""
    shift = 0
    result = 0
    pos = offset
    while True:
        byte = buffer[pos]
        result |= (byte & 0x7F) << shift
        pos += 1
        if not (byte & 0x80):
            break
        shift += 7
    return result, pos
