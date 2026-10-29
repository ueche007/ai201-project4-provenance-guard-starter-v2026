# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. Human writing is almost never called AI

Of 10 pieces of human writing (at least 4 of them plain writing: short
sentences, everyday words), **at most 1 gets the high-confidence AI label**, and
that holds in **each** of 3 trials. None of the 4 plain pieces may get it in any
trial.

**Why this target:** a wrong accusation is the expensive mistake here, and plain
writing is exactly what signal one mistakes for a machine. One in ten is
already a real cost to a real person; I'd rather let AI text through than go
higher. Zero for the plain pieces because those writers (second-language,
younger, writing plainly on purpose) have the least room to argue back.

---

## 2. Clearly-AI and clearly-human text score far apart

Across 5 clearly AI-generated pieces and 5 clearly human pieces, **the mean
combined score of the AI set is at least 0.25 higher than the mean of the
human set**, in each of 3 trials.

**Why this target:** a score that varies by only a few hundredths between
obvious cases can't support three labels; the bands would be decided by
noise. 0.25 is the width of my unsure band plus a margin, so the two groups
can sit on opposite sides of it.

> **Correction (unit 7, after the build):** the reason above is wrong as
> written. When I wrote it the band was 0.35–0.65 (0.30 wide); it's now
> 0.45–0.70, exactly 0.25 wide, so there is no margin. The target itself is
> unchanged: 0.25 is the full width of the unsure band.

---

## 3. All three labels are reachable, and no score falls through a gap

(a) Sweeping the combined score from 0.00 to 1.00 in steps of 0.01 through
`scoring.score_to_label`, **101 of 101 values map to exactly one of the three
labels**. (b) A 9-piece set (3 AI, 3 human, 3 borderline) produces **each of the
three labels at least once** in each of 3 trials.

**Why this target:** a label that no input can reach is a label the reader
never sees, and a gap between thresholds is a crash or a blank label waiting to
happen. (a) checks the mapping; (b) checks that real text, not just a number I
typed, gets there.

---

## 4. Every appeal is recorded and changes status; bad appeals are refused

**10 of 10** appeals against real content_ids return 200, after which
`GET /log` shows an `appeal` entry with the writer's reasoning and
`status: under_review` for that content_id. **3 of 3** appeals against a
content_id that doesn't exist return 404 and write **no** appeal entry.
**3 of 3** appeals with empty reasoning return 400.

**Why this target:** the appeal is the only thing between a wrong accusation and
nothing at all, so "most of the time" isn't good enough. It has to be all of
them. Refusing unknown ids matters too: an appeal that says "received" for a
typo'd id tells the writer they're being reviewed when nobody will ever look.

---

## 5. Bad input never crashes the service

Of 7 malformed `/submit` requests (no `text` field, empty text, whitespace-only
text, `text: null`, `text` as a number, a body that isn't a JSON object, and text
over 20,000 characters), **0 return a 5xx**. Each returns a 4xx with a JSON
`error` field saying what was wrong, and **7 of 7** leave a `rejected` entry
in the audit log.

**Why this target:** a crash on malformed input is one of the most common real
failures, and the attack set will send all of these. A rejection that leaves no
trace in the log is an attack I can't see later.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
