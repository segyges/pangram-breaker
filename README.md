# pangram-breaker

Security research tool for testing AI-generated text detection via [Pangram](https://www.pangram.com/).

Generates text using configured LLMs and checks whether Pangram's detector flags it as AI-written.

## Setup

```bash
uv sync
cp config.example.toml config.toml
# Edit config.toml with your Pangram API key and at least one LLM config
```

## Config

See `config.example.toml`. You need:
- A Pangram API key
- At least one LLM entry with `name`, `base_url`, `api_key`, and `model`

LLM entries should point to OpenAI-compatible `/v1/chat/completions` endpoints.

## Scripts

**Generate text and detect:**
```bash
uv run scripts/basic_prompt.py
uv run scripts/basic_prompt.py --prompt "Write about cats"
uv run scripts/basic_prompt.py --system "Write like a human blogger" --llm openai
```

**Detect arbitrary text:**
```bash
echo "some text to check" | uv run scripts/detect_text.py
uv run scripts/detect_text.py myfile.txt
```
