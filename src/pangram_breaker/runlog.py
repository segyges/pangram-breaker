from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from pangram_breaker.config import LLMConfig
from pangram_breaker.detector import DetectionResult

LOGS_DIR = Path("logs")


class RunLog:
    def __init__(self, script_name: str) -> None:
        self._lines: list[str] = []
        self._step = 0
        self._ts = datetime.now(timezone.utc)
        self._script = script_name

        self._lines.append(f"# Run: {script_name}")
        self._lines.append(f"**Date:** {self._ts.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self._lines.append(f"**Command:** `{' '.join(sys.argv)}`")
        self._lines.append("")

    def _next_step(self, title: str) -> int:
        self._step += 1
        self._lines.append("---")
        self._lines.append("")
        self._lines.append(f"## Step {self._step}: {title}")
        self._lines.append("")
        return self._step

    def log_llm_generation(
        self,
        llm: LLMConfig,
        prompt: str,
        response: str,
        system: str | None = None,
    ) -> int:
        step = self._next_step(f"LLM Generation — {llm.name} ({llm.model})")

        self._lines.append("### Configuration")
        self._lines.append("")
        self._lines.append("| Field | Value |")
        self._lines.append("|-------|-------|")
        self._lines.append(f"| Name | {llm.name} |")
        self._lines.append(f"| Model | {llm.model} |")
        self._lines.append(f"| Base URL | {llm.base_url} |")
        self._lines.append("")

        self._lines.append("### Chat Messages")
        self._lines.append("")
        if system:
            self._lines.append("**System:**")
            self._lines.append("")
            self._lines.append(_quote(system))
            self._lines.append("")
        self._lines.append("**User:**")
        self._lines.append("")
        self._lines.append(_quote(prompt))
        self._lines.append("")

        self._lines.append(f"### Response ({len(response)} chars)")
        self._lines.append("")
        self._lines.append(_quote(response))
        self._lines.append("")

        return step

    def log_detection(
        self,
        result: DetectionResult,
        source: str,
    ) -> int:
        step = self._next_step(f"Pangram Detection")

        self._lines.append(f"**Source:** {source}")
        self._lines.append("")
        self._lines.append("| Metric | Value |")
        self._lines.append("|--------|-------|")
        self._lines.append(f"| Headline | {result.headline} |")
        self._lines.append(f"| Prediction | {result.prediction_short} — {result.prediction} |")
        self._lines.append(f"| Fraction AI | {result.fraction_ai:.1%} |")
        self._lines.append(f"| Fraction Assisted | {result.fraction_ai_assisted:.1%} |")
        self._lines.append(f"| Fraction Human | {result.fraction_human:.1%} |")
        self._lines.append("")

        return step

    def log_text_input(self, text: str, source: str) -> int:
        step = self._next_step(f"Text Input")

        self._lines.append(f"**Source:** {source}")
        self._lines.append(f"**Length:** {len(text)} chars")
        self._lines.append("")
        self._lines.append(_quote(text))
        self._lines.append("")

        return step

    def save(self) -> Path:
        LOGS_DIR.mkdir(exist_ok=True)
        slug = self._script.replace(" ", "_").replace("/", "_")
        filename = f"{self._ts.strftime('%Y%m%d_%H%M%S')}_{slug}.md"
        path = LOGS_DIR / filename
        path.write_text("\n".join(self._lines))
        print(f"\nLog saved: {path}")
        return path


def _quote(text: str) -> str:
    lines = text.splitlines() or [""]
    return "\n".join(f"> {line}" for line in lines)
