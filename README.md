# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

A writing site sends Provenance Guard a piece of text. It sends back a guess
about whether AI wrote it, a score, and a sentence a reader can understand,
and it gives the writer a way to say "you got this wrong".

1. **Arrive.** `POST /submit` gets JSON: `text` and `creator_id`
   (`app.py::submit`).
2. **Check the input.** Missing, empty, non-string or over-long text, a missing
   `creator_id`, or a body that isn't a JSON object is refused with a 4xx and a
   reason (Step 2 in `app.py::submit`, plus `_check_submission`), and `submit` writes the refusal to
   the audit log. Nothing malformed reaches a model. The one refusal that
   happens after the model is text under 3 tokens, which the detector can't
   score: that gets a 400 `too_short`, also logged.
3. **Signal one.** gpt2, running locally, measures how predictable the text
   is (perplexity), squashed to 0–1 where higher means more AI-like
   (`detector.py::model_signal`).
4. **Signal two.** The shape of the text: how much sentence length varies,
   how varied the vocabulary is, how much expressive punctuation it uses,
   combined to 0–1, higher meaning more AI-like
   (`stylometry.py::style_signal`).
5. **Combine.** A 0.6 / 0.4 weighted average where either signal can veto an
   AI verdict (`scoring.py::combine_signals`).
6. **Label.** The score maps to one of three labels written for a reader.
   Text under 40 words is always "unsure" (`scoring.py::score_to_label`).
7. **Log and answer.** The decision, both signal scores, the combined score
   and the label go to `logs/audit.jsonl`. The response carries `content_id`,
   `guess`, `confidence`, `label`, `model_score` and `style_score`. If the
   writer disagrees, `POST /appeal` with that `content_id` moves the item to
   `under_review` and records their reasoning (`app.py::appeal`).

`confidence` is the combined score: 0 means confidently human, 1 means
confidently AI, and the middle means the system isn't sure.

**Stretch feature added:** `GET /content/<id>` returns one item's current
status, label, signal scores and any appeals (`app.py::content_status`).

---

## Signals and Scoring

Measured numbers below come from `results/calibration.md`, produced by
`python calibrate.py` from `calibration/texts.json`, except the Grimm sample
scores, which come from the Sample Run (`logs/audit.jsonl`). Weights,
thresholds and midpoints are settings in `config.py` and `stylometry.py`. The
calibration set is 16 passages from public-domain books on Project Gutenberg
(written long before language models existed) and 8 AI-generated pieces: 4
typical, 2 plainly worded, and 2 rewrites of typical pieces into a casual
voice (`ai_7` rewrites `ai_1`, `ai_8` rewrites `ai_2`). **I tuned the settings on these same texts, so the
results show the settings fit, not that they work on new writing.**

### Signal one — the model signal

**What it measures:** how predictable the text is to gpt2 (perplexity over the
first 400 tokens), mapped to 0–1 by a logistic curve centred at perplexity 45.
Low perplexity gives a high score (more AI-like). I left the starter's
midpoint as it was.

**Why that might differ between human and AI writing:** a language model writes
by picking likely next words, so its output is text a model finds easy to
predict. On the calibration set the typical AI pieces had perplexity 7.4–21.6;
the human passages 22.3–96.4.

**What it can't see:** who wrote the text. It rewards common words in ordinary
sentences, and plenty of people write that way. The plain human passages
(Grimm's fairy tales, *The Wizard of Oz*) scored 0.65–0.76 on this signal,
higher than one of my lightly edited AI pieces (0.435). Writers using a
second language, younger writers, and anyone writing plainly on purpose
will read as machine-like here. Famous text also reads as predictable,
because the model may have seen it in training. It also only reads the first
400 tokens.

### Signal two — the style signal

**What it measures:** three things about the text's shape, none of which needs
to understand a word (`stylometry.py`):

| Measure | How | Reads as AI when | Weight |
|---|---|---|---|
| Sentence-length spread | stdev ÷ mean of words per sentence | low (below 0.42) | 0.6 |
| Vocabulary variety | moving-average type-token ratio, 50-word window | high (above 0.82) | 0.2 |
| Expressive punctuation | `; : ! ? ( ) " ' — – …`, curly quotes, and typed `--` / `...`, per 100 words | low (below 1.5) | 0.2 |

Each goes through a logistic curve to 0–1 and the weighted average is the
signal. A measure with no evidence drops out: spread on a one-sentence text,
vocabulary on under 50 words. Apostrophes count as punctuation, so
contractions (*don't*, *it's*) nudge a text toward human.

**Why that might differ between human and AI writing:** generated prose marches
in even, mid-length sentences. The AI pieces' spread was 0.24–0.42 and the
human passages' 0.45–1.05, the cleanest split of anything I measured. People
also use dialogue, asides, questions and exclamations; the AI pieces mostly
used none.

Vocabulary runs the opposite way from what I expected. On average the AI
pieces had *more* varied vocabulary per 50 words (mean 0.853, range
0.71–0.94) than the human passages (mean 0.798, range 0.74–0.85), so above
the midpoint reads as AI. It's also the safer direction,
because plain human writing has low variety, and "low variety means AI" would
push exactly those writers toward an accusation. It gets only 0.2 weight
because the groups overlap.

**What it can't see:** what the text says. Anything that changes the shape
without changing the substance moves it: breaking long sentences up, adding
a quotation, sprinkling in dashes and exclamation marks. `ai_8` is a casual
rewrite of `ai_2`, the same points in the same order with shorter sentences,
a question, an exclamation, a dash and a colon. Its style score fell from
0.88 to 0.50 (its model score fell less, 0.95 to 0.82). My human set is
also mostly 19th-century fiction full of dialogue, which favours this signal.
Modern plain human writing such as emails and essays is under-represented,
and I expect it to score higher.

### The combining rule

**The rule:** take a weighted average, 0.6 for the model signal and 0.4 for
the style signal. Then, **if either signal is below 0.5 (leans human), cap the
result at 0.69**, just under the AI threshold. Accusing someone needs both
signals to agree. Calling something human doesn't, because a missed AI piece
costs the site little and a wrong accusation costs a writer a lot.

**The numbers:** `WEIGHT_MODEL_SIGNAL = 0.6`, `WEIGHT_STYLE_SIGNAL = 0.4`,
`VETO_BELOW = 0.5` (`config.py`); the cap is `AI_THRESHOLD - 0.01` = 0.69
(`scoring.py::combine_signals`). The model
signal weighs more because it reads the text, while the style signal is the
easier one to game. The veto is what stops the model signal's blind spot
from becoming an accusation.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:**

- **Plain human writing (the Grimm passage in the Sample Run below):** model
  0.7526 (AI-like), style 0.3435 (human-like). The weighted average is 0.589,
  which is "unsure". The style signal also vetoes an AI verdict, so even
  a stronger model score couldn't push this past 0.69. Without the veto, a
  model score of 0.95 with this style score would give 0.707, an accusation.
- **Rewritten AI (`ai_8` in `results/calibration.md`):** model 0.823,
  style 0.497. The average is about 0.693 and the veto caps it at 0.690, so the
  label is "unsure". That's AI text getting through, which is the trade
  I chose.

---

## Label Variants

Thresholds are `HUMAN_THRESHOLD = 0.45` and `AI_THRESHOLD = 0.70`
(`config.py`). The bands are half-open, so every score from 0.00 to 1.00 maps to
exactly one label; a sweep of `score_to_label(i / 100)` for i = 0…100 gave 45
human, 26 unsure, 30 AI, 101 of 101 mapped. Scores are rounded to 4 decimals
before comparing, so floating-point noise like 0.7000000000000001 can't cross
a line. Text under 40 words gets the unsure label whatever it scores.

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 to under 0.45 | This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI. |
| unsure | 0.45 to 0.70 (and any text under 40 words) | We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it. |
| high-confidence AI | over 0.70 to 1.00 | This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it. |

On the calibration set: human passages 11 human, 5 unsure, 0 AI; AI pieces
6 AI, 2 unsure, 0 human. Every human passage scored 0.538 or lower, so the
nearest one sits 0.16 below the AI line.

**Why I worded the "unsure" one this way:** the person reading it probably
wrote every word. So it says plainly that no call is being made, that this
result is common for real writers, and that nothing happens because of it.
It names *plain* writing on purpose: that's who this system is most likely to
put here, and they should hear that it isn't a mark against them. It says
nothing about AI being "possible", because that is an accusation.

---

## Sample Run

The text is from *Grimm's Fairy Tales* (Project Gutenberg #2591), so a person
wrote it. It's plain, long-sentenced storytelling, the kind of writing signal
one reads as machine-like. It's the first three sentences of calibration
passage `human_8`, so the settings were tuned on it. The full passage scored
0.470; this shorter cut scored 0.589. Responses pretty-printed with `python -m json.tool`.

**A submission**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "And when the time came for him to go home, he had bought pearls and jewels for the two eldest, but he had sought everywhere in vain for the rose; and when he went into any garden and asked for such a thing, the people laughed at him, and asked him whether he thought roses grew in snow. This grieved him very much, for Lily was his dearest child; and as he was journeying home, thinking what he should bring her, he came to a fine castle; and around the castle was a garden, in one half of which it seemed to be summer-time and in the other half winter. On one side the finest flowers were in full bloom, and on the other everything looked dreary and buried in the snow.", "creator_id": "writer_lily"}'
```

```json
{
    "confidence": 0.589,
    "content_id": "34a309e5c322",
    "guess": "unsure",
    "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
    "model_score": 0.7526,
    "status": "decided",
    "style_score": 0.3435
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "34a309e5c322", "reasoning": "This passage is from Grimm'"'"'s Fairy Tales, translated in the 1800s. No machine wrote it. The sentences are long and plain because that is how the story is told."}'
```

```json
{
    "appeal_recorded_at": "2026-10-29T00:22:05+00:00",
    "content_id": "34a309e5c322",
    "message": "Thanks, we've got your appeal. A person will review this piece. Until then it's marked as under review, not as AI-generated.",
    "previous_guess": "unsure",
    "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
    "count": 2,
    "entries": [
        {
            "combined_score": 0.589,
            "content_id": "34a309e5c322",
            "creator_id": "writer_lily",
            "guess": "unsure",
            "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
            "model_score": 0.7526,
            "status": "decided",
            "style_score": 0.3435,
            "timestamp": "2026-10-29T00:22:00+00:00",
            "word_count": 133
        },
        {
            "content_id": "34a309e5c322",
            "creator_id": "writer_lily",
            "event": "appeal",
            "reasoning": "This passage is from Grimm's Fairy Tales, translated in the 1800s. No machine wrote it. The sentences are long and plain because that is how the story is told.",
            "status": "under_review",
            "timestamp": "2026-10-29T00:22:05+00:00"
        }
    ]
}
```

The original decision stays in the log unchanged; the appeal is appended after
it with `status: under_review`. `GET /content/34a309e5c322` now reports
`"status": "under_review"`.

---

## How I Used AI

**Moment 1 — debugging `/submit`**

- *What I asked for:* after adding the code Fahad shared, I couldn't figure
  out the bug, so I asked Claude to help debug it.
- *What came back:* the bug was `text = payload.get("text")` straight after
  reading the body. When the body isn't a JSON object (plain text, a list, a
  number), `payload` has no `.get`, so `/submit` crashed with a 500 and left
  nothing in the audit log. The fix is an `isinstance(payload, dict)` check
  before Step 2, plus `test_bad_bodies.py`, which fails 6 of 6 on the buggy
  version and passes 6 of 6 on the fixed one.
- *What I changed:* after Claude helped debug it, I kept the changes: the
  check in front of Step 2 and the regression test.

**Moment 2 — the borderline sample**

- *What I asked for:* I gave Claude the instructor's three demo texts from
  class and asked it to set them up as JSON files in `samples/`.
- *What came back:* three sample files, but the screenshot had cut off the
  first sample's name, and Claude guessed it was "lightly edited AI".
- *What I changed:* I pointed out it was the "borderline" sample and had it
  renamed to `borderline.json`. Running it showed my system labels the
  borderline text **human** (score 0.348), not unsure. It makes the same
  points as `clearly_ai.json` (0.702), but in a casual voice, and that alone
  moved it across two labels. That's the style signal's blind spot, and I'm
  keeping it as a test case for unit 8.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day (`config.py`, `RATE_LIMIT_PER_MINUTE`
and `RATE_LIMIT_PER_DAY`)

**Why those numbers and not others:**
A writer checking their own work sends a piece, reads the answer, edits and
sends it again. That's a few submissions a minute at most, and even a long
editing session doesn't come near 50 in a day. A script trying to map my
thresholds needs hundreds of small variations. At 5 a minute and 50 a day,
one creator_id gets 50 probes a day, not a thousand. I didn't keep the
starter's 10/minute and 200/day because 200 probes a day is enough to find
my 0.45 and 0.70 thresholds in an afternoon. I didn't go lower than 5 a
minute because someone pasting several short pieces in a row would hit the
limit while using the site normally.

**What a caller counts as:** the `creator_id` in the request, falling back
to the caller's address when there isn't a usable one
(`app.py::rate_limit_key`). That has two weak spots:

- A script can make up a new `creator_id` for every request, and each new id
  gets its own fresh 5 and 50. A per-creator limit only stops a caller who
  keeps the same name.
- Anyone can send someone else's `creator_id` and use up that writer's
  allowance for the day, locking them out.

Malformed requests with no `creator_id` all count against one address, so
on my laptop they share a single allowance.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15` (15 submissions as `flood_tester`,
`results/flood_2026-11-08_2101.md`):

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

All 10 rejections are in `logs/audit.jsonl`, for example:

```json
{"timestamp": "2026-11-09T02:01:38+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

---

## Attack Run — Before

`python run_attacks.py --set attack_set --label before`, 56 attacks, written
to `results/attack_run_2026-11-08_2102_before.md` by `run_attacks.py::main`.
Nothing crashed: no 5xx, and every row came back with a status.

**How I marked them.** My labels are human below 0.45, AI above 0.70, unsure
in between, and always unsure under 40 words.

- **Evasion**, and the three prompt injections that wrap AI text (PI01–PI03):
  the text is AI-written, so it **held** only if it was labelled AI. Unsure
  counts as **broke**, because the text got through without being called AI.
- **False positive**, and PI06 (an instruction plus real human writing): the
  text is human, so it **broke** only if it was labelled AI.
- **PI04 and PI05** aim at the label text and the audit log, not the score.
  They held if neither was changed.
- **Malformed**: held if the service refused it with a 4xx and a JSON error,
  or answered without an AI label. A 5xx would be broke; there were none.
- **Flood**: held if the requests over my limit got a 429.

RQ10 and RQ11 came back 429 and never reached my route. They have no usable
`creator_id`, so they counted against my address, which earlier malformed
rows in the same minute had used up. I marked them *not reached* rather than
held. Sent again on their own, both got a 400 from the route
(`results/attack_run_2026-11-08_2103_retry_RQ10.md` and `_RQ11.md`).

| ID | Family | Targeting | Status | Guess | Score | Model | Style | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.4768 | 0.1635 | 0.9468 | **BROKE** |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | human | 0.4326 | 0.5943 | 0.1901 | **BROKE** |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.5791 | 0.6662 | 0.4485 | **BROKE** |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | ai | 0.7441 | 0.6114 | 0.9431 | **HELD** |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.3084 | 0.3212 | 0.2891 | **BROKE** |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.4691 | 0.5727 | 0.3136 | **BROKE** |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.4825 | 0.5862 | 0.327 | **BROKE** |  |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.4909 | 0.2452 | 0.8594 | **BROKE** | under 40 words, so always unsure by design |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.5873 | 0.7042 | 0.412 | **BROKE** |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.7985 | 0.9792 | 0.5275 | **HELD** |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.5677 | 0.6175 | 0.493 | **HELD** |  |
| FP02 | false_positive | human writing in a formal register | 200 | ai | 0.7495 | 0.7387 | 0.7658 | **BROKE** |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | ai | 0.7765 | 0.8051 | 0.7337 | **BROKE** |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | ai | 0.7705 | 0.8329 | 0.6768 | **BROKE** |  |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.7581 | 0.8005 | 0.6946 | **BROKE** |  |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.6677 | 0.8814 | 0.3472 | **HELD** |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | unsure | 0.6054 | 0.8816 | 0.1912 | **HELD** |  |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.4207 | 0.3223 | 0.5684 | **HELD** |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | human | 0.3808 | 0.4625 | 0.2582 | **BROKE** |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.1646 | 0.2044 | 0.1049 | **BROKE** |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.6049 | 0.5943 | 0.6207 | **BROKE** |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.4957 | 0.4998 | 0.4896 | **HELD** | label is my fixed text; nothing from the input is echoed |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.4875 | 0.6401 | 0.2585 | **HELD** | text isn't written to the log; the fake fields never appear |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.5439 | 0.5583 | 0.5224 | **HELD** |  |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | **HELD** |  |
| MF02 | malformed | text is a single character | 400 | — | — | — | — | **HELD** |  |
| MF03 | malformed | text is control characters | 200 | unsure | 0.358 | 0.0 | 0.895 | **HELD** |  |
| MF04 | malformed | text is only punctuation | 200 | unsure | 0.3647 | 0.0112 | 0.895 | **HELD** |  |
| MF05 | malformed | text is a very long single word | 200 | unsure | 0.9566 | 0.9976 | 0.895 | **HELD** | label held only by the 40-word floor; combined score 0.957 |
| MF06 | malformed | text is emoji only | 200 | unsure | 0.9561 | 0.9969 | 0.895 | **HELD** | label held only by the 40-word floor; combined score 0.956 |
| MF07 | malformed | text is right-to-left script | 200 | unsure | 0.9018 | 0.9064 | 0.895 | **HELD** | label held only by the word floor (word_count 0); combined 0.902 |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | **HELD** |  |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | **HELD** |  |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | **HELD** |  |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | **HELD** |  |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | **HELD** |  |
| RQ05 | malformed | text is null | 400 | — | — | — | — | **HELD** |  |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | **HELD** |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | **HELD** |  |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | **HELD** |  |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | **HELD** |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | — | — | **NOT REACHED** | never reached the route: shared-address limit. Re-sent alone: 400 |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | — | — | **NOT REACHED** | never reached the route: shared-address limit. Re-sent alone: 400 |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | **HELD** |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.3752 | 0.0287 | 0.895 | **HELD** |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.3752 | 0.0287 | 0.895 | **HELD** |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.3752 | 0.0287 | 0.895 | **HELD** |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.3752 | 0.0287 | 0.895 | **HELD** |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.3752 | 0.0287 | 0.895 | **HELD** |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** |  |

| Family | Attacks | Held | Broke | Not reached |
|---|---|---|---|---|
| evasion | 10 | 2 | 8 | 0 |
| false_positive | 8 | 4 | 4 | 0 |
| prompt_injection | 6 | 3 | 3 | 0 |
| malformed | 20 | 18 | 0 | 2 |
| flood_same_creator | 12 | 12 | 0 | 0 |
| **All** | **56** | **39** | **15** | **2** |

**Ten audit log entries from the run** (verbatim from `logs/audit.jsonl`):

1. FP03, a non-native English speaker writing carefully, labelled AI.
2. FP05, technical documentation written by a person, labelled AI.
3. EV02, AI text with "Really." between sentences, labelled **human**.
4. PI02, AI text under a fake "SYSTEM:" line, labelled human at 0.165.
5. EV01, AI text with typos. Signal one dropped to 0.16 and vetoed the AI
   call, while signal two stayed at 0.95.
6. MF07, Arabic text: combined 0.902 and `word_count` 0. Only the word floor
   kept it out of the AI label.
7. MF05, one 4,000-character word: combined 0.957, held only by the word floor.
8. PI05, a log injection attempt. The fake `"guess": "human"` and
   `"combined_score": 0.01` in its text never reach the log, because the log
   doesn't store the text.
9. FL01, a rejected request: one of the 7 flood rows over my limit.
10. RQ10 or RQ11, a rejected request: a malformed row that hit the shared
    address limit. Its `creator_id` is `unknown`, and nothing in the entry
    says which request it was.

```json
{"timestamp": "2026-11-09T02:02:33+00:00", "content_id": "c_735bd2772d77", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.7337, "combined_score": 0.7765, "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.", "status": "decided", "word_count": 83}
{"timestamp": "2026-11-09T02:02:33+00:00", "content_id": "c_673630789cea", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.6946, "combined_score": 0.7581, "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.", "status": "decided", "word_count": 70}
{"timestamp": "2026-11-09T02:02:33+00:00", "content_id": "c_dac5af663c5a", "creator_id": "attacker_EV02", "guess": "human", "model_score": 0.5943, "style_score": 0.1901, "combined_score": 0.4326, "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.", "status": "decided", "word_count": 91}
{"timestamp": "2026-11-09T02:02:33+00:00", "content_id": "c_e901ed857910", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.1049, "combined_score": 0.1646, "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.", "status": "decided", "word_count": 45}
{"timestamp": "2026-11-09T02:02:32+00:00", "content_id": "c_eae485952bfe", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.9468, "combined_score": 0.4768, "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.", "status": "decided", "word_count": 85}
{"timestamp": "2026-11-09T02:02:34+00:00", "content_id": "c_e8f14f1624e7", "creator_id": "attacker_MF07", "guess": "unsure", "model_score": 0.9064, "style_score": 0.895, "combined_score": 0.9018, "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.", "status": "decided", "word_count": 0}
{"timestamp": "2026-11-09T02:02:34+00:00", "content_id": "c_5f737ca74917", "creator_id": "attacker_MF05", "guess": "unsure", "model_score": 0.9976, "style_score": 0.895, "combined_score": 0.9566, "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.", "status": "decided", "word_count": 1}
{"timestamp": "2026-11-09T02:02:33+00:00", "content_id": "c_1a21900a6bb2", "creator_id": "attacker_PI05", "guess": "unsure", "model_score": 0.6401, "style_score": 0.2585, "combined_score": 0.4875, "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.", "status": "decided", "word_count": 30}
{"timestamp": "2026-11-09T02:02:34+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
{"timestamp": "2026-11-09T02:02:34+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

FP03. A person writing carefully in their second language about their first
month in a new country got "This piece shows strong signs of being generated
by AI" at 0.7765. Both signals agreed (model 0.8051, style 0.7337), so my
veto, which only steps in when the signals disagree, did nothing. Short
sentences and common words are exactly how a careful second-language writer
writes, and that person has the least room to argue back. Criterion 1 named
this person before I built anything.

---

## Run Log and Verdicts

`python run_eval.py --label before`, written to `results/run_2026-11-09_2239_before.md`. The inputs are in
`scenarios.py`: my own writing in `my_writing/` (criterion 1), held-out texts
in `eval_texts/held_out.json` that weren't used to tune anything
(criteria 2-4), and the instructor's samples. Each Run cell is the number
`run_eval.py::measure` worked out for that trial. A verdict is MET only if
the target held in all three trials.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing called AI | ≤ 1 of 10 labelled AI, 0 of 4 plain, every trial | 0/10 AI, 0/4 plain | 0/10 AI, 0/4 plain | 0/10 AI, 0/4 plain | MET |
| 2. AI and human scores far apart | mean AI − mean human ≥ 0.25, every trial | 0.871 − 0.349 = 0.522 | 0.871 − 0.349 = 0.522 | 0.871 − 0.349 = 0.522 | MET |
| 3. All three labels reachable, no gaps | (a) 101/101 map to one label; (b) 3/3 labels seen, every trial | (a) 101/101; (b) 3/3 (ai, human, unsure) | (a) 101/101; (b) 3/3 (ai, human, unsure) | (a) 101/101; (b) 3/3 (ai, human, unsure) | MET |
| 4. Appeals recorded; bad ones refused | 10/10 appeals recorded; 3/3 unknown → 404, no entry; 3/3 empty → 400 | 10/10, 3/3, 3/3 | 10/10, 3/3, 3/3 | 10/10, 3/3, 3/3 | MET |
| 5. Bad input never crashes | 7/7: no 5xx, 4xx with JSON error, rejected entry logged | 7/7 no 5xx, 7/7 4xx+error, 7/7 logged | 7/7 no 5xx, 7/7 4xx+error, 7/7 logged | 7/7 no 5xx, 7/7 4xx+error, 7/7 logged | MET |

**How I decided each verdict.** I compared each trial's number with the
target in `criteria.md`, without rounding in my favour.

1. **MET.** 0 of 10 pieces labelled AI in every trial, against a limit of
   1, and none of the 4 plain pieces. It was close: `plain_04_my_dog` scored
   0.6958, 0.004 below my AI threshold of 0.70.
2. **MET.** The AI set averaged 0.871 and the human set 0.349, a gap of
   0.522 against a target of 0.25, in every trial.
3. **MET.** (a) All 101 swept scores mapped to exactly one label. (b) The
   9-piece set produced all three labels in every trial. "Unsure" came from
   only one piece, though: the formal Federalist passage (0.6075). The other
   two borderline pieces, including the AI piece rewritten in a casual voice,
   were labelled human.
4. **MET.** 10/10 appeals returned 200 and left an `appeal` entry with the
   reasoning and `status: under_review`. 3/3 unknown ids returned 404 with no
   appeal entry. 3/3 empty reasonings returned 400.
5. **MET.** All 7 malformed requests returned a 4xx with a JSON `error`
   field, and each left a `rejected` entry in the log, read back by
   `run_eval.py::submit_and_record`.

All three trials returned identical scores for every input. Neither signal
is random (gpt2 perplexity and text statistics), so that's expected.

**Did I hold everything because my targets were low?** Partly, yes.
Criterion 1 held on my ten pieces, but the attack set's human pieces in a
formal register, from a second-language writer, written to a rubric, and
technical docs (FP02-FP05) were all labelled AI. My ten pieces didn't include
writing like that. Criterion 2's target of 0.25 was met twice over, because
"clearly AI" and "clearly human" are the easy cases by design. The one I'd
tighten is **criterion 1**: test it on 10 pieces that include formal,
second-language and rubric-style writing, because that's who the attack run
shows getting accused.

**Real output from trial 1**, verbatim from `results/run_2026-11-09_2239_before.md`. The service's answers
come from `app.py::submit` and `app.py::appeal`; `run_eval.py::main`
recorded them.

Criterion 1, `plain_04_my_dog.txt` (closest to the AI line) and
`regular_06_movie.txt` (the only one labelled human):

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6958,
    "model_score": 0.6455,
    "style_score": 0.7712,
    "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "Our family has a dog called Rocky. He is a brown mixed breed and just "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3952,
    "model_score": 0.5606,
    "style_score": 0.1472,
    "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "I finally saw the movie everyone kept recommending, and I understand t"
  }
]
```

Criterion 2, the first clear-AI and the first clear-human piece (all ten are
in the results file):

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7906,
    "model_score": 0.7965,
    "style_score": 0.7818,
    "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "Reading regularly offers a wide range of benefits that extend far beyo"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3329,
    "model_score": 0.4607,
    "style_score": 0.1411,
    "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "But when Elizabeth told of his silence, it did not seem very likely, e"
  }
]
```

Criterion 3, (a) the sweep at each side of both thresholds, from
`run_eval.py::run_label_sweep` calling `scoring.py::score_to_label`, and
(b) one piece for each label from the 9-piece set:

```json
[
  {
    "score": 0.44,
    "guess": "human",
    "has_label": true
  },
  {
    "score": 0.45,
    "guess": "unsure",
    "has_label": true
  },
  {
    "score": 0.7,
    "guess": "unsure",
    "has_label": true
  },
  {
    "score": 0.71,
    "guess": "ai",
    "has_label": true
  }
]
```

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7024,
    "model_score": 0.7544,
    "style_score": 0.6245,
    "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3008,
    "model_score": 0.4445,
    "style_score": 0.0852,
    "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "I didn't sleep. Not properly, anyway — I lay there listening to the bo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6075,
    "model_score": 0.5186,
    "style_score": 0.7409,
    "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
    "error": null,
    "not_json": null,
    "logged": [
      {
        "event": null,
        "status": "decided",
        "reason": null,
        "http_status": null
      }
    ],
    "sent": "Among the lesser criticisms which have been exercised on the Constitut"
  }
]
```

Criterion 4, one real appeal with the log entry it left, one unknown id, and
one empty reasoning, from `run_eval.py::run_appeals`:

```json
[
  {
    "case": "real",
    "submit_status": 200,
    "content_id": "c_2c0e9ccea4f0",
    "appeal_status": 200,
    "response": {
      "appeal_recorded_at": "2026-11-10T03:39:19+00:00",
      "content_id": "c_2c0e9ccea4f0",
      "message": "Thanks, we've got your appeal. A person will review this piece. Until then it's marked as under review, not as AI-generated.",
      "previous_guess": "ai",
      "status": "under_review"
    },
    "appeal_entry": {
      "content_id": "c_2c0e9ccea4f0",
      "creator_id": "eval_appeal_t1_1",
      "event": "appeal",
      "reasoning": "I wrote this myself, in my own words. Please have a person look at it.",
      "status": "under_review",
      "timestamp": "2026-11-10T03:39:19+00:00"
    }
  },
  {
    "case": "unknown_id",
    "content_id": "c_000000000000",
    "appeal_status": 404,
    "response": {
      "error": "unknown_content_id",
      "message": "We have no submission with content_id 'c_000000000000'. Check it against the one /submit gave you."
    },
    "appeal_entries_for_id": 0
  },
  {
    "case": "empty_reasoning",
    "content_id": "c_2c0e9ccea4f0",
    "reasoning_sent": "",
    "appeal_status": 400,
    "response": {
      "error": "missing_reasoning",
      "message": "Tell us in a sentence or two why you think we got it wrong."
    }
  }
]
```

Criterion 5, the body that isn't a JSON object and the 25,000-character text,
with the log entry each left:

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "error": "invalid_body",
    "not_json": null,
    "logged": [
      {
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_body",
        "http_status": 400
      }
    ],
    "sent": "raw body: [\"text\", \"creator_id\"]"
  },
  {
    "status": 413,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "error": "text_too_long",
    "not_json": null,
    "logged": [
      {
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_long",
        "http_status": 413
      }
    ],
    "sent": "word word word word word word word word word word word word word word "
  }
]
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
