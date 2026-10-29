#!/usr/bin/env python3
"""
Score the calibration set with both signals and write the table.

    python calibrate.py          # writes results/calibration.md

The set is calibration/texts.json: 16 human passages from public-domain books
on Project Gutenberg (written long before language models) and 8 AI-generated
pieces (4 typical, 2 plainly worded, 2 lightly hand-edited).

This is the evidence behind the weights, midpoints and thresholds in
config.py and stylometry.py. It is NOT an accuracy test: the settings were
tuned on these same texts, so of course they fit them. Unit 8's attack set
and your own writing are the real test.

Runs the signals directly, not through the service, and writes nothing to the
audit log.
"""

import json
import statistics
from collections import Counter

import config
import detector
import scoring
import stylometry


def main():
    texts = json.loads((config.ROOT / "calibration" / "texts.json").read_text(encoding="utf-8"))
    rows = []
    for item in texts:
        text = item["text"]
        model = detector.model_signal(text)
        style = stylometry.style_signal(text)
        combined = scoring.combine_signals(model, style)
        guess, _ = scoring.score_to_label(combined, word_count=len(stylometry.words(text)))
        rows.append({**item, "perplexity": round(detector.perplexity(text), 1),
                     "model": model, "style": style, "combined": combined, "guess": guess,
                     **stylometry.style_breakdown(text)["raw"]})

    lines = [
        "# Calibration run",
        "",
        "- Produced by: `calibrate.py::main` from `calibration/texts.json`",
        f"- Weights model {config.WEIGHT_MODEL_SIGNAL} / style {config.WEIGHT_STYLE_SIGNAL}, "
        f"veto below {config.VETO_BELOW}, thresholds human < {config.HUMAN_THRESHOLD}, "
        f"AI > {config.AI_THRESHOLD}",
        "- Tuned on these same texts, so this shows the settings fit, not that they generalise.",
        "",
        "| ID | Kind | Source | Perplexity | Sentence spread | Vocabulary (MATTR) | Punct /100w | model | style | combined | guess |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['kind']} | {r['source'].split(' (')[0]} | {r['perplexity']} | "
            f"{r['sentence_spread']:.3f} | {r['vocabulary']:.3f} | {r['punctuation']:.2f} | "
            f"{r['model']:.3f} | {r['style']:.3f} | {r['combined']:.3f} | {r['guess']} |"
        )

    counts = Counter((r["group"], r["guess"]) for r in rows)
    lines += ["", "## Summary", "", "| Group | human | unsure | ai | mean combined | range |",
              "|---|---|---|---|---|---|"]
    for group in ("human", "ai"):
        scores = [r["combined"] for r in rows if r["group"] == group]
        lines.append(f"| {group} | {counts[(group, 'human')]} | {counts[(group, 'unsure')]} | "
                     f"{counts[(group, 'ai')]} | {statistics.mean(scores):.3f} | "
                     f"{min(scores):.3f} – {max(scores):.3f} |")

    out = config.RESULTS_DIR / "calibration.md"
    config.RESULTS_DIR.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-4:]))
    print(f"\nWrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
