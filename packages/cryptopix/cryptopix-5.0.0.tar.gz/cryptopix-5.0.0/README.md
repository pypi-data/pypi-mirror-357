# CryptoPIX v5.0.0 - Revolutionary Post-Quantum Cryptographic Library

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/cryptopix-official/cryptopix)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://python.org)
[![Website](https://img.shields.io/badge/website-cryptopix.in-blue.svg)](https://www.cryptopix.in)

The world's first **Color Lattice Learning with Errors (CLWE)** cryptographic system, providing revolutionary post-quantum security through innovative color-based transformations.

## Revolutionary Features

- **ChromaCrypt Key Encapsulation Mechanism (KEM)** - Post-quantum secure key exchange
- **ChromaCrypt Digital Signatures** - Color-based commitment schemes with geometric proofs
- **Color Cipher** - Symmetric encryption with visual steganographic properties
- **Color Hash** - Visual fingerprinting and data verification
- **Multi-Domain Security** - Mathematical + Visual + Geometric protection layers
- **Performance Optimized** - JIT compilation, vectorization, and parallel processing

## Installation

```bash
pip install cryptopix
```

> **For Publishers**: See [PYPI_PUBLISHING_GUIDE.md](PYPI_PUBLISHING_GUIDE.md) for complete PyPI publishing instructions.

### Optional Performance Dependencies

```bash
# For JIT compilation and performance optimizations
pip install cryptopix[fast]

# For GPU acceleration support
pip install cryptopix[gpu]

# For development and testing
pip install cryptopix[dev]

# Install everything
pip install cryptopix[all]
```

## Quick Start

```python
import cryptopix

# Key Encapsulation Mechanism
kem = cryptopix.create_kem(128)
public_key, private_key = kem.keygen()
shared_secret, capsule = kem.encapsulate(public_key)
recovered_secret = kem.decapsulate(private_key, capsule)

# Digital Signatures
sign_scheme = cryptopix.create_signature_scheme(128)
key_pair = sign_scheme.keygen()
signature = sign_scheme.sign(b"message", key_pair)
is_valid = sign_scheme.verify(b"message", signature, key_pair)

# Symmetric Encryption
cipher = cryptopix.create_cipher(128, fast_mode=True)
ciphertext, color_key = cipher.encrypt(b"secret data", "password")
plaintext = cipher.decrypt(ciphertext, color_key, "password")

# Color Hashing
hasher = cryptopix.create_hash(128)
colors = hasher.hash_to_colors(b"data to hash")
is_valid = hasher.verify_hash(b"data to hash", colors)
```

## Command Line Interface

```bash
# Generate keys
cryptopix keygen --type kem --security 128 --output keys/

# Sign a file
cryptopix sign --key keys/signature.key --file document.txt

# Encrypt data
cryptopix encrypt --mode fast --password secret --input data.txt --output data.enc

# Hash to colors
cryptopix hash --input image.jpg --output colors.json
```

## Security Levels

CryptoPIX supports multiple security levels:

- **128-bit** - Standard post-quantum security
- **192-bit** - Enhanced security for sensitive applications  
- **256-bit** - Maximum security for critical systems

## Performance Optimizations

Enable performance optimizations:

```python
import cryptopix

# Enable all available optimizations
optimizations = cryptopix.enable_optimizations()
print(f"Enabled: {optimizations['enabled_optimizations']}")

# Benchmark performance
profiler = cryptopix.PerformanceProfiler()
kem_stats = profiler.profile_kem_operations(cryptopix.create_kem(128))
```

## Revolutionary Mathematics

CryptoPIX introduces the world's first **Color Lattice Learning with Errors (CLWE)** problem:

```
Traditional LWE: b = A·s + e (mod q)
ChromaCrypt CLWE: C = Φ(A·s + e) ⊕ Ψ(position, color_history)
```

Where:
- `Φ` = Color transformation function (CryptoPIX core innovation)
- `Ψ` = Geometric position function in color space
- `C` = Color lattice point with visual steganographic properties

## Academic Impact

This library represents a paradigm shift in cryptography:

1. **Novel Hard Problems** - First cryptographic system based on color lattice mathematics
2. **Visual Cryptography** - Keys and signatures can be represented as images
3. **Multi-Layered Security** - Combines lattice, color, and geometric security
4. **Post-Quantum Resistance** - Immune to both classical and quantum attacks
5. **GPU Acceleration** - Natural parallel processing capabilities

## Development

```bash
# Clone repository
git clone https://github.com/cryptopix-official/cryptopix.git
cd cryptopix

# Install development dependencies
pip install -e .[dev]

# Run tests
python -m pytest cryptopix/tests/

# Run benchmarks
python examples/benchmark.py
```

## Library Structure

```
cryptopix/
├── core/                    # Core cryptographic algorithms
│   ├── chromacrypt_kem.py  # Key Encapsulation Mechanism
│   ├── chromacrypt_sign.py # Digital Signatures
│   ├── color_cipher.py     # Symmetric Encryption
│   ├── color_hash.py       # Hash Functions
│   ├── lattice.py          # Color Lattice Engine
│   ├── transforms.py       # Color Transformation Engine
│   └── parameters.py       # Security Parameters
├── utils/                   # Utility functions
│   ├── performance.py      # Performance optimizations
│   ├── validation.py       # Input validation
│   └── serialization.py    # Key serialization
├── tests/                   # Comprehensive test suite
├── examples/                # Usage examples
└── cli.py                   # Command-line interface
```

## Documentation

- [API Reference](https://www.cryptopix.in/docs)
- [Tutorial](https://www.cryptopix.in/tutorial)
- [Academic Paper](https://www.cryptopix.in/paper)
- [Performance Guide](https://www.cryptopix.in/performance)

## Contributing

We welcome contributions to advance post-quantum cryptography:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use CryptoPIX in your research, please cite:

```bibtex
@software{cryptopix2025,
  title={CryptoPIX: Revolutionary Post-Quantum Cryptography using Color Lattice Learning with Errors},
  author={CryptoPIX Team},
  year={2025},
  version={5.0.0},
  url={https://github.com/cryptopix-official/cryptopix}
}
```

## Contact

- Website: [www.cryptopix.in](https://www.cryptopix.in)
- Email: founder@cryptopix.in
- GitHub: [https://github.com/cryptopix-official/cryptopix](https://github.com/cryptopix-official/cryptopix)

---

**CryptoPIX v5.0.0** - The future of cryptography: secure, innovative, and beautifully visual.