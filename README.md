# prompt-injection-fuzzkit

A fuzz harness that generates **mutated prompt-injection attack payloads** against a
sample defended LLM app and produces a **defense scorecard**: blocked vs. bypassed
per attack class, plus an overall bypass rate.

Built for QA engineers who need a repeatable, deterministic way to answer
*"which injection tricks does our defense actually catch?"* — without hand-writing
every adversarial case.

> **Scope note:** the target under test is a *simulated* defense stack
> (`src/prompt_injection_fuzzkit/target.py`), not a production LLM. A "bypass"
> here means the sample defense layer missed the payload — exactly the kind of
> gap this harness is designed to surface before you test a real system.

## Attack classes

| Class | What it tries |
| --- | --- |
| `direct_override` | "Ignore previous instructions…" style overrides |
| `role_confusion` | "You are now in developer mode…" / DAN-style roleplay |
| `encoding_trick` | base64 blobs, zero-width characters |
| `instruction_smuggling` | malicious instruction hidden inside quoted "data" (e.g. a fake email) |
| `multi_turn_escalation` | benign setup turn, then the ask (defense only inspects the latest turn) |
| `prompt_leak` | "Repeat your system prompt verbatim" |

## Mutation strategies

`identity` · `base64_wrap` · `homoglyph` (Cyrillic lookalikes) · `zero_width`
· `sponge_case` · `whitespace_flood` · `prefix_benign`

Every seed × every mutator becomes a case (plus one multi-turn replay), so the
matrix stays deterministic and reproducible — no randomness anywhere.

## The sample defense

Three layers, deliberately imperfect (realistic gaps included):

1. Normalized blocklist scan of the latest user message
2. Base64 blob inspection — suspicious blobs are decoded and re-scanned
3. System-prompt guard — the secret is never emitted

Known gaps the fuzzer exercises: no zero-width stripping, no homoglyph
normalization, latest-turn-only inspection.

## Quickstart

```bash
pip install -e .
fuzzkit            # run the matrix and print the scorecard
fuzzkit --json     # raw per-case results as JSON
pytest             # run the test suite
```

## Example output

```
Ran 64 attack cases.

# Defense Scorecard

| Attack class | Cases | Blocked | Bypassed | Bypass rate |
| --- | ---: | ---: | ---: | ---: |
| direct_override | 14 | 10 | 4 | 28.6% |
| role_confusion | 14 | 10 | 4 | 28.6% |
| encoding_trick | 14 | 3 | 11 | 78.6% |
| instruction_smuggling | 7 | 0 | 7 | 100.0% |
| multi_turn_escalation | 1 | 0 | 1 | 100.0% |
| prompt_leak | 14 | 8 | 6 | 42.9% |
| **Overall** | **64** | **31** | **33** | **51.6%** |

Overall bypass rate: 51.6%
```

(Exact numbers depend on the seed/mutator matrix; the table above is from a real run.)

## Architecture

```
src/prompt_injection_fuzzkit/
├── payloads.py    # seed payloads per attack class
├── mutators.py    # deterministic mutation strategies
├── target.py      # the sample defended app (simulated)
├── runner.py      # builds the case matrix and executes it
├── scorecard.py   # per-class aggregation + Markdown report
└── cli.py         # `fuzzkit` entry point
tests/             # pytest suite (mutators, payloads, target, runner, scorecard)
```

## Test results

64-case matrix, all deterministic:

- `pytest` — **31 passed** (mutators 9 · payloads 2 · target 10 · runner 6 · scorecard 4)

## Extending it

- Add seeds to `payloads.py`, mutators to `mutators.py` — the matrix picks them up automatically.
- Swap `target.defended_chat` for an adapter that calls your real LLM app; the
  runner and scorecard work unchanged as long as the adapter returns
  `{"blocked": bool, "reason": str, "response": str}`.

## License

MIT — see [LICENSE](LICENSE).
