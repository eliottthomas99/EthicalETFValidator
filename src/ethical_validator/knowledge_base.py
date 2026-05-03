# src/ethical_validator/knowledge_base.py
import json
import os
import re
from datetime import datetime
from typing import Any

from langchain_openai import ChatOpenAI


def _slugify(company: str) -> str:
    """Create a filesystem-safe slug from a company name."""
    return re.sub(r"[^\w\-]", "_", company).lower()


def _kb_path(company: str) -> str:
    """Return the JSON file path for a company's knowledge base."""
    slug = _slugify(company)
    return os.path.join("knowledge_base", f"{slug}.json")


def _load_kb(company: str) -> dict[str, Any]:
    """Load a company's knowledge base from disk, or return an empty structure."""
    path = _kb_path(company)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"company": company, "items": []}


def _save_kb(company: str, data: dict[str, Any]) -> None:
    """Save a company's knowledge base to disk."""
    os.makedirs("knowledge_base", exist_ok=True)
    path = _kb_path(company)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)


def _count_raw_items(items: list[dict]) -> int:
    """Count how many items are of type 'raw'."""
    return sum(1 for item in items if item.get("type") == "raw")


def _summarize_items(company: str, items: list[dict], api_key: str = "") -> dict[str, Any]:
    """Use the LLM to summarize a list of raw items into one summary item."""
    if not api_key:
        raise RuntimeError("api_key is required.")

    llm = ChatOpenAI(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )

    raw_texts = []
    for item in items:
        if item.get("type") == "raw":
            text = item.get("text", "")
            url = item.get("source_url", "")
            raw_texts.append(f"Source: {url}\n{text}")

    combined = "\n\n---\n\n".join(raw_texts)

    prompt = f"""
You are an expert ESG analyst. The following are news snippets about {company}.

{combined}

Please provide a concise 2-3 sentence summary of the key ethical, environmental, or governance issues mentioned.
Focus on the most important and recurring themes.
"""

    response = llm.invoke(prompt).content.strip()

    return {
        "type": "summary",
        "text": response,
        "summarized_count": len(raw_texts),
        "date_summarized": datetime.now().isoformat()
    }


def _compact_raw_items(data: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
    """If there are 5+ raw items, compact them into a single summary."""
    items = data.get("items", [])
    raw_items = [item for item in items if item.get("type") == "raw"]

    if len(raw_items) >= 5:
        summary = _summarize_items(data["company"], raw_items, api_key=api_key)
        # Remove raw items and add summary
        data["items"] = [item for item in items if item.get("type") != "raw"]
        data["items"].append(summary)

    return data


def _compact_all_items(data: dict[str, Any], api_key: str = "") -> dict[str, Any]:
    """If total items >= 10, compact everything into a single master summary."""
    items = data.get("items", [])

    if len(items) >= 10:
        # Combine all item texts and ask LLM for a single summary
        if not api_key:
            raise RuntimeError("api_key is required.")

        llm = ChatOpenAI(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )

        combined_texts = []
        total_summarized = 0
        for item in items:
            if item.get("type") == "raw":
                combined_texts.append(item.get("text", ""))
                total_summarized += 1
            elif item.get("type") == "summary":
                combined_texts.append(item.get("text", ""))
                total_summarized += item.get("summarized_count", 1)

        combined = "\n\n---\n\n".join(combined_texts)

        prompt = f"""
You are an expert ESG analyst. The following are summaries and news snippets about {data['company']}.

{combined}

Please provide a comprehensive 2-3 sentence summary of all the ethical, environmental, or governance issues mentioned.
"""

        response = llm.invoke(prompt).content.strip()

        master_summary = {
            "type": "summary",
            "text": response,
            "summarized_count": total_summarized,
            "date_summarized": datetime.now().isoformat()
        }

        data["items"] = [master_summary]

    return data


def add_news_items(company: str, news_results: list[dict[str, str]], api_key: str = "") -> dict[str, Any]:
    """
    Add new DuckDuckGo news results to a company's knowledge base.
    Triggers compaction if thresholds are met.
    Returns the updated knowledge base data.
    """
    data = _load_kb(company)

    for result in news_results:
        item = {
            "type": "raw",
            "text": result.get("body", ""),
            "source_url": result.get("href", ""),
            "date_added": datetime.now().isoformat()
        }
        data["items"].append(item)

    # First: compact raw items if >= 5
    data = _compact_raw_items(data, api_key=api_key)

    # Second: compact everything if total >= 10
    data = _compact_all_items(data, api_key=api_key)

    _save_kb(company, data)
    return data


def get_accumulated_context(company: str) -> str:
    """
    Return a formatted string of all accumulated knowledge for a company,
    suitable for passing to the evaluator LLM.
    """
    data = _load_kb(company)
    items = data.get("items", [])

    if not items:
        return "No accumulated knowledge about this company yet."

    lines = [f"# Accumulated Knowledge for {company}", ""]
    for i, item in enumerate(items, 1):
        if item.get("type") == "summary":
            lines.append(f"## Summary {i} (based on {item.get('summarized_count', '?')} items)")
            lines.append(item.get("text", ""))
        else:
            lines.append(f"## Item {i}")
            lines.append(item.get("text", ""))
        lines.append("")

    return "\n".join(lines)
