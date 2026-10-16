import re
import json
from typing import List, Optional, Any

class DenialFeedbackRedactor:
    def __init__(self, secrets: List[str], patterns: Optional[List[str]] = None):
        self.secrets = secrets
        self.patterns = patterns or [r"API_KEY=\w+", r"PASSWORD=\w+", r"TOKEN=\w+"]

    def redact(self, message: str) -> str:
        if not isinstance(message, str):
            return message
        for secret in self.secrets:
            message = message.replace(secret, "[REDACTED]")
        for pattern in self.patterns:
            message = re.sub(pattern, "[REDACTED]", message)
        try:
            parsed = json.loads(message)
            message = json.dumps(self._redact_json(parsed))
        except (json.JSONDecodeError, TypeError):
            pass
        return message

    def _redact_json(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self._redact_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._redact_json(v) for v in data]
        elif isinstance(data, str):
            return self.redact(data)
        else:
            return data
