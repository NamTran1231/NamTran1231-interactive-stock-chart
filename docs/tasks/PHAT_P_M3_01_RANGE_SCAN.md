# Phát's Assignment — Range-Statistics Scan

- **Task ID:** P-M3-01
- **Owner:** Phát — Member 3
- **Reviewer:** Nam
- **Status:** Assigned; implementation not verified
- **Suggested branch:** `feature/m3-range-scan`

## 1. Goal

Implement a function that scans a selected range of candles and returns:

1. Minimum **low**.
2. Maximum **high**.
3. Total **volume**.

Use a normal loop. **Do not implement the Segment Tree yet.** This scan will become the reference result, also called an oracle, used to verify the future tree. Dũng can continue his separate M2 drawing task while you work on this task.

## 2. Read before editing

| File | What to understand |
| --- | --- |
| `AGENTS.md` | Instructions for your AI agent, if used |
| `ROADMAP.md` | Member 3's responsibility and the M3 goal |
| `docs/interfaces.md` | Range queries: half-open intervals, results, and errors |
| `src/core/candle.py` | Existing Candle fields; reuse this model |
| `tests/test_candle.py` | The project's unittest style |
| `CONTRIBUTING.md` | Branch, commit, and PR rules |

Use the restored current `main`. **Do not start from the reverted LeetCode-workflow branch or use its clamping rules.**

## 3. Prepare your branch

Open a terminal at the repository root and run:

```bash
git status
```

If there are uncommitted changes, preserve them and ask Nam before switching. Do not reset, clean, or delete previous work.

With a clean working tree:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feature/m3-range-scan
git branch --show-current
```

The last command should print `feature/m3-range-scan`. If the branch already exists or a command fails, ask Nam rather than overwriting anything. This guide does not claim the branch already exists on GitHub.

## 4. Learn only what you need

Search these terms:

```text
Python frozen dataclass
Python list indexing and range loop
half open interval inclusive exclusive
linear scan minimum maximum sum
Python unittest assertRaises assertAlmostEqual
```

Before coding, understand:

```text
Indices:      0       1       2       3       4
Candles:      A       B       C       D       E

[1, 4) selects B, C, D.
```

`left` is included; `right` is excluded. Therefore, `right == len(candles)` is valid. `[2, 2)` selects nothing.

## 5. Create the shared result class

Create **`src/algorithms/range_stats.py`**:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RangeStats:
    min_low: float
    max_high: float
    volume_sum: float
```

This packages the three answers. The Segment Tree will reuse this class later; do not create a second result type when implementing the tree.

- [ ] Correct file path and class name.
- [ ] Exactly the three fields above.
- [ ] Can import and construct a RangeStats object.

## 6. Implement the scan

Create **`src/algorithms/range_scan.py`** with this interface:

```python
from src.core.candle import Candle
from src.algorithms.range_stats import RangeStats


def scan_range(
    candles: list[Candle],
    left: int,
    right: int,
) -> RangeStats | None:
    # Implement the steps below.
    ...
```

For this task, callers provide integer indices as specified by the type hints. Do not invent new index-conversion behavior or silently convert strings/floats.

### Step A — validate bounds

Require:

```text
0 <= left <= right <= len(candles)
```

Otherwise, raise `IndexError` with a useful message. Do not clamp indices to fit the list.

### Step B — handle a valid empty interval

If `left == right`, return `None`. Validate bounds first: `[5, 5)` is invalid for a three-candle list, even though its width is zero.

### Step C — initialize accumulators

- Minimum low starts at the first selected candle's low.
- Maximum high starts at the first selected candle's high.
- Total volume starts at `0.0`.

Do not initialize price extrema to zero: that fails for ranges containing only positive lows or only negative highs.

### Step D — scan the selected indices

```python
for index in range(left, right):
    candle = candles[index]
    # Update minimum low using candle.low.
    # Update maximum high using candle.high.
    # Add candle.volume to the total.
```

Do not use close prices for extrema. Do not create `candles[left:right]`; an index loop avoids allocating a copy. Do not modify the list or any candle.

### Step E — return the result

Return a `RangeStats` instance containing the computed minimum low, maximum high, and volume total, in that order.

- [ ] Bounds are checked before indexing.
- [ ] Valid empty intervals return None.
- [ ] Only selected candles contribute.
- [ ] Input is unchanged.
- [ ] A nonempty query returns RangeStats, not a tuple or dict.

## 7. Check exact examples

Use the existing model:

```python
candles = [
    Candle(1704067200, 100, 105, 98, 103, 1000),
    Candle(1704067260, 103, 108, 102, 107, 1500),
    Candle(1704067320, 107, 109, 101, 102, 1200),
]
```

| Call | Expected result |
| --- | --- |
| `scan_range(candles, 0, 3)` | `RangeStats(98, 109, 3700)` |
| `scan_range(candles, 1, 3)` | `RangeStats(101, 109, 2700)` |
| `scan_range(candles, 1, 2)` | `RangeStats(102, 108, 1500)` |
| `scan_range(candles, 2, 2)` | `None` |
| `scan_range(candles, 3, 3)` | `None` |
| `scan_range([], 0, 0)` | `None` |
| `scan_range(candles, -1, 2)` | `IndexError` |
| `scan_range(candles, 0, 4)` | `IndexError` |
| `scan_range(candles, 2, 1)` | `IndexError` |
| `scan_range(candles, 5, 5)` | `IndexError` |

Explain why `[1, 3)` returns minimum low **101**, not 98: index 0 is outside the selection.

## 8. Write focused tests

Create **`tests/test_range_scan.py`** using `unittest`; no new test dependency is needed.

Minimal structure:

```python
import unittest

from src.algorithms.range_scan import scan_range
from src.algorithms.range_stats import RangeStats
from src.core.candle import Candle


class RangeScanTests(unittest.TestCase):
    def test_full_range(self):
        # Arrange: create the three candles above.
        # Act: call scan_range(candles, 0, 3).
        # Assert: compare with RangeStats(98, 109, 3700).
        ...
```

Replace placeholders with real assertions. A test containing only `pass` or `...` does not verify anything.

Required checklist:

- [ ] Full range matches hand-calculated results.
- [ ] Partial range excludes candles outside the bounds.
- [ ] One-candle query returns its low/high/volume.
- [ ] Empty interval at the middle and end returns None.
- [ ] Empty list with `[0, 0)` returns None.
- [ ] Negative, excessive, inverted, and out-of-range empty bounds raise IndexError.
- [ ] Negative prices work; construct valid negative-price candles rather than violating Candle validation.
- [ ] Fractional volumes use `assertAlmostEqual` for the total.
- [ ] Input contents and order remain unchanged after the query.

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_range_scan.py' -v
python -m unittest discover -s tests -v
```

Use `python3` if necessary. GUI checks can skip if PyQt6 is absent; report skips honestly. Record actual output, not an assumed pass.

## 9. Explain complexity

Let **W = right - left**, the number of selected candles.

- A nonempty valid query takes **O(W) time** because it visits each selected candle once.
- It uses **O(1) auxiliary space** because it stores a fixed number of accumulators and one result, without copying the interval.
- Empty intervals and invalid-bound checks take constant time.

Write a short docstring explaining these costs and the interval/error rules. Do not claim O(log N); that is the later Segment Tree goal.

## 10. Scope and submission

Expected changed files are only:

```text
src/algorithms/range_stats.py
src/algorithms/range_scan.py
tests/test_range_scan.py
```

Do not change the roadmap, team roles, GUI, model, loader, fixtures, or agent skills. Do not implement the tree, redesign the application, or replace completed work with TODOs. If a shared contract needs a change, discuss it with Nam first. UML/design patterns are not required for this small task.

Review your diff, then:

```bash
git add src/algorithms/range_stats.py src/algorithms/range_scan.py tests/test_range_scan.py
git commit -m "feat(query): add range scan baseline and shared statistics"
git push -u origin feature/m3-range-scan
```

Open a PR into `main`. **Nam reviews before merge.**

Send this handoff:

```text
Task: P-M3-01 — Range-statistics scan
PR link:
Files changed:
Commands run and actual results:
Explanation of [left, right):
Time and auxiliary-space complexity:
Questions or remaining problems:
```

## 11. If using an AI agent

Paste this:

```text
I am Phát, Member 3. Read AGENTS.md and
docs/tasks/PHAT_P_M3_01_RANGE_SCAN.md, then read its listed contracts.
Help me implement ONLY task P-M3-01 on current restored main.
Check git status and preserve existing work before changing branches.
Use the existing Candle model and half-open interval semantics.
Invalid bounds raise IndexError; do not clamp them.
Limit changes to the three implementation/test files listed in the task.
Explain the algorithm and tests so I can understand and present them.
Run checks and report actual results. Do not claim unexecuted checks passed.
Do not commit, push, or merge unless I explicitly ask.
Do not change architecture, roles, plans, or other people's modules.
```

**Next task after acceptance:** implement the Segment Tree and compare its results against this scan. Completing this assignment does not complete all of M3.
