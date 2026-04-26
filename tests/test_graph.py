# tests/test_graph.py
from ethical_validator.graph import research_node, evaluate_node, CompanyState

def test_research_node_success(mocker):
    mocker.patch('ethical_validator.graph.search_company_news', return_value="Great news!")
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="")
    result = research_node(state)
    assert result == {"news": "Great news!"}

def test_research_node_error(mocker):
    mocker.patch('ethical_validator.graph.search_company_news', side_effect=Exception("API Error"))
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="")
    result = research_node(state)
    assert result == {"error": "API Error"}
    
def test_evaluate_node_skips_on_error():
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="Previous Error")
    result = evaluate_node(state)
    assert result == {}
