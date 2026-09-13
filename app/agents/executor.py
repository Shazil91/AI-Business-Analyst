from __future__ import annotations

import inspect
import logging
from datetime import date
from typing import Any

from app.tools.registry import ToolRegistry


logger = logging.getLogger(__name__)


class Executor:
    """
    Executes functions exposed by registered business tools.

    Supports both synchronous and asynchronous tool functions.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ):
        self.registry = registry or ToolRegistry()

    @staticmethod
    def _convert_dates(
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Convert YYYY-MM-DD strings into datetime.date objects.

        Gemini function calling returns dates as strings.
        """

        converted = dict(parameters)

        for field in (
            "start_date",
            "end_date",
        ):

            value = converted.get(field)

            if value is None:
                continue

            if isinstance(value, date):
                continue

            if isinstance(value, str):

                try:
                    converted[field] = date.fromisoformat(
                        value
                    )

                except ValueError as exc:
                    raise ValueError(
                        f"Invalid {field}: '{value}'. "
                        "Expected YYYY-MM-DD."
                    ) from exc

        return converted

    async def run(
        self,
        tool_group: str,
        function_name: str,
        **parameters: Any,
    ) -> Any:

        if not tool_group:
            raise ValueError(
                "tool_group cannot be empty."
            )

        if not function_name:
            raise ValueError(
                "function_name cannot be empty."
            )

        tool = self.registry.get(
            tool_group
        )

        if tool is None:
            raise ValueError(
                f"Tool group '{tool_group}' "
                "is not registered."
            )

        function = getattr(
            tool,
            function_name,
            None,
        )

        if function is None:
            raise ValueError(
                f"Function '{function_name}' "
                f"does not exist in tool "
                f"'{tool_group}'."
            )

        if not callable(function):
            raise ValueError(
                f"'{tool_group}.{function_name}' "
                "is not callable."
            )

        parameters = self._convert_dates(
            parameters
        )

        logger.info(
            "Executing tool %s.%s with parameters=%s",
            tool_group,
            function_name,
            parameters,
        )

        try:

            result = function(
                **parameters
            )

            if inspect.isawaitable(result):
                result = await result

            logger.info(
                "Tool %s.%s executed successfully.",
                tool_group,
                function_name,
            )

            return result

        except TypeError as exc:

            logger.exception(
                "Invalid parameters for %s.%s",
                tool_group,
                function_name,
            )

            raise TypeError(
                f"Invalid parameters for "
                f"'{tool_group}.{function_name}': {exc}"
            ) from exc

        except Exception as exc:

            logger.exception(
                "Tool execution failed: %s.%s",
                tool_group,
                function_name,
            )

            raise RuntimeError(
                f"Tool execution failed: "
                f"'{tool_group}.{function_name}': {exc}"
            ) from exc