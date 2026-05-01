# tests/test_researcher.py
from unittest.mock import patch, MagicMock

from ethical_validator.researcher import search_company_news


@patch("ethical_validator.researcher.DDGS")
def test_search_company_news_calls_ddgs(mock_ddgs_class):
    mock_ddgs = MagicMock()
    mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs
    mock_ddgs.text.return_value = [
        {"body": "Scandal found"},
        {"body": "Another scandal"},
    ]

    result = search_company_news("Test Corp")

    mock_ddgs.text.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["body"] == "Scandal found"
    assert result[1]["body"] == "Another scandal"
