"""Generate an essay, translate to Spanish, translate back to English, and detect each stage."""
import argparse

from pangram_breaker.config import load_config
from pangram_breaker.detector import detect
from pangram_breaker.llm import chat
from pangram_breaker.runlog import RunLog

DEFAULT_INPUT = "inputs/basic_assignments.txt"
NO_FILLER = "Respond with only the requested text. No preamble, no titles, no commentary."


def main() -> None:
    parser = argparse.ArgumentParser(description="Essay → Spanish → English roundtrip with Pangram detection at each stage")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input file, one prompt per line")
    parser.add_argument("--system", default=NO_FILLER, help="System prompt")
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
            log = RunLog(f"translate_roundtrip_{i}_{llm.name}")

            print(f"\n{'#'*60}")
            print(f"Assignment {i}/{len(assignments)} — {llm.name} ({llm.model})")
            print(f"{'#'*60}")
            print(f"  {assignment[:100]}...")

            log.log_text_input(assignment, source=f"{args.input} (line {i})")

            # Stage 1: Generate essay
            print(f"\n  Stage 1: Generate essay")
            essay = chat(llm, assignment, system=args.system)
            s1 = log.log_llm_generation(llm, assignment, essay, system=args.system)
            print(f"    {len(essay)} chars")

            result1 = detect(cfg.pangram_api_key, essay)
            log.log_detection(result1, source=f"Step {s1} — original essay ({llm.name}/{llm.model})")
            print(f"    Detection: {result1.prediction_short} — AI {result1.fraction_ai:.0%}")

            # Stage 2: Translate to Spanish
            print(f"\n  Stage 2: Translate to Spanish")
            translate_prompt = f"Please translate this into idiomatic Spanish:\n\n{essay}"
            spanish = chat(llm, translate_prompt, system=args.system)
            s2 = log.log_llm_generation(llm, translate_prompt, spanish, system=args.system)
            print(f"    {len(spanish)} chars")

            result2 = detect(cfg.pangram_api_key, spanish)
            log.log_detection(result2, source=f"Step {s2} — Spanish translation ({llm.name}/{llm.model})")
            print(f"    Detection: {result2.prediction_short} — AI {result2.fraction_ai:.0%}")

            # Stage 3: Translate back to English
            print(f"\n  Stage 3: Translate back to English")
            back_prompt = f"Please translate this into idiomatic English:\n\n{spanish}"
            english = chat(llm, back_prompt, system=args.system)
            s3 = log.log_llm_generation(llm, back_prompt, english, system=args.system)
            print(f"    {len(english)} chars")

            result3 = detect(cfg.pangram_api_key, english)
            log.log_detection(result3, source=f"Step {s3} — English back-translation ({llm.name}/{llm.model})")
            print(f"    Detection: {result3.prediction_short} — AI {result3.fraction_ai:.0%}")

            # Summary
            print(f"\n  Summary:")
            print(f"    Original essay:    {result1.prediction_short} (AI {result1.fraction_ai:.0%} / Human {result1.fraction_human:.0%})")
            print(f"    Spanish:           {result2.prediction_short} (AI {result2.fraction_ai:.0%} / Human {result2.fraction_human:.0%})")
            print(f"    Back to English:   {result3.prediction_short} (AI {result3.fraction_ai:.0%} / Human {result3.fraction_human:.0%})")

            log.save()


if __name__ == "__main__":
    main()
