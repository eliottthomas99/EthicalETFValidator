# src/ethical_validator/evaluator.py
import os
import re
from langchain_openai import ChatOpenAI

def evaluate_esg_risk(company: str, news: str, accumulated_knowledge: str = "") -> tuple[int, str]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not found in environment.")

    llm = ChatOpenAI(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )

    context_parts = []
    if accumulated_knowledge and accumulated_knowledge.strip():
        context_parts.append(f"## Previously Accumulated Knowledge\n{accumulated_knowledge}")
    context_parts.append(f"## Fresh News\n{news}")
    combined_context = "\n\n".join(context_parts)

    prompt = f"""
You are an expert ESG auditor. Review the following information about {company}:

{combined_context}

Consider both the accumulated historical knowledge and the fresh news. Look for patterns, recurring issues, and new developments.

Assess the risk of greenwashing or unethical practices on a scale of 1-10 (1=Low Risk, 10=Extreme Risk).
Format your response EXACTLY as:
Score: [Number]
Summary: [2-sentence justification]
"""

    response = llm.invoke(prompt).content

    # Loud parsing logic
    score_match = re.search(r"Score:\s*(\d+)", response)
    summary_match = re.search(r"Summary:\s*(.*)", response, re.DOTALL)

    if not score_match or not summary_match:
        raise RuntimeError(f"LLM failed to follow format. Response was: {response}")

    return int(score_match.group(1)), summary_match.group(1).strip()
