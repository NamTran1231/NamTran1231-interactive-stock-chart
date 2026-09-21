# 🛠️ Contributing Guidelines & Git Workflow

This document outlines the collaborative workflow, branching strategy, and commit standards for the 4 team members of the **Interactive Real-Time Stock Chart Engine** project. All contributors must adhere to these conventions to maintain a clean, traceable, and professional version history.

---

## 1. Branching Strategy (Stage-Based Workflow)

To maintain codebase stability, ensure clean version control history, and cleanly separate academic grading milestones, direct pushes to the `main` branch are strictly prohibited.

* **`main` Branch:** Represents production-ready, stable, and tested code. Protected against direct commits.
* **Stage-Based Feature Branches (`feature/stageX-...`):** Each team member works exclusively on their assigned feature branch corresponding to the active project stage:

#### 📌 Stage 1: Core Custom DSA Engine & Terminal CLI
* `feature/stage1-ring-buffer` — Developer 1 (CSV Ingestion & Ring Buffer)
* `feature/stage1-sliding-window` — Developer 2 (Sliding Window Min/Max)
* `feature/stage1-segment-tree` — Developer 3 (Segment Tree & Range Query)
* `feature/stage1-cli-benchmark` — Developer 4 (CLI Visualizer, Test Runner & Integration)

*(Note: For Stage 2 and Stage 3, new branches prefixed with `feature/stage2-...` and `feature/stage3-...` will be created accordingly upon completion of the previous stage).*

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
   * The Project Lead (Developer 4) reviews the PR for merge conflicts and test coverage before merging into `main`.

4. **Synchronize Local Branches:**
   * After a merge, pull the latest changes from `main` into your local feature branch:
     git checkout main
     git pull origin main
     git checkout feature/<your-branch-name>
     git merge main
