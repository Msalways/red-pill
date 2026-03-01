# Releasing Redpill SDKs

This document describes the release process for both the JS and Python Redpill SDKs.

---

## Prerequisites (one-time setup)

Set the following secrets in **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Where to get it |
|--------|----------------|
| `NPM_TOKEN` | npmjs.com → Account → Access Tokens → Automation token |
| `PYPI_API_TOKEN` | pypi.org → Account → API tokens → Scoped to `redpill` |
| `TEST_PYPI_API_TOKEN` | test.pypi.org → Account → API tokens (optional, for dry runs) |

---

## Workflows

| Workflow | File | Trigger |
|----------|------|---------|
| **CI** | `ci.yml` | Every push to `main` / every PR |
| **Publish JS SDK** | `publish-js.yml` | Manual (`workflow_dispatch`) or called from root |
| **Publish Python SDK** | `publish-python.yml` | Manual (`workflow_dispatch`) or called from root |
| **Publish All SDKs** | `publish-all.yml` | Manual (`workflow_dispatch`) |

---

## How to Release

### Option A — Publish both SDKs together (recommended)

1. Go to **GitHub → Actions → "Publish All SDKs"**
2. Click **Run workflow**
3. Choose:
   - `version_type`: `patch` | `minor` | `major`
   - `dry_run`: `false` for real publish, `true` to test
4. Click **Run workflow**

Both SDKs are published in parallel. A summary table appears in the workflow run.

### Option B — Publish one SDK individually

1. Go to **GitHub → Actions → "Publish JS SDK"** (or Python)
2. Click **Run workflow**, choose version type
3. Done

---

## What each publish workflow does

```
Install deps
  → Run tests (gate — fails fast if tests fail)
  → Build (npm build / python -m build)
  → Bump version in package.json / __init__.py + pyproject.toml
  → Git commit + tag (js-vX.Y.Z / py-vX.Y.Z)
  → Publish to npm / PyPI
  → Push commit + tag to repo
  → Create GitHub Release with auto-generated notes
```

### Tags

- JS SDK tags: `js-v1.2.3`
- Python SDK tags: `py-v1.2.3`

This lets both SDKs be versioned independently on the same repo.

---

## Versioning rules

| Type | When to use | Example: 0.1.0 → |
|------|------------|-------------------|
| `patch` | Bug fixes, docs | `0.1.1` |
| `minor` | New features, backwards-compatible | `0.2.0` |
| `major` | Breaking API changes | `1.0.0` |

---

## Dry runs

Set `dry_run: true` to:
- **JS**: runs `npm publish --dry-run` (no actual publish)
- **Python**: publishes to **Test PyPI** (`test.pypi.org`) instead of real PyPI

Neither will push a commit or tag in dry-run mode.

---

## Local development

```bash
# JS SDK
cd packages/js/redpill
npm install
npm test          # run smoke tests
npm run build     # build dist/

# Python SDK
cd packages/python/redpill
pip install -e ".[dev]"
pytest tests/ -v  # run smoke tests
python -m build   # build wheel/sdist
```
