# plug_mcp: The Missing Connector for AI

**plug_mcp** is a Python library that provides a simple and efficient way to connect your applications to AI models using the Multi-purpose Cooperative Protocol (MCP). It acts as a wrapper around the `mcp` library, offering a streamlined client interface for seamless integration with various AI providers and transport protocols.

[![PyPI version](https://badge.fury.io/py/plug-mcp.svg)](https://badge.fury.io/py/plug-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/Documentation-blue.svg)](https://2796gaurav.github.io/plug_mcp)

## Table of Contents

- [plug_mcp: The Missing Connector for AI](#plug_mcp-the-missing-connector-for-ai)
  - [✨ Features](#-features)
  - [🚀 Getting Started](#-getting-started)
    - [Installation](#installation)
    - [Quick Start](#quick-start)
  - [📚 Documentation](#-documentation)
  - [🗺️ Roadmap](#️-roadmap)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [⚠️ Disclaimer](#️-disclaimer)
  - [Code of Conduct](#code-of-conduct)
  - [🛡️ Security](#️-security)
  - [🌟 Showcase](#-showcase)
  - [💬 Support](#-support)
  - [🐍 Supported Python Versions](#-supported-python-versions)

## ✨ Features

- **Simplified Client Interface**: A high-level `MCPClient` for easy interaction with MCP servers.
- **Multi-provider Support**: Out-of-the-box support for Anthropic and OpenAI models.
- **Flexible Transports**: Connect to servers using STDIO, SSE, or Streamable HTTP.
- **Built-in Guardrails**: Protect your application with content filtering, PII masking, and injection detection.
- **Conversation Management**: Easily manage conversation history, context, and persistence.
- **Asynchronous by Design**: Built with `asyncio` for high-performance, non-blocking I/O.
- **Extensible**: Easily add new LLM providers, transports, or guardrails.

## 🚀 Getting Started

### Installation

```bash
pip install plug_mcp
```

### Quick Start

Here's a simple example of how to use `plug_mcp` to connect to an MCP server and interact with an AI model:

```python
import asyncio
from plug_mcp.client import MCPClient

async def main():
    # Connect to a local server using STDIO
    client = MCPClient(llm_provider="anthropic")
    await client.connect("python examples/simple_server/main.py")

    # Start a conversation
    conversation_id = client.start_conversation()
    print(f"Started conversation: {conversation_id}")

    # Send a message and get a response
    response = await client.query("Hello, world!")
    print(f"AI: {response}")

    # Disconnect from the server
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 Documentation

For full details on all features and the complete API reference, please visit our **[documentation site](https://2796gaurav.github.io/plug_mcp)**.

The documentation is automatically generated from the `main` branch and includes:

- A full **Getting Started** guide.
- In-depth **tutorials and examples**.
- The complete **API Reference**.

## 🗺️ Roadmap

- [ ] Add support for more LLM providers.
- [ ] Implement a more comprehensive test suite.
- [ ] Add more examples and tutorials.
- [ ] Improve documentation and type hinting.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute to `plug_mcp`, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and add tests.
4.  Ensure that the tests pass.
5.  Submit a pull request with a clear description of your changes.

## 📄 License

`plug_mcp` is licensed under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This project is under active development and may undergo significant changes.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for everyone. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🛡️ Security

If you discover a security vulnerability, please report it to us by emailing [2796gaurav@gmail.com](mailto:2796gaurav@gmail.com). We will address all reports promptly.

## 🌟 Showcase

Have you built something cool with `plug_mcp`? Written an article or created a video? We'd love to see it! Please open a pull request to add your project to this list.

## 💬 Support

If you have questions or need help, please open an issue in the [issue tracker](https://github.com/2796gaurav/plug_mcp/issues).

## 🐍 Supported Python Versions

`plug_mcp` is tested and supported on the following Python versions:

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11 