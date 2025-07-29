# AIWand 🪄

A simple and elegant Python package for AI-powered text processing using OpenAI and Google Gemini APIs.

## Features

- **Text Summarization**: Create concise, detailed, or bullet-point summaries
- **AI Chat**: Have conversations with AI models
- **Text Generation**: Generate text from prompts
- **Smart Provider Selection**: Automatically uses available API (OpenAI or Gemini)
- **Multiple AI Providers**: Support for both OpenAI and Google Gemini
- **CLI Interface**: Use directly from command line
- **Environment Variables**: Secure API key management

## Installation

### Recommended: Using Virtual Environment

We strongly recommend using a virtual environment to avoid conflicts with other packages:

```bash
# Create a virtual environment
python -m venv .venv

# Activate it (Linux/Mac)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate

# Install aiwand
pip install aiwand
```

### From PyPI (when published)
```bash
pip install aiwand
```

### Development Installation

**Quick Setup (Recommended)**

Use our setup scripts for automatic environment configuration:

```bash
# Linux/Mac
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh

# Windows
scripts\setup-dev.bat
```

**Manual Setup**

**Step 1: Clone and setup virtual environment**
```bash
git clone <your-repo-url>
cd aiwand

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

**Step 2: Install in development mode**
```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install requirements directly
pip install -r requirements.txt
```

**Step 3: Verify installation**
```bash
python test_install.py
```

## Quick Start

### 1. Set up your API Key

AIWand is smart about API provider selection:
- **If only OpenAI key is available** → Uses OpenAI models
- **If only Gemini key is available** → Uses Gemini models  
- **If both keys are available** → Uses `AI_DEFAULT_PROVIDER` preference (defaults to OpenAI)

**Option A: OpenAI Only**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option B: Google Gemini Only**
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

**Option C: Both with Preference**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export GEMINI_API_KEY="your-gemini-api-key-here"
export AI_DEFAULT_PROVIDER="gemini"  # or "openai"
```

**Using .env File**
Create a `.env` file in your project:
```
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
AI_DEFAULT_PROVIDER=openai
```

**Programmatically**
```python
import aiwand
# For OpenAI
aiwand.configure_api_key("your-api-key-here", "openai")
# For Gemini
aiwand.configure_api_key("your-api-key-here", "gemini")
```

### 2. Basic Usage

```python
import aiwand

# Summarize text (auto-selects best available AI)
text = """
Artificial Intelligence (AI) is intelligence demonstrated by machines, 
in contrast to the natural intelligence displayed by humans and animals. 
Leading AI textbooks define the field as the study of "intelligent agents": 
any device that perceives its environment and takes actions that maximize 
its chance of successfully achieving its goals.
"""

summary = aiwand.summarize(text)
print(summary)

# Chat with AI
response = aiwand.chat("What is the future of AI?")
print(response)

# Generate text
story = aiwand.generate_text("Write a short story about a robot learning to paint")
print(story)
```

## Advanced Usage

### Customized Summarization

```python
import aiwand

# Different summary styles
summary = aiwand.summarize(
    text="Your long text here...",
    style="bullet-points",  # 'concise', 'detailed', 'bullet-points'
    max_length=50,          # Maximum words
    model="gemini-2.0-flash"  # Specify model (optional)
)
```

### Conversation History

```python
import aiwand

# Maintain conversation context
conversation = []
response1 = aiwand.chat("Hello, how are you?", conversation_history=conversation)
conversation.append({"role": "user", "content": "Hello, how are you?"})
conversation.append({"role": "assistant", "content": response1})

response2 = aiwand.chat("What did I just ask you?", conversation_history=conversation)
```

### Custom Parameters

```python
import aiwand

# Fine-tune generation
text = aiwand.generate_text(
    prompt="Write a poem about coding",
    max_tokens=200,
    temperature=0.8,  # Higher = more creative
    model="gpt-4"     # Specify model (optional)
)
```

## Command Line Interface

AIWand provides a CLI for quick tasks:

```bash
# Summarize text (auto-selects AI provider)
aiwand summarize "Your text here" --style concise --max-length 30

# Chat
aiwand chat "What is machine learning?"

# Generate text
aiwand generate "Write a haiku about programming" --temperature 0.9
```

## API Reference

### `summarize(text, max_length=None, style="concise", model=None)`

Summarize text with customizable options.

**Parameters:**
- `text` (str): Text to summarize
- `max_length` (int, optional): Maximum words in summary
- `style` (str): Summary style - "concise", "detailed", or "bullet-points"
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Summarized text (str)

### `chat(message, conversation_history=None, model=None, temperature=0.7)`

Have a conversation with AI.

**Parameters:**
- `message` (str): Your message
- `conversation_history` (list, optional): Previous conversation messages
- `model` (str, optional): Specific model to use (auto-selected if not provided)
- `temperature` (float): Response creativity (0.0-1.0)

**Returns:** AI response (str)

### `generate_text(prompt, max_tokens=500, temperature=0.7, model=None)`

Generate text from a prompt.

**Parameters:**
- `prompt` (str): Text prompt
- `max_tokens` (int): Maximum tokens to generate
- `temperature` (float): Response creativity (0.0-1.0)
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Generated text (str)

### `configure_api_key(api_key, provider="openai")`

Set API key programmatically.

**Parameters:**
- `api_key` (str): Your API key
- `provider` (str): Provider type ("openai" or "gemini")

## Smart Model Selection

AIWand automatically selects the best available model:

| Available APIs | Default Model | Provider |
|----------------|---------------|----------|
| OpenAI only | `gpt-3.5-turbo` | OpenAI |
| Gemini only | `gemini-2.0-flash` | Gemini |
| Both available | Based on `AI_DEFAULT_PROVIDER` | Configurable |

Supported models:
- **OpenAI**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`, etc.
- **Gemini**: `gemini-2.0-flash`, `gemini-2.5-flash`, `gemini-2.5-pro`, etc.

## Error Handling

```python
import aiwand

try:
    summary = aiwand.summarize("Some text")
except ValueError as e:
    print(f"Input error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Requirements

- Python 3.8+
- At least one API key (OpenAI or Gemini)
- Internet connection

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.0.1
- Initial release
- OpenAI and Gemini API support
- Smart provider selection
- Text summarization, chat, and generation
- CLI support
- Environment-based configuration 