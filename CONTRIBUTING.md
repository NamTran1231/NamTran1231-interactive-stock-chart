# 🛠️ Contributing Guidelines & Git Workflow

This document outlines the collaborative workflow, branching strategy, and commit standards for the 4 team members of the **Interactive Real-Time Stock Chart Engine** project. All contributors must adhere to these conventions to maintain a clean, traceable, and professional version history.

---

## 1. Branching Strategy (Milestone-Based Workflow)

To maintain codebase stability, ensure clean version control history, and cleanly separate academic grading milestones, direct pushes to the `main` branch are strictly prohibited.

* **`main` Branch:** Represents production-ready, stable, and tested code. Protected against direct commits.
* **Short-lived branches:** Use `feature/m<N>-<task>` for new implementation work and `docs/<task>` for documentation. Start from current `main`, open a focused PR, then start the next task on a fresh branch. Ownership is stable; a branch represents a task, not a permanent personal workspace.

The M0–M6 plan in `ROADMAP.md` replaces the three-stage naming scheme:

| Developer / Member | Ownership | Example future branch |
| --- | --- | --- |
| 1 — Hưng | Candle model, CSV, custom array Ring Buffer | `feature/m1-csv-loader` |
| 2 — Dũng | QPainter rendering, coordinates, interactions | `feature/m2-chart-canvas` |
| 3 — Phát | Custom Segment Tree, scan oracle, query tests | `feature/m3-segment-tree` |
| 4 — Nam (Project Lead) | CLI/app integration, replay, benchmarks, docs | `feature/m1-cli-summary` |

Example branches are not claims that they already exist. Keep existing `feature/stage1-*`, `feature/ring-buffer`, and `test` history. Do not delete or rewrite teammate work. Review the Ring Buffer prototype and move useful changes through focused PRs; do not blindly merge its PyQt5 simulator or generated `.pyc` files. Agree with the contributor before migrating work.

Each owner tests their module; Developer 4 coordinates integration/review. Coordinate cross-module changes through `docs/interfaces.md`. Sliding-window analytics is optional unless required by the course rubric.

---

## 2. Commit Message Standards (Conventional Commits)

Commit messages must follow the Conventional Commits specification. Every message must clearly describe what was changed and why:

Format:
<type>(<scope>): <short imperative description>

### Commit Types:
* `feat`: Add a new user-facing feature or algorithm (Thêm một tính năng mới hoặc thuật toán mới).
* `fix`: Fix a bug in the codebase (Sửa lỗi trong mã nguồn).
* `perf`: Performance optimization, improving algorithm execution speed (Tối ưu hóa hiệu năng, cải thiện tốc độ thuật toán).
* `test`: Add automated unit tests or correct existing tests (Thêm bài kiểm thử tự động hoặc sửa test).
* `docs`: Update documentation, README, notes, or UML diagrams (Cập nhật tài liệu, README, ghi chú, biểu đồ UML).
* `refactor`: Restructure source code without changing external behavior (Tái cấu trúc mã nguồn mà không đổi tính năng).
* `chore`: Project configuration, dependency, or .gitignore maintenance.

### Approved Examples (Ví dụ commit chuẩn):
* ✅ feat(canvas): implement world to screen coordinate transform
* ✅ feat(tree): implement query range min max in segment tree
* ✅ feat(stream): create ring buffer with fixed capacity for realtime candles
* ✅ fix(canvas): correct vertical axis inversion when zooming
* ✅ test(tree): add unit test cases for segment tree edge cases
* ✅ docs(uml): add class diagram to docs folder

### Prohibited Examples (Các ví dụ KHÔNG ĐƯỢC làm):
* ❌ update code
* ❌ fix bug
* ❌ xong nhe
* ❌ final version 1

---

## 3. Commit Cadence & Work Distribution

* **Atomic Commits:** Make small, logical commits frequently. Avoid bundling an entire week's worth of work into a single monolithic commit.
* **Commit Frequency:** Each contributor is expected to make at least 2 to 3 commits per week on their designated branch to demonstrate steady, equitable contribution across the project lifecycle.

---

## 4. Pull Request & Review Protocol

1. **Push Changes:** Push local commits to your remote feature branch:
   git push origin feature/<your-branch-name>

2. **Open a Pull Request (PR):**
   * Navigate to the GitHub repository and open a PR targeting `main`.
   * Title the PR clearly (e.g., `feat(tree): implement query range min max in segment tree`).
   * Provide a brief bulleted summary of changes and verify that all unit tests pass.

3. **Review & Merge:**
    * The Project Lead (Nam, Developer 4) reviews the PR for merge conflicts and test coverage before merging into `main`.

4. **Synchronize Local Branches:**
   * After a merge, pull the latest changes from `main` into your local feature branch:
     git checkout main
     git pull origin main
     git checkout feature/<your-branch-name>
     git merge main
