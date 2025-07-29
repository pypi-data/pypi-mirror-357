# hashidf

A lightweight Python library for decoding Base64, ROT13, and SHA256 hashes. Designed for developers who need simple, reliable tools for hash manipulation.

## Features
- Decode Base64-encoded strings
- Decode ROT13-encoded strings
- Compute SHA256 hashes
- Lightweight with minimal dependencies
- Cross-platform compatibility

## Installation
```bash
pip install hashidf
```

## Usage
```python
from hashidf import decode_base64, decode_rot13, compute_sha256

# Decode Base64
print(decode_base64("SGVsbG8gV29ybGQ="))  # Outputs: Hello World

# Decode ROT13
print(decode_rot13("Uryyb Jbeyq"))  # Outputs: Hello World

# Compute SHA256
print(compute_sha256("Hello World"))  # Outputs: SHA256 hash
```

## Contributing
We welcome contributions! Please see our [GitHub repository](https://github.com/hashidf/hashidf) for details on how to submit issues or pull requests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support
For questions or support, contact us at [support@hashidf.org](mailto:support@hashidf.org) or open an issue on GitHub.

---
*hashidf* is maintained by a community of developers dedicated to providing reliable tools for hash decoding.