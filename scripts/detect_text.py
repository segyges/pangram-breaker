"""Detect whether arbitrary text (from stdin or a file) is AI-generated."""
import argparse
import sys

from pangram_breaker.config import load_config
from pangram_breaker.detector import detect, print_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect AI-generated text via Pangram")
    parser.add_argument("file", nargs="?", help="File to read (default: stdin)")
    parser.add_argument("--config", default="config.toml", help="Config file path")
    args = parser.parse_args()

    cfg = load_config(args.config)

    if args.file:
        text = open(args.file).read()
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("No text provided.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(text)} chars...")
    result = detect(cfg.pangram_api_key, text)
    print_result(result)


if __name__ == "__main__":
    main()
