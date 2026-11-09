"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

A scenario carries one of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
              A body given as a str is sent raw as the request body, for
              bodies that aren't a JSON object at all.

    "kind"    "label_sweep" or "appeals": checks that aren't a list of
              submissions. run_eval.py handles them itself.

Where the texts come from (none of them were used to tune the settings):

    my_writing/*.txt          criterion 1: my own writing. plain_* are the plain pieces.
    eval_texts/held_out.json  criteria 2-4: AI pieces and public-domain passages,
                              each with its source.
    samples/*.json            criterion 3: the instructor's three demo texts.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
DRAFT_MARK = "DRAFT - rewrite"


def _my_writing():
    """(file name, text) for each piece in my_writing/, in name order."""
    return [(p.name, p.read_text(encoding="utf-8").strip())
            for p in sorted((HERE / "my_writing").glob("*.txt"))]


def _held_out():
    return json.loads((HERE / "eval_texts" / "held_out.json").read_text(encoding="utf-8"))


def _sample(name):
    return json.loads((HERE / "samples" / f"{name}.json").read_text(encoding="utf-8"))["text"]


_MINE = _my_writing()
_HELD = _held_out()
_AI = [x["text"] for x in _HELD["clearly_ai"]]
_HUMAN = [x["text"] for x in _HELD["clearly_human"]]
_BORDER = [x["text"] for x in _HELD["borderline"]]

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Ten pieces I wrote. Criterion 1: at most 1 labelled AI in each trial,
        # and none of the plain_* pieces in any trial.
        "texts": [text for _, text in _MINE],
        "files": [name for name, _ in _MINE],
        "plain": [name.startswith("plain_") for name, _ in _MINE],
    },
    {
        "name": "clear AI",
        "criterion": 2,
        # Criterion 2: mean score of these five minus mean of "clear human" >= 0.25.
        "texts": _AI,
    },
    {
        "name": "clear human",
        "criterion": 2,
        "texts": _HUMAN,
    },
    {
        "name": "label sweep",
        "criterion": 3,
        # Criterion 3(a): 0.00 to 1.00 in steps of 0.01 through
        # scoring.score_to_label. Run in-process; nothing is sent.
        "kind": "label_sweep",
    },
    {
        "name": "label mix",
        "criterion": 3,
        # Criterion 3(b): 3 AI, 3 human, 3 borderline. Each label at least once.
        "texts": [_sample("clearly_ai"), _AI[0], _AI[1],
                  _sample("clearly_human"), _HUMAN[0], _HUMAN[1],
                  _sample("borderline"), _BORDER[0], _BORDER[1]],
        "groups": ["ai"] * 3 + ["human"] * 3 + ["borderline"] * 3,
    },
    {
        "name": "appeals",
        "criterion": 4,
        "kind": "appeals",
        # Criterion 4: 10 real appeals -> 200 and an appeal entry in the log;
        # 3 unknown content_ids -> 404 and no appeal entry; 3 empty reasonings -> 400.
        "texts": _AI + _HUMAN,
        "reasoning": "I wrote this myself, in my own words. Please have a person look at it.",
        "unknown_ids": ["c_000000000000", "c_doesnotexist", "not-a-content-id"],
        "empty_reasonings": ["", "   ", "\n\t"],
    },
    {
        "name": "bad input",
        "criterion": 5,
        # Criterion 5: the seven malformed requests it names. 0 return a 5xx,
        # each returns a 4xx with a JSON "error", and each leaves a "rejected"
        # entry in the log.
        "bodies": [
            {"creator_id": "eval_bad_notext"},                       # no text field
            {"text": "", "creator_id": "eval_bad_empty"},            # empty text
            {"text": "   \n\t  ", "creator_id": "eval_bad_space"},   # whitespace only
            {"text": None, "creator_id": "eval_bad_null"},           # text: null
            {"text": 12345, "creator_id": "eval_bad_number"},        # text as a number
            '["text", "creator_id"]',                                # not a JSON object
            {"text": "word " * 5000, "creator_id": "eval_bad_huge"}, # 25,000 characters
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        if scenario.get("kind") == "label_sweep":
            continue

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, (dict, str)):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict or a raw string — bodies "
                        f"are whole request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            name = (scenario.get("files") or [None] * len(texts))[j - 1] or f"text {j}"
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, {name} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), {name} is still "
                    f"the placeholder"
                )
            elif str(text).startswith(DRAFT_MARK):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), my_writing/{name} is "
                    f"still the AI draft. Rewrite it in your own words and delete "
                    f"the DRAFT line."
                )

    mine = SCENARIOS[0]
    if len(mine["texts"]) != 10 or sum(mine["plain"]) < 4:
        problems.append("criterion 1 needs 10 pieces in my_writing/, at least 4 named plain_*")
    return problems
