import pytest
from unittest.mock import patch
from services.ai_agent import check_saturation  # تأكد من وجود services.




@patch("services.ai_agent.call_llm") # تأكد من وجود services. هنا أيضاً
def test_check_saturation_success(mock_call_llm):
    mock_llm_response = """
    ```json
    {
        "is_saturated": true,
        "coverage_percentage": 95,
        "missing_areas": []
    }
    ```
    """

    mock_call_llm.return_value = mock_llm_response
    fake_history = [{"role": "user", "content": "I want a login page."}]
    result = check_saturation(
        conversation_history=fake_history,
        provider="openai",
        model="gpt-5.4-nano"
    )
    assert result["is_saturated"] is True
    assert result["coverage_percentage"] == 95
    assert len(result["missing_areas"]) == 0
    mock_call_llm.assert_called_once()


@patch("services.ai_agent.call_llm") 
def test_check_saturation_failure_fallback(mock_call_llm):
    mock_call_llm.return_value = "Hello, I am an AI and I didn't understand the format."
    fake_history = [{"role": "user", "content": "Hello"}]

    result = check_saturation(fake_history, "openai", "gpt-5.4-nano")
    assert result["is_saturated"] is False
    assert result["coverage_percentage"] == 0
    assert result["missing_areas"] == []