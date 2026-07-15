"""
trustcalc.tools.email_tool
==========================

Email tool.

Provides controlled email sending capability.
Actual email delivery should be delegated to an
SMTP provider or API in production.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from trustcalc.tools.base import Tool


@dataclass(slots=True)
class EmailTool(Tool):
    """
    Email sending tool.
    """

    name: str = "email"

    description: str = (
        "Send an email message."
    )

    required_capability: str = "email.send"

    argument_schema = {
        "required": (
            "recipient",
            "subject",
            "body",
        ),
        "properties": {
            "recipient": str,
            "subject": str,
            "body": str,
        },
    }

    def execute(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute an email send request.

        Placeholder implementation.
        """

        recipient = kwargs["recipient"]
        subject = kwargs["subject"]
        body = kwargs["body"]

        return {
            "tool": self.name,
            "status": "not_implemented",
            "recipient": recipient,
            "subject": subject,
            "body_length": len(body),
        }