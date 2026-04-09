"""Generate text with each configured LLM and check if Pangram detects it."""
import argparse

from pangram_breaker.config import load_config
from pangram_breaker.detector import detect, print_result
from pangram_breaker.llm import chat
from pangram_breaker.runlog import RunLog

DEFAULT_INPUT = "inputs/basic_assignments.txt"
NO_FILLER = "Respond with only the requested text. No preamble, no titles, no commentary."


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LLM text and test Pangram detection")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input file, one prompt per line")
    parser.add_argument("--system", default=NO_FILLER, help="System prompt to use")
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
        for llm in llms:
            log = RunLog(f"basic_prompt_{i}_{llm.name}")

            print(f"\n{'='*60}")
            print(f"Assignment {i}/{len(assignments)} — {llm.name} ({llm.model})")
            print(f"{'='*60}")
            print(f"  {assignment[:100]}...")

            log.log_text_input(assignment, source=f"{args.input} (line {i})")

            response = chat(llm, assignment, system=args.system)
            gen_step = log.log_llm_generation(llm, assignment, response, system=args.system)
            print(f"\n--- Generated text ({len(response)} chars) ---")
            print(response)

            print(f"\n--- Pangram detection ---")
            result = detect(cfg.pangram_api_key, response)
            log.log_detection(result, source=f"Step {gen_step} output ({llm.name}/{llm.model})")
            print_result(result)

            log.save()


if __name__ == "__main__":
    main()
