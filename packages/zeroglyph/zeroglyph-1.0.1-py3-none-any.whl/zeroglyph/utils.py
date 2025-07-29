def encode_varint(value: int) -> bytes:
    parts = []
    while True:
        to_write = value & 0x7F
        value >>= 7
        if value:
            parts.append(to_write | 0x80)
        else:
            parts.append(to_write)
            break
    return bytes(parts)


def decode_varint(data: bytes, offset: int = 0) -> (int, int):
    shift = 0
    result = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, offset
