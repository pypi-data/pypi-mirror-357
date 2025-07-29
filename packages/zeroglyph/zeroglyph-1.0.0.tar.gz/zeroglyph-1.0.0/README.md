# ZeroGlyph: Ultra-Compact Text Compression for AI APIs

A modular, high-performance framework leveraging static LZ77 + Huffman coding, Zstandard, and a binary TLV header for sub-10 ms/KiB latency and ≥ 5× compression on UTF-8 text.

## Table of Contents
1. [Features](#features)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Usage](#usage)
   - [Basic Compression](#basic-compression)
   - [Configuration](#configuration)
4. [Architecture Overview](#architecture-overview)
5. [Plugin System](#plugin-system)
6. [Contributing](#contributing)
7. [License](#license)

## Features
- **High Compression Ratio**: Achieves ≥ 5× size reduction on typical English text using static-dictionary LZ77 + Huffman entropy coding.
- **Low Latency**: Encode/decode under 10 ms per 1 KiB on mid-range CPUs via Zstandard and hardware-accelerated CRC32 checks.
- **Modular Plugins**: Swap in Zstd, dedicated Huffman, static dictionaries, or future neural compressors via a clear plugin API.
- **Binary TLV Framing**: Compact header with varint length encoding and CRC32 ensures integrity and extensibility.
- **UTF-8 & Multi-Language**: Full support for emojis, CJK, and other Unicode characters with lossless recovery.

## Getting Started

### Prerequisites
- **Python 3.8+**
- **pip** package manager

### Installation
```bash
# Clone the repo
git clone https://github.com/<your-username>/ZeroGlyph.git
cd ZeroGlyph

# Install dependencies
pip install -r requirements.txt
```
*We recommend using a virtual environment (venv or conda) to avoid dependency conflicts.*

## Usage

### Basic Compression
```python
from zeroglyph import CompressorClient

client = CompressorClient(config={
    'zstd_level': 1,
    'huffman': True,
    'dict_path': 'sample.dict'
})
packet = client.compress("Hello, ZeroGlyph!")
text   = client.decompress(packet)
assert text == "Hello, ZeroGlyph!"
```

### Configuration
Configuration options can be passed via a `dict` or YAML file:
```yaml
# config.yaml
zstd_level: 3        # Zstandard compression level (1–22)
huffman: true        # Enable additional Huffman stage
dict_path: sample.dict  # Path to static dictionary file
```
Load via:
```python
client = CompressorClient(config="config.yaml")
```
*YAML support requires `PyYAML` installed.*

## Architecture Overview
ZeroGlyph’s pipeline comprises:
1. **Static Dictionary Loader** (optional)
2. **Zstandard Codec Plugin**
3. **Huffman Entropy Plugin** (optional)
4. **Framer** (binary TLV header + CRC32)

![Architecture Diagram](docs/architecture.png)

## Plugin System
Each stage implements the `Plugin` protocol:
```python
class Plugin(Protocol):
    def process(self, data: bytes) -> bytes: ...
    def reverse(self, data: bytes) -> bytes: ...
```
- **StaticDictPlugin**: seeds LZ77 dictionary from `.dict` files.
- **ZstdCodecPlugin**: wraps `zstandard.ZstdCompressor` & `ZstdDecompressor`.
- **HuffmanPlugin**: optional stage for residual entropy coding.

## Contributing
We welcome all contributions! Please follow these steps:
1. **Fork** the repo and create a feature branch (`git checkout -b feat/your-feature`).
2. **Implement** your feature or fix and add tests.
3. **Commit** your changes with clear messages (`git commit -m "feat: add ..."`).
4. **Push** to your branch and open a **Pull Request** against `main`.
5. **Review** will include CI checks (lint, tests, benchmarks).

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## License
This project is licensed under the **MIT License**—see [LICENSE](LICENSE) for details.
