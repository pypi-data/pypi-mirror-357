import struct
import binascii
from .utils import encode_varint, decode_varint


class Framer:
    """
    TLV header packer/unpacker with varint length and CRC32 integrity.
    """

    MAGIC = b"ZG"
    SCHEME_ID = 1
    VERSION = 1
    FLAGS = 0
    CRC_SIZE = 4

    @staticmethod
    def pack(payload: bytes) -> bytes:
        length = len(payload)
        varint_len = encode_varint(length)
        crc = binascii.crc32(payload) & 0xFFFFFFFF

        header = bytearray()
        header += Framer.MAGIC
        header += struct.pack("B", Framer.SCHEME_ID)
        header += struct.pack("B", Framer.VERSION)
        header += struct.pack("B", Framer.FLAGS)
        header += varint_len
        header += struct.pack(">I", crc)

        return bytes(header) + payload

    @staticmethod
    def unpack(packet: bytes) -> bytes:
        if packet[:2] != Framer.MAGIC:
            raise ValueError("Invalid magic header")
        if packet[2] != Framer.SCHEME_ID:
            raise ValueError(f"Unsupported scheme ID: {packet[2]}")

        offset = 5
        length, offset = decode_varint(packet, offset)
        crc_read = struct.unpack(">I", packet[offset : offset + Framer.CRC_SIZE])[0]
        offset += Framer.CRC_SIZE

        payload = packet[offset : offset + length]
        crc_calc = binascii.crc32(payload) & 0xFFFFFFFF
        if crc_read != crc_calc:
            raise ValueError("CRC mismatch")

        return payload
