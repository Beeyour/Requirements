
import pytest
import json

from backend.services.uml.class_digram_service import generate_class_json, generate_class_plantuml
from backend.services.llm.config import DEFAULT_PROVIDER, DEFAULT_MODEL


@pytest.mark.asyncio
async def test_generate_class_digram_prompt_structure():
    sample_req =   "A new patient, Mr. Smith, arrives at the clinic. The Medical Receptionist searches the database to ensure he isn't already registered. Finding no record, she registers his personal details (Name, DoB, Address) and books an initial consultation slot"
    prompt1 = await generate_class_json(sample_req, DEFAULT_PROVIDER, "gpt-5.4-2026-03-05") # "gpt-5.4-2026-03-05"    DEFAULT_MODEL
    print("omar")
    print(prompt1)
    prompt = generate_class_plantuml(json.loads(prompt1))
    print(prompt)

    assert "@startuml" in prompt
    assert "@enduml" in prompt
    assert "left to right direction" in prompt
@pytest.mark.asyncio
async def test_generate_class_digram_prompt_empty_error():
    with pytest.raises(ValueError):
        await generate_class_json("",DEFAULT_PROVIDER, DEFAULT_MODEL)

