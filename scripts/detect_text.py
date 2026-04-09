"""Detect whether arbitrary text (from stdin or a file) is AI-generated."""
import argparse
import sys

from pangram_breaker.config import load_config
from pangram_breaker.detector import detect, print_result
from pangram_breaker.runlog import RunLog


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect AI-generated text via Pangram")
    parser.add_argument("file", nargs="?", help="File to read (default: stdin)")
    parser.add_argument("--config", default="config.toml", help="Config file path")
    args = parser.parse_args()

    cfg = load_config(args.config)
    log = RunLog("detect_text")

    if args.file:
        text = open(args.file).read()
        source = args.file
    else:
        text = sys.stdin.read()
        source = "stdin"

    if not text.strip():
        print("No text provided.", file=sys.stderr)
        sys.exit(1)

    input_step = log.log_text_input(text, source=source)
    print(f"Scanning {len(text)} chars...")
    result = detect(cfg.pangram_api_key, text)
    log.log_detection(result, source=f"Step {input_step} text ({source})")
    print_result(result)

    log.save()


if __name__ == "__main__":
    main()
