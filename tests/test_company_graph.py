import pytest
from ethical_validator.company_graph import research_node, evaluate_node, CompanyState

def test_research_node_success(mocker):
    mocker.patch('ethical_validator.company_graph.search_company_news', return_value=[{"body": "Great news!", "href": ""}])
    mocker.patch('ethical_validator.company_graph.add_news_items', return_value={"company": "Test Co", "items": []})
    mocker.patch('ethical_validator.company_graph.get_accumulated_context', return_value="Test context")
    state = CompanyState(company="Test Co", news="", accumulated_knowledge="", score=0, summary="", error="", api_key="", model="")
    result = research_node(state)
    assert result["news"] == "Great news!"
    assert "accumulated_knowledge" in result

def test_research_node_error(mocker):
    mocker.patch('ethical_validator.company_graph.search_company_news', side_effect=Exception("API Error"))
    state = CompanyState(company="Test Co", news="", accumulated_knowledge="", score=0, summary="", error="", api_key="", model="")
    result = research_node(state)
    assert result == {"error": "API Error"}

def test_evaluate_node_skips_on_error():
    state = CompanyState(company="Test Co", news="", accumulated_knowledge="", score=0, summary="", error="Previous Error", api_key="", model="")
    result = evaluate_node(state)
    assert result == {}
