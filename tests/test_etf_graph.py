import pytest
from ethical_validator.etf_graph import process_company_wrapper, fetch_node, process_holdings, ETFState

def test_process_company_wrapper(mocker):
    mocker.patch('ethical_validator.etf_graph.company_graph.invoke', return_value={"company": "Test Co", "score": 5})
    result = process_company_wrapper({"company": "Test Co"})
    assert result == {"company_results": [{"company": "Test Co", "score": 5}]}

def test_fetch_node(mocker):
    mocker.patch('ethical_validator.etf_graph.fetch_top_holdings', return_value=["Co A"])
    state = ETFState(ticker="EPAB.PA", holdings=[], company_results=[], final_report="")
    assert fetch_node(state) == {"holdings": ["Co A"]}

def test_process_holdings():
    state = ETFState(ticker="EPAB.PA", holdings=["Co A", "Co B"], company_results=[], final_report="", api_key="", model="nvidia/nemotron-3-super-120b-a12b:free")
    sends = process_holdings(state)
    assert len(sends) == 2
    assert sends[0].node == "process_company"
    assert sends[0].arg == {"company": "Co A", "api_key": "", "model": "nvidia/nemotron-3-super-120b-a12b:free"}
