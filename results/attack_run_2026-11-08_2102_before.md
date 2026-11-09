# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 21:02
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_eae485952bfe` | unsure | 0.477 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_dac5af663c5a` | human | 0.433 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_4c2c0428f5a3` | unsure | 0.579 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_acf477506b06` | ai | 0.744 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_1521526a4014` | human | 0.308 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_5c1cc6a91b93` | unsure | 0.469 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_db897ed6b7de` | unsure | 0.482 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `c_4abfcdf65ef4` | unsure | 0.491 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_2683d9b4f671` | unsure | 0.587 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_73a25eb7b546` | ai | 0.798 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_93823c34a964` | unsure | 0.568 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `c_1f869fc12fe1` | ai | 0.750 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_735bd2772d77` | ai | 0.776 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_064047ab4f16` | ai | 0.770 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_673630789cea` | ai | 0.758 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_9fb1a5a48219` | unsure | 0.668 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_832f25d5faaf` | unsure | 0.605 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `c_1e1be425ebfc` | unsure | 0.421 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_89c5ebed0ce5` | human | 0.381 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_e901ed857910` | human | 0.165 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_0e8b4fd4ece4` | unsure | 0.605 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_785c4c7e8c2c` | unsure | 0.496 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_1a21900a6bb2` | unsure | 0.487 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_eaf42fda4133` | unsure | 0.544 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `c_5e7a118cf718` | unsure | 0.358 |  |
| MF04 | malformed | text is only punctuation | 200 | `c_a63cc5d82ae8` | unsure | 0.365 |  |
| MF05 | malformed | text is a very long single word | 200 | `c_5f737ca74917` | unsure | 0.957 |  |
| MF06 | malformed | text is emoji only | 200 | `c_b4d543fa784d` | unsure | 0.956 |  |
| MF07 | malformed | text is right-to-left script | 200 | `c_e8f14f1624e7` | unsure | 0.902 |  |
| MF08 | malformed | text is 60,000 characters | 413 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_67dda814b7a8` | unsure | 0.375 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_0964dfaf8200` | unsure | 0.375 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_d80c4200f19d` | unsure | 0.375 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_aa501d9f6b92` | unsure | 0.375 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_76d7bf25a8b4` | unsure | 0.375 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_eae485952bfe",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.4768,
  "model_score": 0.1635,
  "style_score": 0.9468,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_dac5af663c5a",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.4326,
  "model_score": 0.5943,
  "style_score": 0.1901,
  "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_4c2c0428f5a3",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5791,
  "model_score": 0.6662,
  "style_score": 0.4485,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_acf477506b06",
  "creator_id": "attacker_EV04",
  "guess": "ai",
  "confidence": 0.7441,
  "model_score": 0.6114,
  "style_score": 0.9431,
  "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_1521526a4014",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3084,
  "model_score": 0.3212,
  "style_score": 0.2891,
  "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_5c1cc6a91b93",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4691,
  "model_score": 0.5727,
  "style_score": 0.3136,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_db897ed6b7de",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.4825,
  "model_score": 0.5862,
  "style_score": 0.327,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_4abfcdf65ef4",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.4909,
  "model_score": 0.2452,
  "style_score": 0.8594,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_2683d9b4f671",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5873,
  "model_score": 0.7042,
  "style_score": 0.412,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_73a25eb7b546",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.7985,
  "model_score": 0.9792,
  "style_score": 0.5275,
  "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_93823c34a964",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5677,
  "model_score": 0.6175,
  "style_score": 0.493,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_1f869fc12fe1",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.7495,
  "model_score": 0.7387,
  "style_score": 0.7658,
  "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_735bd2772d77",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.7765,
  "model_score": 0.8051,
  "style_score": 0.7337,
  "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_064047ab4f16",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.7705,
  "model_score": 0.8329,
  "style_score": 0.6768,
  "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_673630789cea",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7581,
  "model_score": 0.8005,
  "style_score": 0.6946,
  "label": "This piece shows strong signs of being generated by AI: both of our checks point that way. Automated checks can be wrong. If you wrote this yourself, you can appeal, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_9fb1a5a48219",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.6677,
  "model_score": 0.8814,
  "style_score": 0.3472,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_832f25d5faaf",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.6054,
  "model_score": 0.8816,
  "style_score": 0.1912,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_1e1be425ebfc",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.4207,
  "model_score": 0.3223,
  "style_score": 0.5684,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_89c5ebed0ce5",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.3808,
  "model_score": 0.4625,
  "style_score": 0.2582,
  "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_e901ed857910",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.1646,
  "model_score": 0.2044,
  "style_score": 0.1049,
  "label": "This looks like a person wrote it. Our checks found nothing that suggests it was generated by AI.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_0e8b4fd4ece4",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.6049,
  "model_score": 0.5943,
  "style_score": 0.6207,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_785c4c7e8c2c",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4957,
  "model_score": 0.4998,
  "style_score": 0.4896,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_1a21900a6bb2",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4875,
  "model_score": 0.6401,
  "style_score": 0.2585,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_eaf42fda4133",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5439,
  "model_score": 0.5583,
  "style_score": 0.5224,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_5e7a118cf718",
  "creator_id": "attacker_MF03",
  "guess": "unsure",
  "confidence": 0.358,
  "model_score": 0.0,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_a63cc5d82ae8",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.3647,
  "model_score": 0.0112,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_5f737ca74917",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.9566,
  "model_score": 0.9976,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_b4d543fa784d",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.9561,
  "model_score": 0.9969,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_e8f14f1624e7",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.9018,
  "model_score": 0.9064,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 413,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_67dda814b7a8",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3752,
  "model_score": 0.0287,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_0964dfaf8200",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3752,
  "model_score": 0.0287,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_d80c4200f19d",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3752,
  "model_score": 0.0287,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_aa501d9f6b92",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3752,
  "model_score": 0.0287,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_76d7bf25a8b4",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3752,
  "model_score": 0.0287,
  "style_score": 0.895,
  "label": "We can't tell either way, so we're not making a call. Our checks gave mixed or weak results, which happens often with writing people did themselves, especially short or plainly worded pieces. This is not a finding that AI was used, and nothing happens to the piece or its writer because of it.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
