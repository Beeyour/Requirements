import json
import re
from typing import Dict, Any

def parse_json_response(raw_text: str) -> Dict[str, Any]:
    # Utility to clean LLM response and extract valid JSON
    # This is critical for 2026 models that might return markdown blocks
    try:
        # Search for JSON structure within the text
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw_text)
    except (json.JSONDecodeError, AttributeError):
        # Return a safe empty structure if parsing fails
        return {}