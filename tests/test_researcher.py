# tests/test_researcher.py
from ethical_validator.researcher import search_company_news
from unittest.mock import patch

@patch("ethical_validator.researcher.os.getenv")
@patch("ethical_validator.researcher.TavilyClient")
def test_search_company_news_calls_tavily(mock_tavily, mock_getenv):
    mock_getenv.return_value = "fake_key"
    mock_tavily.return_value.search.return_value = {"results": [{"content": "Scandal found"}]}
    result = search_company_news("Test Corp")
    assert "Scandal found" in result
