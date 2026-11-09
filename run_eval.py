#!/usr/bin/env python3
"""
Run your five criteria three times each.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_eval.py --label before          # in another
    python run_eval.py --label after

The attack set tests what staff thought to test. This tests what *you* thought
to test, and the two rarely overlap much. Both count.

Fill in `scenarios.py` first — that's where you say what each criterion needs
run against it. A criterion about false positives needs your own writing. One
about label coverage needs inputs across the score range.

!! Three trials, and **your first signal runs a model, so identical input can
score differently twice.** That's exactly why repeats matter here.

This does the sending and the recording, and it works out each trial's number
for each of my five criteria (`measure`), next to the target from criteria.md.
A criterion is MET only if the target holds in every trial.

Beyond plain submissions it also runs:

  - a "label_sweep" scenario: scores 0.00-1.00 through scoring.score_to_label,
    in-process (criterion 3a);
  - an "appeals" scenario: submits, appeals each content_id, and reads the log
    back to check the appeal was recorded (criterion 4);
  - for "bodies" scenarios, the log entries each request left (criterion 5),
    read from GET /log before and after every request.

Run nothing else against the service while this runs: it reads "the entries
this request added" from the end of the log.
"""

import argparse
import datetime as dt
import json
import sys

import config

# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help — which is a miserable first thing to hit.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):  # not a normal text stream
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"

TARGETS = {
    1: "≤ 1 of 10 labelled AI, 0 of 4 plain, every trial",
    2: "mean AI − mean human ≥ 0.25, every trial",
    3: "(a) 101/101 map to one label; (b) 3/3 labels seen, every trial",
    4: "10/10 appeals recorded; 3/3 unknown → 404, no entry; 3/3 empty → 400",
    5: "7/7: no 5xx, 4xx with JSON error, rejected entry logged",
}


def bodies_for(scenario):
    """
    The request bodies one scenario sends.

    A "texts" scenario gets a creator_id made up for it. A "bodies" scenario is
    sent exactly as written, which is how a bad-input criterion says things a
    string can't — no `text` field, a null, something enormous.
    """
    if scenario.get("bodies"):
        return list(scenario["bodies"])
    return [
        {"text": text, "creator_id": f"eval_{scenario['name'][:12]}_{i}"}
        for i, text in enumerate(scenario["texts"], 1)
    ]


def describe(body):
    """A short, readable note of what was sent — for the report."""
    if isinstance(body, str):
        return f"raw body: {body[:100]}"
    if set(body) == {"text", "creator_id"} and isinstance(body.get("text"), str):
        text = body["text"]
        return text[:70] if text else "(empty text)"
    return json.dumps(body)[:120]


# ── Talking to the service ───────────────────────────────────────────────────

class Service:
    def __init__(self, requests, url, timeout):
        self.r, self.url, self.timeout = requests, url, timeout

    def post(self, path, body):
        if isinstance(body, str):
            return self.r.post(f"{self.url}{path}", data=body.encode("utf-8"),
                               headers={"Content-Type": "application/json"},
                               timeout=self.timeout)
        return self.r.post(f"{self.url}{path}", json=body, timeout=self.timeout)

    def log_count(self):
        return self.r.get(f"{self.url}/log", timeout=self.timeout).json()["count"]

    def log_since(self, before):
        """The entries added since the log held `before` entries."""
        added = self.log_count() - before
        if added <= 0:
            return []
        return self.r.get(f"{self.url}/log", params={"limit": added},
                          timeout=self.timeout).json()["entries"]


def _json(response):
    try:
        return response.json() if response.content else {}
    except ValueError:
        return {"_not_json": response.text[:200]}


def submit_and_record(svc, body):
    preview = describe(body)
    try:
        before = svc.log_count()
        response = svc.post("/submit", body)
        payload = _json(response)
        logged = svc.log_since(before)
        return {
            "status": response.status_code,
            "guess": payload.get("guess"),
            "confidence": payload.get("confidence"),
            "model_score": payload.get("model_score"),
            "style_score": payload.get("style_score"),
            "label": payload.get("label"),
            "error": payload.get("error"),
            "not_json": payload.get("_not_json"),
            "logged": [{k: e.get(k) for k in ("event", "status", "reason", "http_status")}
                       for e in logged],
            "sent": preview,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": None, "error": f"{type(exc).__name__}: {exc}", "sent": preview}


def run_label_sweep(_svc, _scenario, _trial):
    import scoring
    out = []
    for i in range(101):
        score = i / 100
        try:
            guess, label = scoring.score_to_label(score)
            out.append({"score": score, "guess": guess, "has_label": bool(label)})
        except Exception as exc:  # noqa: BLE001
            out.append({"score": score, "error": f"{type(exc).__name__}: {exc}"})
    return out


def run_appeals(svc, scenario, trial):
    """Submit each text, appeal it, and read the log back for the appeal entry."""
    out = []
    ids = []
    for i, text in enumerate(scenario["texts"], 1):
        owner = f"eval_appeal_t{trial}_{i}"
        sub = svc.post("/submit", {"text": text, "creator_id": owner})
        content_id = _json(sub).get("content_id")
        ids.append((content_id, owner))
        app = svc.post("/appeal", {"content_id": content_id, "creator_id": owner,
                                   "reasoning": scenario["reasoning"]})
        entries = svc.r.get(f"{svc.url}/log", timeout=svc.timeout).json()["entries"]
        recorded = [e for e in entries if e.get("content_id") == content_id
                    and e.get("event") == "appeal"]
        out.append({
            "case": "real", "submit_status": sub.status_code, "content_id": content_id,
            "appeal_status": app.status_code, "response": _json(app),
            "appeal_entry": recorded[-1] if recorded else None,
        })
    for bad_id in scenario["unknown_ids"]:
        app = svc.post("/appeal", {"content_id": bad_id, "reasoning": scenario["reasoning"]})
        entries = svc.r.get(f"{svc.url}/log", timeout=svc.timeout).json()["entries"]
        out.append({
            "case": "unknown_id", "content_id": bad_id, "appeal_status": app.status_code,
            "response": _json(app),
            "appeal_entries_for_id": sum(1 for e in entries if e.get("content_id") == bad_id
                                         and e.get("event") == "appeal"),
        })
    for (content_id, owner), reasoning in zip(ids, scenario["empty_reasonings"]):
        app = svc.post("/appeal", {"content_id": content_id, "creator_id": owner,
                                   "reasoning": reasoning})
        out.append({"case": "empty_reasoning", "content_id": content_id,
                    "reasoning_sent": reasoning, "appeal_status": app.status_code,
                    "response": _json(app)})
    return out


def run_scenario_trial(svc, scenario, trial):
    kind = scenario.get("kind")
    if kind == "label_sweep":
        return run_label_sweep(svc, scenario, trial)
    if kind == "appeals":
        return run_appeals(svc, scenario, trial)
    return [submit_and_record(svc, body) for body in bodies_for(scenario)]


# ── Turning a trial into the number its criterion names ─────────────────────

def measure(criterion, by_name, t):
    """(cell text, target met?) for one criterion in trial t (0-based)."""
    if criterion == 1:
        sc, res = by_name["my own writing"]
        res = res[t]
        ai = sum(r.get("guess") == "ai" for r in res)
        plain_ai = sum(r.get("guess") == "ai" for r, p in zip(res, sc["plain"]) if p)
        n_plain = sum(sc["plain"])
        ok = all(r.get("status") == 200 for r in res)
        return (f"{ai}/{len(res)} AI, {plain_ai}/{n_plain} plain" + ("" if ok else " (non-200!)"),
                ok and ai <= 1 and plain_ai == 0)
    if criterion == 2:
        ai = [r.get("confidence") for r in by_name["clear AI"][1][t]]
        hu = [r.get("confidence") for r in by_name["clear human"][1][t]]
        if None in ai or None in hu:
            return "missing scores", False
        gap = sum(ai) / len(ai) - sum(hu) / len(hu)
        return (f"{sum(ai)/len(ai):.3f} − {sum(hu)/len(hu):.3f} = {gap:.3f}", gap >= 0.25)
    if criterion == 3:
        sweep = by_name["label sweep"][1][t]
        valid = sum(r.get("guess") in ("human", "unsure", "ai") and r.get("has_label")
                    for r in sweep)
        seen = {r.get("guess") for r in by_name["label mix"][1][t]} & {"human", "unsure", "ai"}
        return (f"(a) {valid}/{len(sweep)}; (b) {len(seen)}/3 ({', '.join(sorted(seen))})",
                valid == len(sweep) == 101 and len(seen) == 3)
    if criterion == 4:
        res = by_name["appeals"][1][t]
        real = [r for r in res if r["case"] == "real"]
        real_ok = sum(r["appeal_status"] == 200 and r["appeal_entry"] is not None
                      and r["appeal_entry"].get("status") == "under_review"
                      and bool(r["appeal_entry"].get("reasoning")) for r in real)
        unk = [r for r in res if r["case"] == "unknown_id"]
        unk_ok = sum(r["appeal_status"] == 404 and r["appeal_entries_for_id"] == 0 for r in unk)
        emp = [r for r in res if r["case"] == "empty_reasoning"]
        emp_ok = sum(r["appeal_status"] == 400 for r in emp)
        return (f"{real_ok}/{len(real)}, {unk_ok}/{len(unk)}, {emp_ok}/{len(emp)}",
                real_ok == len(real) == 10 and unk_ok == len(unk) == 3 and emp_ok == len(emp) == 3)
    if criterion == 5:
        res = by_name["bad input"][1][t]
        no5xx = sum(isinstance(r.get("status"), int) and r["status"] < 500 for r in res)
        jerr = sum(isinstance(r.get("status"), int) and 400 <= r["status"] < 500
                   and bool(r.get("error")) and not r.get("not_json") for r in res)
        logged = sum(any(e.get("event") == "rejected" for e in r.get("logged") or []) for r in res)
        n = len(res)
        return (f"{no5xx}/{n} no 5xx, {jerr}/{n} 4xx+error, {logged}/{n} logged",
                no5xx == jerr == logged == n == 7)
    return "", False


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        import scenarios
    except ImportError:
        print("No scenarios.py found. Milestone 3 starts by filling it in.",
              file=sys.stderr)
        sys.exit(1)

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s). The submission asks for three.\n")

    svc = Service(requests, args.url, args.timeout)
    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario.get('criterion') or '—'})")
        trials = []
        for trial in range(1, args.trials + 1):
            results = run_scenario_trial(svc, scenario, trial)
            trials.append(results)
            summary = [r.get("guess") or str(r.get("appeal_status") or r.get("status") or "—")
                       for r in results]
            print(f"  trial {trial}: {', '.join(summary[:12])}"
                  + (" …" if len(summary) > 12 else ""))
        rows.append({"scenario": scenario, "trials": trials})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    by_name = {row["scenario"]["name"]: (row["scenario"], row["trials"]) for row in rows}
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)
    names = {1: "My own writing called AI", 2: "AI and human scores far apart",
             3: "All three labels reachable, no gaps", 4: "Appeals recorded; bad ones refused",
             5: "Bad input never crashes"}

    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`, numbers by `run_eval.py::measure`",
        "- Service: `app.py::submit` and `app.py::appeal` · scoring: `scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- Settings: weights {config.WEIGHT_MODEL_SIGNAL}/{config.WEIGHT_STYLE_SIGNAL}, "
        f"veto below {config.VETO_BELOW}, human < {config.HUMAN_THRESHOLD}, AI > {config.AI_THRESHOLD}, "
        f"min words {config.MIN_WORDS_TO_JUDGE}",
        "",
        "Each Run cell is that trial's number. The Verdict is MET only if the",
        "target held in every trial.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]
    for c in range(1, 6):
        cells = [measure(c, by_name, t) for t in range(n)]
        verdict = "MET" if all(ok for _, ok in cells) else "MISSED"
        lines.append(f"| {c}. {names[c]} | {TARGETS[c]} | "
                     + " | ".join(text + ("" if ok else " ✗") for text, ok in cells)
                     + f" | {verdict} |")

    lines += ["", "---", "", "## What actually came back", "",
              "Real output. Paste the relevant parts into your README — the rubric",
              "asks for the actual JSON, not a description of it.", ""]

    for row in rows:
        scenario = row["scenario"]
        lines += [f"### {scenario['name']} (criterion {scenario.get('criterion')})", ""]
        if scenario.get("files"):
            lines += ["Files, in order: " + ", ".join(scenario["files"]), ""]
        for trial_number, results in enumerate(row["trials"], 1):
            lines += [f"**Trial {trial_number}**", "", "```json",
                      json.dumps(results, indent=2, ensure_ascii=False), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("Commit it. It's the evidence the test actually happened.")


if __name__ == "__main__":
    main()
