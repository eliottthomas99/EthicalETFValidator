# Ethical ETF Validator - Project Blueprint

> **Note for AI agents:** This file replaces the old `GEMINI.md`. If you're using the Gemini CLI, point it here instead.

## Vision
A pipeline that detects greenwashing by cross-referencing ETF holdings with real-world news and controversies.

## Current Tech Stack (Prototype)
- **Orchestration:** LangGraph (Python)
- **LLM:** `nvidia/nemotron-3-super-120b-a12b:free` (via OpenRouter)
- **Environment:** `uv`
- **Data Tools:** `justetf.com` scraping (ETF holdings via ISIN), `ddgs` (DuckDuckGo web search)

## Milestone 1: "Walking Skeleton" (Completed)
1. Fetch top 3 holdings for an ETF.
2. Search web for recent news on those companies.
3. Rough LLM evaluation for greenwashing/ethics risk using `langchain-openai` (OpenRouter).
4. Output basic markdown report to `reports/`.

> **Updates since initial implementation:**
> - Replaced `yfinance` with **JustETF scraper** (`holdings.py`) — no API key needed, better recency for European ETFs.
> - Replaced `tavily-python` with **DuckDuckGo search** (`ddgs`) — removed paid API dependency.
> - Input is now the fund's **ISIN** (e.g. `LU2195226068`) rather than a ticker symbol.

## Milestone 2: Graph Architecture (Completed)
1. Transition the linear script (`main.py`) into a LangGraph `StateGraph`.
2. Define the State schema to pass data between nodes.
3. Wire the nodes: `fetch_holdings` -> `research_companies` (parallel map/reduce) -> `analyze_ethics` -> `generate_report`.
4. Extracted Sub-Graph (`company_graph.py`) and Main Graph (`etf_graph.py`) for clarity.

## Milestone 3: Refining Data Sources & Features (In Progress)
1. ~~Investigate alternative holding fetchers (replacing or augmenting `yfinance` for better recency).~~ ✅ **Done** — JustETF scraper implemented.
2. ~~Consider caching mechanisms to reduce `ddgs` / API costs across runs.~~ ✅ **Done** — Replaced with **Company Knowledge Base** (`knowledge_base.py`). Accumulates research per company, auto-compacts when thresholds are met.
3. Enhance the LLM evaluation prompt and scoring mechanism.

## Known Limitations & Future Improvements
- **Scraping fragility:** JustETF layout changes could break `holdings.py`. A fallback strategy or API-based source would improve resilience.
- **Holdings caching:** ETF holdings are re-fetched from JustETF on every run. Holdings don't change minute-to-minute, so a short TTL cache (e.g., 1 hour) could reduce scraping load.
- **ISIN-only input:** Currently requires the user to provide the ISIN. A ticker-to-ISIN lookup would be a nice UX improvement.

## Current Focus: Web GUI
The pipeline works locally. The current priority is building a web interface so users can analyze ETFs without running Python locally.

### Web Architecture
- **Backend:** FastAPI (`web/app.py`)
- **Frontend:** HTML + Tailwind CSS (`web/static/index.html`)
- **Deployment:** Render (free tier)

### Deployment Status
✅ **Render deployment working.** Key fix: ensure `fastapi` and `uvicorn` are in `pyproject.toml` dependencies, and use `.venv/bin/pip install -e .` as the build command so packages install into the same environment as the start command.

### What's Left
- [ ] Wire the `/api/analyze` endpoint to the actual ETF pipeline
- [ ] Add loading states and progress feedback
- [ ] Polish the UI (colors, typography, responsive design)
- [ ] Handle errors gracefully (invalid ISIN, API failures, etc.)
- [ ] Add report display (markdown rendering)

## Project Standards
- Surgical updates to code.
- Frequent git commits.
- All secrets (API keys) in `.env`.

## Git Workflow & PR Best Practices
This project uses a branch-and-PR workflow even though it's a single-developer repo. This is intentional practice for professional collaboration:

### Branch Strategy: Task-Level Branches
One branch = one PR = one logical change. Commit freely on the branch (even messy "wip" messages), then clean up at merge time.

### Branch Naming Convention
| Prefix | Use for | Example |
|--------|---------|---------|
| `feature/` | New functionality | `feature/add-caching` |
| `fix/` | Bug fixes | `fix/holdings-scraper-timeout` |
| `docs/` | README, AGENTS.md, comments | `docs/update-pr-workflow` |
| `refactor/` | Restructuring code without changing behavior | `refactor/extract-search-client` |

Rules: lowercase, hyphens between words, descriptive but concise.

### Full Workflow

```bash
# 1. Start fresh from main
git checkout main && git pull origin main
git checkout -b feature/description

# 2. Work freely — commit as often as you want
# (Messy messages like "wip", "fix", "ugh" are totally fine)
git add .
git commit -m "wip start caching"
git commit -m "fix import error"
git commit -m "tests pass"

# 3. Before PR: sync your branch with latest main
git checkout main && git pull origin main
git checkout feature/description
git merge main
# Resolve any conflicts if they arise
git push origin feature/description

# 4. Open PR on GitHub
# Base: main | Compare: feature/description
# The diff shows only your changes

# 5. Self-review the PR
# Read every file as if a colleague wrote it
# Check for debug prints, unclear names, missing docs

# 6. Merge with "Squash and merge"
# This combines all your messy commits into one clean commit on main

# 7. Cleanup
git checkout main && git pull origin main
git branch -d feature/description
git push origin --delete feature/description
```

### Why This Workflow?
- **Commit freely:** Your hourly "save point" habit stays intact
- **Push messy commits:** The full draft history is visible in the PR for reference
- **Squash on GitHub:** `main` stays clean with 1 commit per feature
- **Use `git merge main`:** Safer than rebase, no force-push needed, standard in most teams
- **Delete branches after merge:** Keeps the repository clean

### If main Changes While You're Working
This is normal. The `git merge main` step (Step 3) brings the latest `main` into your branch before opening the PR. If there are conflicts, you resolve them before the reviewer sees anything.

### Key Rules
1. **Never commit directly to `main`** — always use a feature branch
2. **Keep PRs small and focused** — one logical change per PR
3. **Self-review before merging** — read the diff as if you were a reviewer
4. **Delete branches after merging** — keeps the remote clean
