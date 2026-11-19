# Agent Guidelines

## Design Patterns & YAGNI (Python)

Follow [Refactoring.Guru](https://refactoring.guru/design-patterns/creational-patterns) idiomatically without Java-style bloat:

- **Use where justified:** **Factory Method** (`@classmethod` constructors like `ReplayDataSource.from_csv` / `from_synthetic`), **Prototype** (`dataclasses.replace` on immutable `ViewportState`), **Observer** (`EventBus`), and **Command** (`CommandHistory`).
- **Avoid over-engineering:** Do not add `Builder` classes when `@dataclass` defaults suffice, do not add `Abstract Factory` for a single backend (`PyQt6`), and never use global **Singleton** for `EventBus` or `CommandHistory` (inject via constructor for isolated `pytest` tests).
- **Zero-Shortcut DSA Rule:** Never import `collections.deque` in `src/core/ring_buffer.py` or `src/algorithms/monotonic_deque.py`.

## Agent skills

### Issue tracker

GitHub Issues using the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context (`CONTEXT.md` and `docs/adr/` at repo root). See `docs/agents/domain.md`.
