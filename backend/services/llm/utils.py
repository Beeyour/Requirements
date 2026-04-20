import json
import re
from typing import Any


def parse_json_response(text: str) -> Any:
    """Strip optional markdown fences then parse JSON."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "",  cleaned.strip(), flags=re.MULTILINE)
    return json.loads(cleaned.strip())

