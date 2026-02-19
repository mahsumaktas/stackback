# stackback ⚡

[![CI](https://github.com/mahsumaktas/stackback/actions/workflows/ci.yml/badge.svg)](https://github.com/mahsumaktas/stackback/actions)
[![PyPI](https://img.shields.io/pypi/v/stackback?color=blue)](https://pypi.org/project/stackback/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> AI-powered terminal error fixer. Explains Python exceptions, suggests fixes, and searches Stack Overflow — all without leaving your terminal.

Inspired by [thefuck](https://github.com/nvbn/thefuck) (95K ⭐) and [rebound](https://github.com/shobrook/rebound) (4.1K ⭐, abandoned 2022), rebuilt for the LLM era.

## Features

- 🔍 **Understands your errors** — LLM explains what went wrong in plain English
- 🛠️ **Suggests fixes** — get a ready-to-apply code patch
- 📚 **Stack Overflow integration** — surfaces top 3 relevant threads
- 🤖 **Provider agnostic** — OpenAI, Claude, Gemini, or local Ollama (free)
- ⚡ **Fast** — interactive numbered menu, no browser needed

## Install

```bash
pip install stackback
```

## Usage

```bash
sb python app.py
sb git comit -m "fix"
```

When an error occurs:

```
✗ TypeError: list indices must be integers, not str  (app.py:42)

[1] Apply fix        → data[int(idx)]
[2] Explain more     → Why does this happen?
[3] Stack Overflow   → 3 relevant threads
[4] Skip

Choice: _
```

## Configure LLM

```bash
sb config set provider openai    # default
sb config set provider ollama    # free, fully local
sb config set provider claude
sb config set provider gemini
```

## Roadmap

- [x] v0.0.1 — Project skeleton
- [ ] v0.0.2 — Traceback parser
- [ ] v0.0.3 — OpenAI LLM integration
- [ ] v0.0.4 — Interactive TUI menu
- [ ] v0.0.5 — Stack Overflow API (top 3 answers)
- [ ] v0.0.6 — Multi-provider support (Claude, Gemini)
- [ ] v0.0.7 — Auto-fix engine
- [ ] v0.0.8 — Ollama local support
- [ ] v0.1.0 — PyPI stable release

## Contributing

PRs welcome! See [open issues](https://github.com/mahsumaktas/stackback/issues) for good first tasks.

## License

MIT
