# CLI Reference

Command line interface for AIWand.

## Basic Usage

```bash
aiwand [command] [options] [arguments]
```

## Commands

### `summarize`

Summarize text with various styles.

```bash
aiwand summarize "Your text here" [options]
```

**Options:**
- `--style {concise,detailed,bullet-points}` - Summary style (default: concise)
- `--max-length LENGTH` - Maximum words in summary
- `--model MODEL` - Specific AI model to use

**Examples:**
```bash
# Basic summarization
aiwand summarize "Machine learning is a powerful technology..."

# Bullet-point summary with length limit
aiwand summarize "Long text..." --style bullet-points --max-length 30

# Use specific model
aiwand summarize "Text..." --model gemini-2.0-flash
```

### `chat`

Have a conversation with AI.

```bash
aiwand chat "Your message" [options]
```

**Options:**
- `--model MODEL` - Specific AI model to use
- `--temperature TEMP` - Response creativity (0.0-1.0, default: 0.7)

**Examples:**
```bash
# Simple chat
aiwand chat "What is machine learning?"

# More creative response
aiwand chat "Tell me a story" --temperature 0.9

# Use specific model
aiwand chat "Explain quantum computing" --model gpt-4
```

### `generate`

Generate text from a prompt.

```bash
aiwand generate "Your prompt" [options]
```

**Options:**
- `--max-tokens TOKENS` - Maximum tokens to generate (default: 500)
- `--temperature TEMP` - Response creativity (0.0-1.0, default: 0.7)
- `--model MODEL` - Specific AI model to use

**Examples:**
```bash
# Generate a poem
aiwand generate "Write a haiku about programming"

# Longer, more creative text
aiwand generate "Write a story about AI" --max-tokens 800 --temperature 0.8

# Technical writing with specific model
aiwand generate "Explain neural networks" --model gpt-4 --temperature 0.3
```

## Global Options

These work with all commands:

- `--help, -h` - Show help message
- `--version` - Show version information

## Examples

```bash
# Get help
aiwand --help
aiwand summarize --help

# Check version
aiwand --version

# Multiple operations
aiwand summarize "AI is transforming industries..." --style detailed
aiwand chat "What are the implications of this?"
aiwand generate "Write recommendations based on this discussion"
```

## Environment Variables

The CLI uses the same environment variables as the Python package:

- `OPENAI_API_KEY` - Your OpenAI API key
- `GEMINI_API_KEY` - Your Gemini API key
- `AI_DEFAULT_PROVIDER` - Default provider ("openai" or "gemini")

## Smart Model Selection

The CLI automatically selects the best available model based on your API keys:

- **OpenAI only**: Uses `gpt-3.5-turbo`
- **Gemini only**: Uses `gemini-2.0-flash`
- **Both available**: Uses `AI_DEFAULT_PROVIDER` preference 