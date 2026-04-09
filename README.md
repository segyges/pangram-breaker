# pangram-breaker

Security research tool for testing AI-generated text detection via [Pangram](https://www.pangram.com/). The goal is to understand how well Pangram's detector identifies AI-written text under various generation strategies.

## Design

Each experiment is a standalone script in `scripts/`. Scripts read assignment prompts from text files in `inputs/` (one prompt per line), generate text via configured LLMs, and run the output through Pangram's detection API. Every run produces a markdown log in `logs/` that captures the full chat history, LLM configuration, and detection results with unambiguous step references.

To try a new approach, add a new script. To try new prompts, add a new input file. The shared library in `src/pangram_breaker/` handles config, LLM calls, Pangram detection, and logging so scripts stay short.

## Setup

```bash
uv sync
cp config.example.toml config.toml
# Edit config.toml with your Pangram API key and at least one LLM config
```

## Config

See `config.example.toml`. You need:
- A Pangram API key
- At least one `[[llm]]` entry with `name`, `base_url`, `api_key`, and `model`

LLM entries should point to OpenAI-compatible `/v1/chat/completions` endpoints (Anthropic's API supports this natively).

## Scripts

All scripts default to reading `inputs/basic_assignments.txt` and accept `--input`, `--config`, and `--llm` flags.

**`basic_prompt.py`** — Baseline: send each assignment to each LLM with a minimal no-filler system prompt and detect.

```bash
uv run scripts/basic_prompt.py
uv run scripts/basic_prompt.py --input inputs/other.txt --llm openai
```

**`styled_essay.py`** — Prompt engineering approach: uses a detailed system prompt that defines a persona (confident college junior with interests in rhetoric and prosody) and bans known LLM tells (em dashes, "not X but Y", triple lists, overused words like "delve" and "moreover").

```bash
uv run scripts/styled_essay.py
```

**`translate_roundtrip.py`** — Translation laundering: generates an essay, translates it to Spanish, translates it back to English, and detects at each stage.

```bash
uv run scripts/translate_roundtrip.py
```

**`run_assignments.py`** — Runs each assignment through all LLMs with a configurable `--system` prompt. Good for quick one-off tests of a new system prompt without writing a new script.

```bash
uv run scripts/run_assignments.py --system "Write as a bored teenager"
```

**`detect_text.py`** — Detect arbitrary text from a file or stdin, without any LLM generation.

```bash
echo "some text" | uv run scripts/detect_text.py
uv run scripts/detect_text.py myfile.txt
```

## Logs

Each run writes a markdown file to `logs/` named `YYYYMMDD_HHMMSS_<script>.md`. Logs contain:
- The exact command that was run
- Each step numbered sequentially (text input, LLM generation, detection)
- Full LLM config (name, model, base URL) for each generation step
- Complete chat messages (system + user prompts)
- Full response text
- Pangram results (prediction, fraction AI/assisted/human) with an explicit reference back to which step produced the text

## Extending

- **New strategy**: add a script to `scripts/` that imports from `pangram_breaker` and uses `RunLog` for logging.
- **New prompts**: add a text file to `inputs/`, one assignment per line.
- **New LLMs**: add another `[[llm]]` block to `config.toml`. All scripts iterate over every configured LLM by default.

## Results so far

All experiments tested with Claude Opus against realistic college essay assignments.

- **Baseline** (`basic_prompt.py`): 100% AI detected across all assignments.
- **Prompt engineering** (`styled_essay.py`): Persona + banned constructions + idiomatic style. Still 100% AI detected. The essays read more naturally but Pangram wasn't fooled.
- **Translation roundtrip** (`translate_roundtrip.py`): English → Spanish → English. 100% AI detected at every stage.
