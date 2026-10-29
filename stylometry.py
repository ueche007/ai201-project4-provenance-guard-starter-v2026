"""
Signal two: the style signal.

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import math
import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures ───────────────────────────────────────────────────────

# Punctuation that varies between writers. Full stops and plain commas are left
# out: almost everyone uses them at about the same rate, so they mostly measure
# sentence count. These are the marks people choose.
EXPRESSIVE_PUNCTUATION = set(";:!?()\"'\u2014\u2013\u2026\u2018\u2019\u201c\u201d")

# Window for the moving-average type-token ratio. See type_token_ratio.
TTR_WINDOW = 50


def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies, as a coefficient of variation.

    Returns:
        stdev(sentence lengths in words) / mean(sentence lengths). 0.0 means
        every sentence is the same length. Typical prose sits around 0.3-0.8.
        **Higher means more human** (lumpier).

    Fewer than two sentences has no spread to measure, so this returns 0.0, and
    `style_signal` treats that case as "no evidence" rather than as "perfectly
    even", which would otherwise read as very AI-like.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    return round(statistics.stdev(lengths) / mean, 4)


def type_token_ratio(text: str) -> float:
    """
    Vocabulary variety, as a moving-average type-token ratio (MATTR).

    Returns:
        A float between 0 and 1. **Higher means more varied vocabulary.**

    A plain type-token ratio falls as text gets longer, because common words
    repeat. So this slides a 50-word window across the text and averages the
    ratio inside each window. That makes a 100-word piece and a 400-word
    piece comparable. Texts shorter than the window fall back to the plain
    ratio, which is noisier and is one more reason short text is labelled
    "unsure" upstream.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    if len(tokens) <= TTR_WINDOW:
        return round(len(set(tokens)) / len(tokens), 4)
    ratios = [
        len(set(tokens[i:i + TTR_WINDOW])) / TTR_WINDOW
        for i in range(len(tokens) - TTR_WINDOW + 1)
    ]
    return round(statistics.mean(ratios), 4)


def punctuation_density(text: str) -> float:
    """
    Expressive punctuation per 100 words.

    Returns:
        A float, usually 0-15. Counts semicolons, colons, dashes, brackets,
        quotation marks, question and exclamation marks and ellipses: the marks
        a writer picks, not the full stops and commas everyone uses.

    Generated prose leans on full stops and commas; people use dialogue
    quotes, asides in brackets, questions and exclamations. **Higher leans
    more human.** But modern models love the em dash, and that cuts the other
    way, so this measure only nudges the score (weight 0.2).
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    count = sum(1 for ch in text if ch in EXPRESSIVE_PUNCTUATION)
    count += text.count("--") + text.count("...")   # typed dashes and ellipses
    return round(100 * count / len(tokens), 4)


# ── Combining them ───────────────────────────────────────────────────────────
#
# Each measure is turned into a 0-1 "AI-ness" with a logistic curve:
#     ai_ness = 1 / (1 + exp(direction * (value - midpoint) / spread))
# direction +1: a value BELOW the midpoint reads as more AI (spread, punctuation)
# direction -1: a value ABOVE the midpoint reads as more AI (vocabulary)
#
# The midpoints and directions came from running 24 calibration texts through
# the measures (16 public-domain human passages, 8 AI-written). See README,
# "Signals and Scoring". They are scoring decisions, not facts.
#
# Vocabulary runs the "wrong" way on purpose. On the calibration set the AI
# texts had MORE varied vocabulary in each 50-word window than the human
# passages, not less. It's also the safer direction: plain human writing has
# low variety, and "low variety = AI" would push exactly those writers toward
# an accusation.

STYLE_PARAMS = {
    # measure:            (midpoint, spread, direction, weight)
    "sentence_spread":    (0.42, 0.08, +1, 0.60),
    "vocabulary":         (0.82, 0.04, -1, 0.20),
    "punctuation":        (1.50, 0.70, +1, 0.20),
}


def _ai_ness(value: float, midpoint: float, spread: float, direction: int) -> float:
    return 1.0 / (1.0 + math.exp(direction * (value - midpoint) / spread))


def style_breakdown(text: str) -> dict:
    """The three raw measures and their 0-1 AI-ness. Handy for debugging."""
    n_sentences = len(sentences(text))
    raw = {
        "sentence_spread": sentence_length_spread(text),
        "vocabulary": type_token_ratio(text),
        "punctuation": punctuation_density(text),
    }
    parts = {}
    for name, value in raw.items():
        midpoint, spread, direction, _ = STYLE_PARAMS[name]
        if name == "sentence_spread" and n_sentences < 2:
            parts[name] = None          # no evidence either way
        elif name == "vocabulary" and len(words(text)) < TTR_WINDOW:
            parts[name] = None          # short text inflates the ratio
        else:
            parts[name] = round(_ai_ness(value, midpoint, spread, direction), 4)
    return {"raw": raw, "ai_ness": parts}


def style_signal(text: str) -> float:
    """
    The style signal as a 0-1 score. **Higher means more likely AI.**

    A weighted average of the three measures' AI-ness: sentence spread 0.6,
    vocabulary 0.2, punctuation 0.2. Sentence spread gets the most because it
    separated the calibration texts cleanly (AI 0.24-0.42, human 0.45-1.05).
    The other two overlap between groups, so they only nudge.

    A measure with no evidence (sentence spread on a one-sentence text,
    vocabulary on fewer than 50 words) drops out and the remaining weights are rescaled. If nothing is left, 0.5.
    """
    parts = style_breakdown(text)["ai_ness"]
    total = weight_sum = 0.0
    for name, ai_ness in parts.items():
        if ai_ness is None:
            continue
        weight = STYLE_PARAMS[name][3]
        total += weight * ai_ness
        weight_sum += weight
    if weight_sum == 0:
        return 0.5
    return round(min(max(total / weight_sum, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print(f"per-measure AI-ness      {style_breakdown(text)['ai_ness']}")
