# Design Spec: Graph Architecture (Milestone 2)

**Date:** 2024-04-26
**Status:** Draft
**Topic:** Transition Ethical ETF Validator to LangGraph

## 1. Goal
Refactor the linear "Walking Skeleton" pipeline into a robust, parallelized LangGraph application using the Sub-Graph (Map-Reduce) pattern. This will significantly speed up the research phase and provide a foundation for complex, stateful workflows.

## 2. Architecture: Dual-Graph Strategy
We will use a Main Graph to manage the ETF and multiple parallel Sub-Graphs to manage individual companies.

### 2.1 The Sub-Graph (Company Evaluator)
Handles the research and LLM evaluation for a single company.
*   **State (`CompanyState`):**
    *   `company: str`
    *   `news: str`
    *   `score: int`
    *   `summary: str`
    *   `error: str`
*   **Nodes:**
    *   `research_node`: Wraps `search_company_news()`.
    *   `evaluate_node`: Wraps `evaluate_esg_risk()`.
*   **Flow:** `START` -> `research_node` -> `evaluate_node` -> `END`

### 2.2 The Main Graph (ETF Orchestrator)
Manages the ETF data and orchestrates the parallel Sub-Graphs.
*   **State (`ETFState`):**
    *   `ticker: str`
    *   `holdings: List[str]`
    *   `company_results: List[CompanyState]`
    *   `final_report: str`
*   **Nodes:**
    *   `fetch_node`: Wraps `fetch_top_holdings()`.
    *   `process_holdings_node`: The Map step. Uses LangGraph's `Send` API to spawn a Sub-Graph for each holding in `ETFState["holdings"]`.
    *   `report_node`: Formats the collected `company_results` into a Markdown report and saves it.
*   **Flow:** `START` -> `fetch_node` -> `process_holdings_node` (Parallel) -> `report_node` -> `END`

## 3. Data Flow & Constraints
1.  **Input:** The Main Graph starts with `ticker` = "EPAB.PA".
2.  **Limitation Handling:** To conserve Tavily API credits during this architectural refactor, `fetch_node` will remain hardcoded to return a maximum of **3 holdings**.
3.  **Parallel Execution:** The `process_holdings_node` will execute the Sub-Graph for all 3 holdings concurrently.
4.  **Error Handling:** If a Sub-Graph fails (e.g., Tavily API timeout), it will populate the `error` field in its `CompanyState` and return, allowing the Main Graph to continue and report the failure, rather than crashing the entire pipeline.

## 4. Implementation Details
*   **Refactoring:** The existing functions in `src/ethical_validator/` (`holdings.py`, `researcher.py`, `evaluator.py`) will be reused. They will be wrapped by the new LangGraph node functions.
*   **New File:** A new file `src/ethical_validator/graph.py` will contain the State definitions and the Graph compilation logic.
*   **Update Main:** `src/ethical_validator/main.py` will be updated to invoke the compiled LangGraph instead of calling functions sequentially.

## 5. Testing Strategy
*   Unit tests for existing functions remain valid.
*   New tests will be added in `tests/test_graph.py` to verify the State schema and ensure the graph nodes transition correctly (using mocked node functions).