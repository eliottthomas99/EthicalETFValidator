# Alternative Data Sources for ETF Holdings

## Overview
This document summarizes alternative data sources to yfinance for fetching ETF holdings, focusing on improved data recency as identified in Milestone 3 of the project roadmap.

## Identified Alternatives

### 1. Alpha Vantage ETF Profile & Holdings API
- **Documentation**: https://www.alphavantage.co/documentation/#etf-profile
- **Endpoint**: ETF Profile & Holdings (under Fundamental Data)
- **Advantages**:
  - More current data than yfinance
  - Free tier available with API key
  - Includes allocation percentages for holdings
  - Well-documented with multiple language bindings (Python, NodeJS, PHP, C#/.NET)
  - Reliable enterprise-grade API
- **Considerations**:
  - Requires API key (free tier: 5 requests/minute, 500 requests/day)
  - Premium tiers available for higher volume needs

### 2. JustETF
- **Reference**: Mentioned in GEMINI.md as having better recency than yfinance
- **Website**: https://www.justetf.com/
- **Advantages**:
  - European-focused ETF data
  - Comprehensive ETF database
  - Holdings data appears to be frequently updated
- **Considerations**:
  - Likely requires web scraping (no official API documented)
  - May have terms of service restrictions
  - Site structure changes could break scrapers

### 3. Official Fund Manager Sources
- **Examples**: BlackRock/iShares, Vanguard, State Street/SPDR websites
- **Advantages**:
  - Most authoritative source (direct from fund managers)
  - Highest data accuracy and timeliness
  - Often provides downloadable CSV/JSON reports
- **Considerations**:
  - Requires custom scraping for each provider
  - Different formats and structures per provider
  - Higher maintenance overhead
  - May require handling of PDF documents

### 4. Other Financial Data APIs
- **IEX Cloud**: https://iexcloud.io/docs/api/
- **Polygon.io**: https://polygon.io/
- **Financial Modeling Prep**: https://financialmodelingprep.com/
- **Considerations**: These typically focus on stock data rather than specialized ETF holdings data

## Recommended Implementation Approach

### Phase 1: Abstraction Layer
Modify `src/ethical_validator/holdings.py` to support multiple data sources with a common interface:
```python
def fetch_top_holdings(ticker: str, count: int = 3, source: str = "yfinance") -> List[str]:
    if source == "yfinance":
        return _fetch_holdings_yfinance(ticker, count)
    elif source == "alpha_vantage":
        return _fetch_holdings_alpha_vantage(ticker, count, api_key)
    elif source == "justetf":
        return _fetch_holdings_justetf(ticker, count)
    # ... other sources
```

### Phase 2: Fallback Mechanism
Implement a fallback system that tries multiple sources in order of preference:
1. Try primary source (e.g., Alpha Vantage)
2. Fall back to yfinance if primary fails
3. Log which source was used for transparency

### Phase 3: Caching Layer
As mentioned in Milestone 3, implement caching to reduce API calls:
- Cache holdings data for 24-48 hours (typical ETF holdings update frequency)
- Use file-based or memory caching (e.g., diskcache, functools.lru_cache)
- Include cache invalidation based on ETF ticker and date

## Next Steps for Implementation

1. **Acquire API Keys**: Sign up for free Alpha Vantage API key
2. **Create Prototype**: Implement Alpha Vantage alternative in holdings.py
3. **Update Tests**: Modify test_holdings.py to test the new implementation
4. **Document Usage**: Update README or API docs to show how to specify data source
5. **Performance Comparison**: Benchmark data recency between sources

## References
- GEMINI.md: Milestone 3 planning for refining data sources
- Alpha Vantage ETF Profile documentation: https://www.alphavantage.co/documentation/#etf-profile
- JustETF website: https://www.justetf.com/