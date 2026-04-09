"""Generate text with each configured LLM and check if Pangram detects it."""
import argparse

from pangram_breaker.config import load_config
from pangram_breaker.detector import detect, print_result
from pangram_breaker.llm import chat
from pangram_breaker.runlog import RunLog

DEFAULT_PROMPT = "Write a short essay (200-300 words) about the impact of renewable energy on modern economies."


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LLM text and test Pangram detection")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Prompt to send to LLMs")
    parser.add_argument("--system", default=None, help="System prompt to use")
    parser.add_argument("--config", default="config.toml", help="Config file path")
    parser.add_argument("--llm", default=None, help="Name of a specific LLM to use (default: all)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    log = RunLog("basic_prompt")

    llms = cfg.llms
    if args.llm:
        llms = [l for l in llms if l.name == args.llm]
        if not llms:
            print(f"No LLM named '{args.llm}' found in config.")
            return

    for llm in llms:
        print(f"\n{'='*60}")
        print(f"LLM: {llm.name} ({llm.model})")
        print(f"{'='*60}")

        print(f"Prompt: {args.prompt[:80]}...")
        response = chat(llm, args.prompt, system=args.system)
        gen_step = log.log_llm_generation(llm, args.prompt, response, system=args.system)
        print(f"\n--- Generated text ({len(response)} chars) ---")
        print(response)

        print(f"\n--- Pangram detection ---")
        result = detect(cfg.pangram_api_key, response)
        log.log_detection(result, source=f"Step {gen_step} output ({llm.name}/{llm.model})")
        print_result(result)

    log.save()


if __name__ == "__main__":
    main()
