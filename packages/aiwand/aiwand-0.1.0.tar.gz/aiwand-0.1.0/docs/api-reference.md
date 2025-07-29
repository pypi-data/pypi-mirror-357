# API Reference

Complete documentation for all AIWand functions and features.

## Core Functions

### `summarize(text, max_length=None, style="concise", model=None)`

Summarize text with customizable options.

**Parameters:**
- `text` (str): Text to summarize
- `max_length` (int, optional): Maximum words in summary
- `style` (str): Summary style - "concise", "detailed", or "bullet-points"
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Summarized text (str)

**Example:**
```python
import aiwand

# Basic summarization
summary = aiwand.summarize("Your long text here...")

# Customized summarization
summary = aiwand.summarize(
    text="Your text...",
    style="bullet-points",
    max_length=50,
    model="gemini-2.0-flash"
)
```

### `chat(message, conversation_history=None, model=None, temperature=0.7)`

Have a conversation with AI.

**Parameters:**
- `message` (str): Your message
- `conversation_history` (list, optional): Previous conversation messages
- `model` (str, optional): Specific model to use (auto-selected if not provided)
- `temperature` (float): Response creativity (0.0-1.0)

**Returns:** AI response (str)

**Example:**
```python
import aiwand

# Simple chat
response = aiwand.chat("What is machine learning?")

# Conversation with history
conversation = []
response1 = aiwand.chat("Hello!", conversation_history=conversation)
conversation.append({"role": "user", "content": "Hello!"})
conversation.append({"role": "assistant", "content": response1})

response2 = aiwand.chat("What did I just say?", conversation_history=conversation)
```

### `generate_text(prompt, max_tokens=500, temperature=0.7, model=None)`

Generate text from a prompt.

**Parameters:**
- `prompt` (str): Text prompt
- `max_tokens` (int): Maximum tokens to generate
- `temperature` (float): Response creativity (0.0-1.0)
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Generated text (str)

**Example:**
```python
import aiwand

# Basic generation
text = aiwand.generate_text("Write a poem about coding")

# Customized generation
text = aiwand.generate_text(
    prompt="Write a technical explanation of neural networks",
    max_tokens=300,
    temperature=0.3,
    model="gpt-4"
)
```

## Configuration Functions

### `configure_api_key(api_key, provider="openai")`

Set API key programmatically.

**Parameters:**
- `api_key` (str): Your API key
- `provider` (str): Provider type ("openai" or "gemini")

**Example:**
```python
import aiwand

# Configure OpenAI
aiwand.configure_api_key("your-openai-key", "openai")

# Configure Gemini
aiwand.configure_api_key("your-gemini-key", "gemini")
```

## Smart Model Selection

AIWand automatically selects the best available model:

| Available APIs | Default Model | Provider |
|----------------|---------------|----------|
| OpenAI only | `gpt-3.5-turbo` | OpenAI |
| Gemini only | `gemini-2.0-flash` | Gemini |
| Both available | Based on `AI_DEFAULT_PROVIDER` | Configurable |

### Supported Models

**OpenAI Models:**
- `gpt-3.5-turbo` (default)
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`

**Gemini Models:**
- `gemini-2.0-flash` (default)
- `gemini-2.5-flash`
- `gemini-2.5-pro`

## Error Handling

All functions raise appropriate exceptions:

```python
import aiwand

try:
    summary = aiwand.summarize("Some text")
except ValueError as e:
    print(f"Input error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Gemini API key  
- `AI_DEFAULT_PROVIDER`: Default provider when both keys available ("openai" or "gemini") 