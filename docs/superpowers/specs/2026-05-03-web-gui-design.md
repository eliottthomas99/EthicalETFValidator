# Web GUI Design — Ethical ETF Validator

## Goal
Build a simple web interface where users can enter an ISIN and their OpenRouter API key, then receive an ESG risk report for the ETF's top holdings.

## Architecture
```
Browser                    FastAPI Backend              External APIs
  │                            │                            │
  ├─ POST /api/analyze ───────►│                            │
  │  {isin, api_key}           │                            │
  │                            ├─ fetch_top_holdings() ────►│ JustETF
  │                            │                            │
  │                            ├─ search_company_news() ───►│ DuckDuckGo
  │                            │                            │
  │                            ├─ evaluate_esg_risk() ─────►│ OpenRouter
  │                            │  (using user's api_key)    │
  │                            │                            │
  │◄─ JSON report ─────────────┤                            │
```

## API Endpoint

### `POST /api/analyze`
**Request body:**
```json
{
  "isin": "LU2195226068",
  "api_key": "sk-or-v1-..."
}
```

**Response (success):**
```json
{
  "isin": "LU2195226068",
  "holdings": ["Apple Inc.", "Microsoft Corp", "NVIDIA Corp"],
  "results": [
    {
      "company": "Apple Inc.",
      "score": 3,
      "summary": "Low risk. Minor supply chain concerns..."
    }
  ],
  "report": "# ESG Risk Report..."
}
```

**Response (error):**
```json
{
  "error": "Failed to fetch holdings from JustETF"
}
```

## Frontend

Single-page app with three states:

### 1. Input Form
- Title: "Ethical ETF Validator"
- Description: "Enter an ETF ISIN and your OpenRouter API key to analyze its top holdings for ESG risks."
- Input: ISIN (text, placeholder: "LU2195226068")
- Input: API Key (password field, placeholder: "sk-or-v1-...")
- Button: "Analyze"

### 2. Loading State
- Spinner animation
- Status text updates:
  - "Fetching ETF holdings..."
  - "Researching [Company 1]..."
  - "Researching [Company 2]..."
  - "Analyzing risks..."

### 3. Results Display
- ETF identifier
- List of holdings with:
  - Company name
  - Risk score (1-10) with color coding (green/yellow/red)
  - 2-sentence summary
- Full markdown report (expandable or below)
- "Analyze Another ETF" button to reset

## Styling
- Clean, modern look
- Tailwind CSS via CDN (no build step needed)
- Mobile-responsive
- No external dependencies except Tailwind CDN

## Security
- API key is sent in request body (HTTPS in production)
- No storage in browser (localStorage, cookies)
- No server-side storage of API keys
- Each request is stateless

## Deployment
- Platform: Render (free tier)
- Auto-deploy from GitHub `main` branch
- Environment variables: None needed (users provide API keys)

## Files to Create
```
web/
├── app.py              # FastAPI backend
├── requirements.txt    # FastAPI + uvicorn
└── static/
    ├── index.html      # Main page
    ├── style.css       # Custom styles (optional, mostly Tailwind)
    └── app.js          # Frontend logic
```

## Implementation Notes
- Backend reuses existing pipeline code from `src/ethical_validator/`
- No changes to core logic — just a new HTTP wrapper
- Frontend makes fetch() call to `/api/analyze`
- Backend sets `OPENROUTER_API_KEY` env var from request for the duration of the pipeline run
