# 🛠️ Contributing Guidelines & Git Workflow

This document outlines the collaborative workflow, branching strategy, and commit standards for the 4 team members of the **Interactive Real-Time Stock Chart Engine** project. All contributors must adhere to these conventions to maintain a clean, traceable, and professional version history.

---

## 1. Branching Strategy

To maintain codebase stability and satisfy academic Git criteria, direct pushes to the `main` branch are strictly prohibited.

* **`main` Branch:** Represents production-ready, stable, and tested code. Protected against direct commits.
* **Feature Branches (`feature/`):** Each team member works exclusively on their assigned feature branch:
  * `feature/canvas-rendering` &mdash; Developer 1 (Custom Canvas, Coordinates & Viewport)
  * `feature/segment-tree-quadtree` &mdash; Developer 2 (Segment Tree & 2D Quadtree)
  * `feature/data-pipeline-lttb` &mdash; Developer 3 (CSV Loader, Ring Buffer & LTTB)
  * `feature/main-window-patterns` &mdash; Developer 4 (UI Shell, Design Patterns & Tests)

---

## 2. Commit Message Standards (Conventional Commits)

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Every message must clearly explain what was changed and why:

```text
<type>(<scope>): <short imperative description>
