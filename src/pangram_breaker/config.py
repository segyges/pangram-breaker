from __future__ import annotations

import sys
from pathlib import Path

import tomli
from pydantic import BaseModel, model_validator


class LLMConfig(BaseModel):
    name: str
    base_url: str
    api_key: str
    model: str


class Config(BaseModel):
    pangram_api_key: str
    llms: list[LLMConfig]

    @model_validator(mode="after")
    def _at_least_one_llm(self) -> Config:
        if len(self.llms) < 1:
            raise ValueError("At least one [[llm]] entry is required in the config")
        return self


def load_config(path: str | Path | None = None) -> Config:
    if path is None:
        path = Path("config.toml")
    path = Path(path)
    if not path.exists():
        print(f"Config file not found: {path}", file=sys.stderr)
        print("Copy config.example.toml to config.toml and fill in your keys.", file=sys.stderr)
        sys.exit(1)
    with open(path, "rb") as f:
        raw = tomli.load(f)
    return Config(
        pangram_api_key=raw["pangram"]["api_key"],
        llms=[LLMConfig(**entry) for entry in raw["llm"]],
    )
