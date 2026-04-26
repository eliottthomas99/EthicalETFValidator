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

from ethical_validator.graph import process_company_wrapper

def test_process_company_wrapper(mocker):
    # Mock the compiled graph's invoke method
    mocker.patch('ethical_validator.graph.company_graph.invoke', return_value={"company": "Test Co", "score": 5})
    # The wrapper should return a dict updating the company_results list
    result = process_company_wrapper({"company": "Test Co"})
    assert result == {"company_results": [{"company": "Test Co", "score": 5}]}

from ethical_validator.graph import fetch_node, process_holdings, ETFState

def test_fetch_node(mocker):
    mocker.patch('ethical_validator.graph.fetch_top_holdings', return_value=["Co A"])
    state = ETFState(ticker="EPAB.PA", holdings=[], company_results=[], final_report="")
    assert fetch_node(state) == {"holdings": ["Co A"]}

def test_process_holdings():
    state = ETFState(ticker="EPAB.PA", holdings=["Co A", "Co B"], company_results=[], final_report="")
    sends = process_holdings(state)
    assert len(sends) == 2
    assert sends[0].node == "process_company"
    assert sends[0].arg == {"company": "Co A"}
