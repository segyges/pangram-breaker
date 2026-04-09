from __future__ import annotations

from dataclasses import dataclass

from pangram import Pangram


@dataclass
class DetectionResult:
    prediction: str
    prediction_short: str
    fraction_ai: float
    fraction_ai_assisted: float
    fraction_human: float
    headline: str
    raw: dict


def detect(api_key: str, text: str) -> DetectionResult:
    client = Pangram(api_key=api_key)
    result = client.predict(text)
    return DetectionResult(
        prediction=result.get("prediction", ""),
        prediction_short=result.get("prediction_short", ""),
        fraction_ai=result.get("fraction_ai", 0.0),
        fraction_ai_assisted=result.get("fraction_ai_assisted", 0.0),
        fraction_human=result.get("fraction_human", 0.0),
        headline=result.get("headline", ""),
        raw=result,
    )


def print_result(result: DetectionResult) -> None:
    print(f"  Headline:     {result.headline}")
    print(f"  Prediction:   {result.prediction_short} — {result.prediction}")
    print(f"  Fraction AI:  {result.fraction_ai:.1%}")
    print(f"  Fraction Assisted: {result.fraction_ai_assisted:.1%}")
    print(f"  Fraction Human:    {result.fraction_human:.1%}")
