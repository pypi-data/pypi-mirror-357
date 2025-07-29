__version__ = "1.0.0"

import json


def format_json(unformatted: str, _info_str: str) -> str:
    parsed = json.loads(unformatted)
    return json.dumps(parsed, indent=2) + "\n"
