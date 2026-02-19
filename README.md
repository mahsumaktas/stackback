# stackback ⚡

> AI-powered terminal error fixer. Explains exceptions, suggests fixes, and searches Stack Overflow — all without leaving your terminal.

Inspired by [thefuck](https://github.com/nvbn/thefuck) (95K ⭐) and [rebound](https://github.com/shobrook/rebound) (4K ⭐), powered by LLMs.

## Install

```bash
pip install stackback
```

## Usage

```bash
sb python app.py
sb git comit -m "fix"
stackback run ./deploy.sh
```

When an error occurs, stackback gives you options:

```
✗ TypeError: list indices must be integers, not str (app.py:42)

[1] Apply fix    → data[int(idx)]
[2] Explain      → What went wrong and why
[3] Stack Overflow → Top 3 results
[4] Skip

Choice: _
```

## LLM Providers

Supports OpenAI, Claude, Gemini, and local Ollama.

```bash
sb config set provider openai
sb config set provider ollama  # free, local
```

## Status

🚧 v0.0.1 — Under active development

## License

MIT
