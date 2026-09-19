---
name: anse-release-manager
description: >-
  Automate quality gate verification, version bumping, Git commits, pushes, and
  GitHub release creation for the AutoevolveAI / ANSE repository. Use this skill when
  finalizing, tagging, or publishing new releases.
---

# ANSE Release Manager Skill

This skill guides the agent through the complete release lifecycle for ANSE, enforcing all formal and empirical quality gates before committing or tagging.

## 1. Quality Gate Checklist

Before making any release, all gates must pass:
1. **Formal Proofs:** `cd formal && lake build` (all jobs must succeed).
2. **Python Test Suite:** `uv run pytest tests/` (all 195+ tests must pass).
3. **Documentation:** Ensure `README.md`, `memory.md`, and walkthroughs reflect new use cases and features.
4. **Version Bump:** Update `version = "x.y.z"` in `pyproject.toml`.

## 2. Git Automation Commands

```bash
# Stage modified and new files
git add README.md memory.md pyproject.toml formal/ tasks/ tests/

# Commit with structured semantic commit message
git commit -m "feat: <concise summary of release> (vX.Y.Z)

- <bullet point 1>
- <bullet point 2>"

# Push to origin main
git push origin main
```

## 3. GitHub Release Creation

```bash
gh release create vX.Y.Z \
  --title "ANSE vX.Y.Z — <Release Title>" \
  --notes "<Detailed markdown release notes>"
```
