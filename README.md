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
   reason, and the refusal is written to the audit log
   (`app.py::_check_submission`). Nothing malformed reaches a model.
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

All numbers below come from `results/calibration.md`, produced by
`python calibrate.py` from `calibration/texts.json`. That set is 16 passages
from public-domain books on Project Gutenberg (written long before language
models existed) and 8 AI-generated pieces: 4 typical, 2 plainly worded, and 2
lightly hand-edited. **I tuned the settings on these same texts, so the
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
| Expressive punctuation | `; : ! ? ( ) " ' — – …` per 100 words | low (below 1.5) | 0.2 |

Each goes through a logistic curve to 0–1 and the weighted average is the
signal. A measure with no evidence drops out: spread on a one-sentence text,
vocabulary on under 50 words.

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
a quotation, sprinkling in dashes and exclamation marks. One of my
hand-edited AI pieces got from 0.88 down to 0.50 that way. My human set is
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
`VETO_BELOW = 0.5`, cap = `AI_THRESHOLD - 0.01` = 0.69 (`config.py`). The model
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
- **Lightly edited AI (`ai_8` in `results/calibration.md`):** model 0.823,
  style 0.497. The average is 0.6926 and the veto caps it at 0.690, so the
  label is "unsure". That's AI text getting through, which is the trade
  I chose.

---

## Label Variants

Thresholds are `HUMAN_THRESHOLD = 0.45` and `AI_THRESHOLD = 0.70`
(`config.py`). The bands are half-open, so every score from 0.00 to 1.00 maps to
exactly one label; a sweep in steps of 0.01 gave 45 human, 26 unsure, 30 AI,
101 of 101 mapped. Text under 40 words gets the unsure label whatever it scores.

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
one reads as machine-like. Responses pretty-printed with `python -m json.tool`.

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

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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
