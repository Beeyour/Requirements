import pytest
import json

from backend.services.uml.usecase_service import generate_usecase_json, format_requirements_for_ai, generate_plantuml
from backend.enums import ReqType, ReqPriority
from backend.services.llm import call_llm
from backend.services.llm.config import DEFAULT_PROVIDER, DEFAULT_MODEL

@pytest.mark.asyncio
def test_format_requirements_logic():
    class MockRequirement:
        def __init__(self, description, req_type, is_active=True, priority=ReqPriority.HIGH):
            self.description = description
            self.type = req_type
            self.is_active = is_active
            self.priority = priority
    reqs = [
        MockRequirement("The user can login", ReqType.FUNCTIONAL),
        MockRequirement("The system should be fast", ReqType.NON_FUNCTIONAL),
        MockRequirement("Old requirement", ReqType.FUNCTIONAL, is_active=False)
    ]
    formatted_text = format_requirements_for_ai(reqs)
    assert "The user can login" in formatted_text
    assert "The system should be fast" not in formatted_text
    assert "Old requirement" not in formatted_text


@pytest.mark.asyncio
async def test_generate_usecase_prompt_structure():
    sample_req = "Dr. Ramani determines Mr. Smith is a danger to himself. She prescribes a specific medication (Nurse cannot do this) and formally detains him under the Mental Health Act (Sectioning)."
    prompt1 = await generate_usecase_json(sample_req, DEFAULT_PROVIDER, "gpt-5.4-2026-03-05") # "gpt-5.4-2026-03-05"    DEFAULT_MODEL

    prompt = generate_plantuml(json.loads(prompt1))
    print(prompt)

    assert "@startuml" in prompt
    assert "@enduml" in prompt
    assert "left to right direction" in prompt

async def test_generate_usecase_prompt_empty_error():
    with pytest.raises(ValueError):
        await generate_usecase_json("",DEFAULT_PROVIDER, DEFAULT_MODEL)











