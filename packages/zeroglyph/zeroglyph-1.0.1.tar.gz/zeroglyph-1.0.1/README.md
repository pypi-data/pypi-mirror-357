# ZeroGlyph

[![CI](https://github.com/goodzeeak/ZeroGlyph/actions/workflows/ci.yml/badge.svg)](https://github.com/goodzeeak/ZeroGlyph/actions/workflows/ci.yml)  
[![Codecov](https://codecov.io/gh/goodzeeak/ZeroGlyph/branch/main/graph/badge.svg)](https://codecov.io/gh/goodzeeak/ZeroGlyph)  
[![PyPI version](https://badge.fury.io/py/zeroglyph.svg)](https://pypi.org/project/zeroglyph)  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

ZeroGlyph is an open-source compression framework that **dynamically compresses human language** for AI interactions—minimizing token usage, cutting cloud costs, and reducing AI inference energy. It wraps any AI endpoint (API or web UI) in a zero-overhead compression protocol, enabling businesses to **slash AI bills by up to 80%** while maintaining full fidelity.

---

## 🚀 Key Features

- **End-to-end compression**: Zstandard + Huffman + TLV framing for both prompts and replies, driven by a simple system prompt protocol.  
- **Plugin-based**: Swap or extend codecs via static-dictionary, Zstd, Huffman, or your own module.  
- **Zero dependencies** beyond `zstandard`, `pyyaml`, and `huffman`—easy to install and integrate.  
- **Cross-platform**: Python 3.8+ support, with CI validation on 3.8–3.11.  
- **Extensible clients**: Built-in support for OpenAI API, Azure OpenAI, and browser-automated ChatGPT flows.  

---

## 🎯 Business Value

- **Cost reduction**: Typical English text compresses ≥5×, translating to ∼80% fewer tokens and massive savings on AI invoice lines.  
- **Energy efficiency**: Fewer tokens means ⩽70% less compute energy per inference, aligning with corporate sustainability targets.  
- **Developer productivity**: One unified Python API and optional CLI or web demo—get running in minutes, not days.  
- **Open collaboration**: MIT-licensed, community-driven, with clear contribution guidelines and issue templates.

---

## 🎨 Architecture

![ZeroGlyph Architecture](/docs/architecture.png)  
ZeroGlyph layers:  
1. **CompressorClient**: Python façade with YAML/dict config  
2. **Framer**: TLV header (magic, version, varint length, CRC32)  
3. **PipelineManager**: Ordered `process`/`reverse` plugin execution  
4. **Plugins**: Static dict, Zstd, Huffman (modular)  

---

## 💡 Quickstart

```bash
# Clone & install
git clone https://github.com/goodzeeak/ZeroGlyph.git
cd ZeroGlyph
pip install -e .

# In Python
from zeroglyph.client import CompressorClient
client = CompressorClient({
  'zstd_level': 3,
  'huffman': True,
  'dict_path': 'sample.dict'
})
packet = client.compress("Hello, ZeroGlyph!")
print(client.decompress(packet))
```

For end-to-end AI integration—see [examples/ai_chat.py](examples/ai_chat.py) for a full OpenAI workflow with Base64 framing.

---

## 📚 Documentation & Examples

- **`docs/`**: Architecture diagrams, protocol details  
- **`examples/`**:  
  - `cli_compress.py`: stdin → ZeroGlyph → stdout  
  - `ai_chat.py`: End-to-end compressed chat via OpenAI  
- **API reference**: coming soon via MkDocs/GitHub Pages

---

## 🤝 Contributing

We welcome all contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow our templates for issues and pull requests.

---

## ⚖️ License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
