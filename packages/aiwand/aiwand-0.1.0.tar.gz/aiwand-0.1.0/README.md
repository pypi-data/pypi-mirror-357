# AIWand 🪄

> A simple and elegant Python package for AI-powered text processing using OpenAI and Google Gemini APIs.

[![PyPI version](https://img.shields.io/pypi/v/aiwand.svg)](https://pypi.org/project/aiwand/)
[![Python versions](https://img.shields.io/pypi/pyversions/aiwand.svg)](https://pypi.org/project/aiwand/)
[![License](https://img.shields.io/pypi/l/aiwand.svg)](https://github.com/onlyoneaman/aiwand/blob/main/LICENSE)

## ✨ Features

- **Smart Provider Selection** - Automatically uses OpenAI or Gemini based on available keys
- **Text Summarization** - Create concise, detailed, or bullet-point summaries  
- **AI Chat** - Have conversations with context history
- **Text Generation** - Generate content from prompts
- **CLI Interface** - Use from command line
- **Virtual Environment Ready** - Easy setup with automated scripts

## 🚀 Quick Start

### Installation

```bash
# Using pip
pip install aiwand

# With virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install aiwand
```

### Basic Usage

```python
import aiwand

# Set your API key
aiwand.configure_api_key("your-api-key", "openai")  # or "gemini"

# Summarize text
summary = aiwand.summarize("Your long text here...")

# Chat with AI  
response = aiwand.chat("What is machine learning?")

# Generate text
story = aiwand.generate_text("Write a poem about coding")
```

### CLI Usage

```bash
# Summarize text
aiwand summarize "Your text here" --style bullet-points

# Chat with AI
aiwand chat "Explain quantum computing"

# Generate content
aiwand generate "Write a haiku about programming"
```

## 🔧 Configuration

Set your API keys via environment variables:

```bash
# Option 1: OpenAI
export OPENAI_API_KEY="your-openai-key"

# Option 2: Gemini  
export GEMINI_API_KEY="your-gemini-key"

# Option 3: Both (set preference)
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export AI_DEFAULT_PROVIDER="gemini"  # or "openai"
```

Or use a `.env` file:
```
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
AI_DEFAULT_PROVIDER=openai
```

## 📚 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[API Reference](docs/api-reference.md)** - Complete function documentation  
- **[CLI Reference](docs/cli.md)** - Command line usage
- **[Virtual Environment Guide](docs/venv-guide.md)** - Best practices for Python environments

## 🤝 Connect

- **GitHub**: [github.com/onlyoneaman/aiwand](https://github.com/onlyoneaman/aiwand)
- **PyPI**: [pypi.org/project/aiwand](https://pypi.org/project/aiwand/)
- **X (Twitter)**: [@onlyoneaman](https://x.com/onlyoneaman)

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [Aman Kumar](https://x.com/onlyoneaman)** 