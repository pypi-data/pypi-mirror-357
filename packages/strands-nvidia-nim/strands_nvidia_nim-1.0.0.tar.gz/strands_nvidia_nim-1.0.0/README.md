# Strands Nvidia NIM Provider

A minimal custom provider that fixes message formatting compatibility between Strands Agents SDK and Nvidia NIM API.

[![PyPI version](https://badge.fury.io/py/strands-nvidia-nim.svg)](https://badge.fury.io/py/strands-nvidia-nim)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Problem Solved

The standard Strands LiteLLM integration fails with Nvidia NIM because:
- **Strands** formats messages as structured content: `[{"text": "content", "type": "text"}]`
- **Nvidia NIM** expects simple string content: `"content"`

This provider bridges that gap by converting structured content to simple strings.

## Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install strands-nvidia-nim
```

### Option 2: Install from GitHub
```bash
pip install git+https://github.com/yourusername/strands-nvidia-nim.git
```

### Option 3: Local Development
```bash
git clone https://github.com/yourusername/strands-nvidia-nim.git
cd strands-nvidia-nim
pip install -e .
```

## Quick Start

### Option 1: Direct API Key
```python
from strands import Agent
from strands_tools import calculator
from strands_nvidia_nim import NvidiaNIM

# Create the provider
model = NvidiaNIM(
    api_key="your-nvidia-nim-api-key",
    model_id="meta/llama-3.1-70b-instruct",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

# Use with standard Strands Agent
agent = Agent(model=model, tools=[calculator])
agent("What is 123.456 * 789.012?")
```

### Option 2: Environment Variables (Recommended)
```bash
# Set your API key as an environment variable
export NVIDIA_NIM_API_KEY=your-nvidia-nim-api-key
```

```python
import os
from strands import Agent
from strands_tools import calculator
from strands_nvidia_nim import NvidiaNIM

model = NvidiaNIM(
    api_key=os.getenv("NVIDIA_NIM_API_KEY"),
    model_id="meta/llama-3.1-70b-instruct",
    params={"max_tokens": 1000, "temperature": 0.7}
)

agent = Agent(model=model, tools=[calculator])
agent("What is 123.456 * 789.012?")
```

## Available Models

Popular Nvidia NIM models:
- `meta/llama-3.1-70b-instruct` - High quality, larger model
- `meta/llama-3.1-8b-instruct` - Faster, smaller model  
- `meta/llama-3.3-70b-instruct` - Latest Llama model
- `mistralai/mistral-large` - Mistral's flagship model
- `nvidia/llama-3.1-nemotron-70b-instruct` - Nvidia-optimized

## Configuration

```python
model = NvidiaNIM(
    api_key="your-api-key",
    model_id="meta/llama-3.1-70b-instruct",
    params={
        "max_tokens": 1500,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
)
```

## Features

- ✅ **Fixes BadRequestError** - No more message formatting issues
- ✅ **Minimal Code** - Simple, focused solution
- ✅ **Standard Strands Pattern** - Uses `Agent(model=model, tools=[tools])`
- ✅ **Clean Output** - Proper streaming without artifacts
- ✅ **Error Handling** - Context window overflow detection

## Comparison

| Approach | Standard LiteLLM | This Provider |
|----------|------------------|---------------|
| Message Format | ❌ Fails with structured content | ✅ Converts to string format |
| Setup Complexity | ⚠️ Requires workarounds | ✅ Simple, clean setup |
| Strands Integration | ⚠️ Compatibility issues | ✅ Native integration |
| Error Handling | ⚠️ Generic errors | ✅ Strands-specific errors |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/strands-nvidia-nim/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/strands-nvidia-nim/discussions)
- 📖 **Documentation**: [README](https://github.com/yourusername/strands-nvidia-nim#readme)
