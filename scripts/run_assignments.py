"""Run each assignment prompt from an input file through every configured LLM and detect with Pangram."""
import argparse

from pangram_breaker.config import load_config
from pangram_breaker.detector import detect, print_result
from pangram_breaker.llm import chat
from pangram_breaker.runlog import RunLog

DEFAULT_INPUT = "inputs/basic_assignments.txt"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run assignment prompts through LLMs and detect with Pangram")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input file, one prompt per line")
    parser.add_argument("--system", default=None, help="System prompt to use")
    parser.add_argument("--config", default="config.toml", help="Config file path")
    parser.add_argument("--llm", default=None, help="Name of a specific LLM to use (default: all)")
    args = parser.parse_args()

    cfg = load_config(args.config)

    llms = cfg.llms
    if args.llm:
        llms = [l for l in llms if l.name == args.llm]
        if not llms:
            print(f"No LLM named '{args.llm}' found in config.")
            return

    with open(args.input) as f:
        assignments = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(assignments)} assignments from {args.input}")
    print(f"Running against {len(llms)} LLM(s)\n")

    for i, assignment in enumerate(assignments, 1):
        log = RunLog(f"assignment_{i}")

        print(f"\n{'#'*60}")
        print(f"Assignment {i}/{len(assignments)}")
        print(f"{'#'*60}")
        print(f"  {assignment[:100]}...")

        log.log_text_input(assignment, source=f"{args.input} (line {i})")

        for llm in llms:
            print(f"\n  LLM: {llm.name} ({llm.model})")

            response = chat(llm, assignment, system=args.system)
            gen_step = log.log_llm_generation(llm, assignment, response, system=args.system)
            print(f"    Generated {len(response)} chars")

            result = detect(cfg.pangram_api_key, response)
            log.log_detection(result, source=f"Step {gen_step} output ({llm.name}/{llm.model})")
            print(f"    Detection: {result.prediction_short} — AI {result.fraction_ai:.0%} / Human {result.fraction_human:.0%}")

        log.save()


if __name__ == "__main__":
    main()
