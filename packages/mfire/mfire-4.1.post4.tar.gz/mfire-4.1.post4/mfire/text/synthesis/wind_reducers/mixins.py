from __future__ import annotations

from abc import ABC
from typing import Optional

from mfire.settings import get_logger

LOGGER = get_logger(name=__name__, bind="reducer_mixins")


class BaseSummaryBuilderMixin(ABC):
    """SummaryBuilderMixin class."""

    TEMPLATE_KEY: str = "case"

    def __init__(self):
        self._summary: dict = {}

    @property
    def summary(self) -> dict:
        return self._summary

    @property
    def case(self) -> Optional[str]:
        # Get the case value stored in the summary.
        return self._summary.get(self.TEMPLATE_KEY)

    def _set_summary_case(self, case: str) -> None:
        # Set the wind case in the summary.
        self._summary[self.TEMPLATE_KEY] = case
