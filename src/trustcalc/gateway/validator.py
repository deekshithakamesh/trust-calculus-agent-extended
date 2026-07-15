"""
trustcalc.gateway.validator
===========================

Gateway request validation.

Responsible for validating:

    • Tool existence
    • Tool metadata
    • Required arguments
    • Argument structure

Security decisions are NOT made here.

Author
------
Trust Calculus Research Prototype
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from trustcalc.gateway.exceptions import (
    InvalidArgumentError,
    InvalidToolError,
)


@dataclass(slots=True)
class GatewayValidator:
    """
    Performs structural validation before policy enforcement.
    """

    # ---------------------------------------------------------
    # Tool Validation
    # ---------------------------------------------------------

    def validate_tool(
        self,
        tool: Any,
    ) -> None:
        """
        Validate that a tool exposes the required interface.
        """

        if tool is None:
            raise InvalidToolError(
                "Tool does not exist."
            )

        required = (
            "execute",
            "name",
        )

        for attribute in required:

            if not hasattr(tool, attribute):

                raise InvalidToolError(
                    f"Tool missing required attribute '{attribute}'."
                )

    # ---------------------------------------------------------
    # Argument Validation
    # ---------------------------------------------------------

    def validate_arguments(
        self,
        tool: Any,
        arguments: dict[str, Any],
    ) -> None:
        """
        Validate request arguments.
        """

        if arguments is None:

            raise InvalidArgumentError(
                "Arguments cannot be None."
            )

        if not isinstance(arguments, dict):

            raise InvalidArgumentError(
                "Arguments must be a dictionary."
            )

        schema = getattr(
            tool,
            "argument_schema",
            {},
        )

        for field in schema.get(
            "required",
            (),
        ):

            if field not in arguments:

                raise InvalidArgumentError(
                    f"Missing required argument '{field}'."
                )
        # ---------------------------------------------------------
    # Schema Validation
    # ---------------------------------------------------------

    def validate_schema(
        self,
        tool: Any,
        arguments: dict[str, Any],
    ) -> None:
        """
        Validate argument types using the tool schema.

        Expected schema format:

        {
            "properties": {
                "email": str,
                "count": int,
            }
        }
        """

        schema = getattr(
            tool,
            "argument_schema",
            {},
        )

        properties = schema.get(
            "properties",
            {},
        )

        for key, expected_type in properties.items():

            if key not in arguments:
                continue

            if not isinstance(
                arguments[key],
                expected_type,
            ):

                raise InvalidArgumentError(
                    f"Argument '{key}' must be "
                    f"{expected_type.__name__}."
                )

    # ---------------------------------------------------------
    # Full Validation
    # ---------------------------------------------------------

    def validate(
        self,
        tool: Any,
        arguments: dict[str, Any],
    ) -> None:
        """
        Perform all structural validation.
        """

        self.validate_tool(
            tool,
        )

        self.validate_arguments(
            tool,
            arguments,
        )

        self.validate_schema(
            tool,
            arguments,
        )