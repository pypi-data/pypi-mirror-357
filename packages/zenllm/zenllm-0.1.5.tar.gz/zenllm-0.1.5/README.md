# 🧘‍♂️ ZenLLM

[![PyPI version](https://badge.fury.io/py/zenllm.svg)](https://badge.fury.io/py/zenllm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)

The zen, simple, and unified API to prompt LLMs from different providers using a single function call.

> **Our Goal:** No fancy dependencies, no SDK bloat. Just `requests` and your API keys. Easily switch between models and providers without changing your code.

## ✨ Key Features

- **Unified API**: A single `prompt()` function for Anthropic, Google, and OpenAI.
- **Easy Model Switching**: Change models and providers with a single `model` argument.
- **Lightweight**: Built with only the `requests` library. No heavy SDKs to install.
- **Simple Authentication**: Just set your provider's API key as an environment variable.

## 🚀 Installation

```bash
pip install zenllm
```

## 💡 Usage

First, make sure you've set your API key as an environment variable (e.g., `export OPENAI_API_KEY="your-key"`).

### Basic Prompt

The default model is `gpt-4.1`. You can change this by setting the `ZENLLM_DEFAULT_MODEL` environment variable.

```python
from zenllm import prompt

# Uses the default model (either the fallback or ZENLLM_DEFAULT_MODEL)
response = prompt("Why is the sky blue?")
print(response)
```

### Using another Provider (Google's Gemini)

Simply change the model name to use a different provider.

```python
from zenllm import prompt

response = prompt(
    "Why is the sky blue?",
    model="gemini-2.5-pro",
    system_prompt="Reply only in French."
)
print(response)
```

### Using Anthropic

```python
from zenllm import prompt

response = prompt(
    "Tell me a three sentence bedtime story about a unicorn.",
    model="claude-sonnet-4-20250514"
)
print(response)
```

### Using TogetherAI

To use models from TogetherAI, prefix the model name with `together/`.

```python
from zenllm import prompt

response = prompt(
    "What are the top 3 things to do in New York?",
    model="together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
)
print(response)
```

### Streaming Responses

Set `stream=True` to get a generator of response chunks.

```python
from zenllm import prompt

response_stream = prompt(
    "Tell me a story about a robot.", 
    model="claude-sonnet-4-20250514", 
    stream=True
)
for chunk in response_stream:
    print(chunk, end="", flush=True)
```

## ✅ Supported Providers

| Provider  | Environment Variable  | Model Prefix | Example Models                                       |
| :-------- | :-------------------- | :----------- | :--------------------------------------------------- |
| Anthropic | `ANTHROPIC_API_KEY`   | `claude`     | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` |
| Deepseek  | `DEEPSEEK_API_KEY`    | `deepseek`   | `deepseek-chat`, `deepseek-reasoner`                 |
| Google    | `GEMINI_API_KEY`      | `gemini`     | `gemini-2.5-pro`, `gemini-2.5-flash`                 |
| OpenAI    | `OPENAI_API_KEY`      | `gpt`        | `gpt-4.1`                                            |
| TogetherAI| `TOGETHER_API_KEY`    | `together`   | `together/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` |

*Note: Streaming is not yet supported for OpenAI with this library.*

## 📜 License

MIT License - Copyright (c) 2025 Koen van Eijk