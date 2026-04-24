# tests/test_evaluator.py
from ethical_validator.evaluator import evaluate_esg_risk
from unittest.mock import patch

@patch("os.getenv")
@patch("ethical_validator.evaluator.ChatOpenAI")
def test_evaluate_esg_risk_returns_score_and_summary(mock_chat, mock_getenv):
    # Mocking environment variable
    mock_getenv.return_value = "fake_key"
    
    # Mocking the LLM response
    mock_chat.return_value.invoke.return_value.content = "Score: 7. Summary: Highly controversial."
    score, summary = evaluate_esg_risk("Test Corp", "Bad news here.")
    assert score == 7
    assert "Highly controversial" in summary
