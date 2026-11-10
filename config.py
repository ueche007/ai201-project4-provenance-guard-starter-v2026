"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Input limits ────────────────────────────────────────────────────────────
# Anything longer is refused with a 413 before it reaches a model. 20,000
# characters is roughly 3,500 words: a long short story. The model only reads
# the first 400 tokens anyway, so longer text buys no accuracy, only cost.
MAX_TEXT_CHARS = 20_000

# Below this many words neither signal has enough to go on, so the label is
# always "unsure", whatever the score says. A short poem is legitimate writing,
# and a confident verdict on 30 words would be a guess dressed up as a finding.
MIN_WORDS_TO_JUDGE = 40

# An appeal's reasoning is for a person to read. 5,000 characters is plenty.
MAX_APPEAL_CHARS = 5_000


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# The rule lives in scoring.py::combine_signals: a 0.6 / 0.4 weighted average,
# and either signal can veto an AI verdict by scoring below VETO_BELOW.

WEIGHT_MODEL_SIGNAL = 0.6
WEIGHT_STYLE_SIGNAL = 0.4
VETO_BELOW = 0.5


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

#
# Mine (unit 7; unit 8 raised the AI line to 0.78, see below): below 0.45 is
# human, above 0.70 is AI, 0.45-0.70 is unsure. Set from 24
# calibration texts (README, "Signals and Scoring"): no human passage scored
# above 0.54, so 0.70 leaves a margin of 0.16 before anyone is accused. The
# rewritten AI pieces (0.53, 0.69) land in unsure, and that's the trade
# I chose: let some AI through rather than accuse a writer.

HUMAN_THRESHOLD = 0.45
# Unit 8 improvement: 0.70 -> 0.78. The attack run labelled four human pieces
# AI (formal, second-language, rubric essay, technical docs) at 0.750-0.776.
# 0.78 puts them in unsure. The cost: AI text scoring 0.70-0.78 is no longer
# called AI. README, "The Improvement".
AI_THRESHOLD = 0.78

# ⚠️ One thing that catches people out in Milestone 5. A weighted average can
# only land between its two inputs — so while `style_signal` is still the stub
# returning 0.5, the combined score can never leave 0.25–0.75 no matter what
# the model signal says, and the human label needs a model score below 0.20 to
# be reachable at all.
#
# If a label you can't reach is the problem, the fix is upstream of the
# thresholds: a style signal that actually varies. `scoring.label_ranges()`
# prints the bands; the reachable range is a different question.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# Off in unit 7. You turn it on and choose the numbers in unit 8, Milestone 1.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.

RATE_LIMITING_ENABLED = True

# Mine: 5 a minute, 50 a day, per creator_id (per address when there isn't
# one). A writer revising a piece sends a few a minute at most and nowhere near
# 50 a day. A script mapping my thresholds gets 50 probes a day per id.
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_DAY = 50

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
# Override with AI201_AUDIT_LOG to send test traffic somewhere other than the
# log you commit as evidence.
AUDIT_LOG = Path(os.getenv("AI201_AUDIT_LOG", str(LOG_DIR / "audit.jsonl")))
RESULTS_DIR = ROOT / "results"
