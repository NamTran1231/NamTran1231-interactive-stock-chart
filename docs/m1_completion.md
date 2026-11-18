# M1 Completion Report — November 18, 2026

## 1. Status

PRs #3/#4 introduced the initial Candle/CSV/CLI implementation. PR #5 completed model validation, statistics, preview limits, and tests and has been merged into main at `9920f75`. The `docs/m1-english` follow-up translates the interface and documentation. **Implementation and agent-side checks are complete; the team still needs to confirm an independent run.**

Ownership remains Hưng (model/CSV) and Nam (CLI/integration). Hưng created the initial model; the agent assisted with the loader/CLI and completion at Nam's request. Agent-written changes should not be attributed as independently written student work. Phát and Dũng do not have dedicated M1 testing assignments.

## 2. Deliverables

| Component | File | Behavior |
| --- | --- | --- |
| Model | `src/core/candle.py` | Immutable; validates integer timestamps, finite numeric values, OHLC bounds, and nonnegative volume on direct construction |
| Loader | `src/core/csv_loader.py` | UTF-8 CSV to candles; rejects malformed/duplicate/out-of-order input, adds row context, preserves I/O errors |
| CLI | `src/main_cli.py` | Three-candle demo or CSV input, bounded table preview, full-data summary, empty/error handling |
| Fixture | `tests/fixtures/candles_valid.csv` | 12 deterministic synthetic candles; no external download |
| Tests | `tests/test_candle.py`, `tests/test_csv_cli.py` | Direct model validation and end-to-end CLI subprocess checks |

The model owns individual-candle validation. The loader converts fields and adds row numbers instead of maintaining duplicate OHLC rules. CLI statistics use scans; M1 does not require a Segment Tree.

## 3. Reproduction

Run from the repository root using Python 3.10+. No pip dependencies are needed. An optional virtual environment is documented in README. Use `python3` if required by your system:

```bash
python -m src.core.candle
python -m src.main_cli
python -m src.main_cli tests/fixtures/candles_valid.csv --limit 2
python -m src.main_cli tests/fixtures/candles_valid.csv --limit 0
python -m unittest discover -s tests -v
```

Expected: model demo close price 103; default CLI demo three candles; CSV fixture 12 candles. With `--limit 2`, the table has two rows but the summary covers all 12:

```text
Candle count: 12
First timestamp (UTC Unix seconds): 1704067200
Last timestamp (UTC Unix seconds): 1704067860
Min low: 98.00
Max high: 113.00
Total volume: 13600.00
```

`--limit 0` displays every row. Negative/non-integer limits return status 2. Invalid data/missing files return status 1 with an error on stderr; success returns 0. Empty/header-only input does not crash; single-row input has a summary.

## 4. Evidence and acceptance

The M1 completion was tested on the agent's Linux environment (kernel `7.0.0-43-generic`), Python **3.14.4**: `python3 -m unittest discover -s tests -v` — **19 tests passed**. Python 3.10 and other operating systems were not exercised in that run. Subtests cover multiple invalid values but are not counted as separate tests. The CSV command with `--limit 2` produced the expected statistics. Whitespace and 16 local Markdown link targets were checked for the completion PR. The English follow-up updates assertions to match the translated messages and reruns the suite.

Coverage includes immutability, timestamp types excluding bool, non-finite/nonnumeric values in every numeric field, OHLC/volume rules, negative/flat prices, zero volume, CSV empty/single-row/header/column/order errors, row-specific errors, preview-independent summaries, all-row output, invalid limits, missing files, broken quotes, encoding errors, and quiet imports.

- [x] Deterministic fixture and data validation without GUI/download dependencies.
- [x] CLI summary and sample table.
- [x] Model/CSV/CLI tests pass on the agent's machine.
- [x] README includes setup/demo/test commands and expected output.
- [x] M1 implementation merged through PR #5.
- [ ] Hưng or Nam reproduces the commands on their machine and records OS, Python version, commit, commands, and results in the PR.

Agent-side automation does not substitute for a teammate's independent run. The workflow is still empty; no CI success is claimed. No benchmark was run. GUI, custom DSA integration, and replay belong to later milestones.

## 5. Next step

After the team's successful reproduction, Nam can mark M1 accepted in ROADMAP. M2 begins with a small QPainter chart led by Dũng. This change does not implement M2. The course rubric and deadline remain open constraints.
