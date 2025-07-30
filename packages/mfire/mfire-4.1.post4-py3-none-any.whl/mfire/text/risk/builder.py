from __future__ import annotations

from functools import cached_property
from typing import Optional

import numpy as np

from mfire.composite.component import RiskComponentComposite
from mfire.composite.event import EventComposite
from mfire.settings import get_logger
from mfire.text.base.builder import BaseBuilder
from mfire.text.risk.reducer import RiskReducer
from mfire.text.risk.rep_value import RepValueBuilder
from mfire.utils.wwmf import Wwmf

# Logging
LOGGER = get_logger(name="text.risk.builder.mod", bind="risk.builder")


class RiskBuilder(BaseBuilder):
    """
    This class enables to manage all text for representative values. It chooses which
    class needs to be used for each case.
    """

    reducer_class: type = RiskReducer
    reducer: Optional[RiskReducer] = None
    parent: RiskComponentComposite

    module_name: str = "risk"

    @property
    def is_multizone(self):
        return self.reducer.is_multizone

    @cached_property
    def _gusts_under_thunderstorm_event(self) -> Optional[EventComposite]:
        for lvl in self.parent.levels_of_risk(1):
            for event in lvl.events:
                if "WWMF__SOL" not in event.field.name:
                    continue

                thresholds = []
                if event.plain is not None:
                    thresholds += event.plain.threshold
                if event.mountain is not None:
                    thresholds += event.mountain.threshold
                if all(Wwmf.is_thunderstorm(ts) for ts in thresholds):
                    return event
        return None

    @property
    def is_gusts_under_thunderstorm(self) -> bool:
        return (
            self.parent.hazard_name in ["Rafales", "Vent"]
            and self._gusts_under_thunderstorm_event is not None
        )

    @property
    def template_name(self) -> str:
        if self.parent.hazard_name.startswith("ME_"):
            return "ME"
        if self.parent.hazard_name == "Neige":
            return "snow"
        if self.parent.hazard_name == "Pluies":
            return "rain"
        return "multizone" if self.is_multizone else "monozone"

    @property
    def template_key(self) -> str | np.ndarray:
        """
        Get the template key.

        Returns:
            str: The template key.
        """
        if self.parent.hazard_name.startswith("ME_"):
            parts = []
            if (
                "temporality" in self.reduction
                and not self.parent.hazard_name.endswith("_bis")
            ):
                parts.append("temp")
            if "value" in self.reduction:
                parts.append("val")
            if "localisation" in self.reduction:
                parts.append("loc")
            return "+".join(parts) if parts else "RAS"
        if self.parent.hazard_name in ["Neige", "Pluies"]:
            return self.reduction["key"]
        if self.is_multizone:
            return self.reducer.localisation.unique_name
        return self.reducer.strategy.norm_risk

    def post_process_monozone(self):
        """Processes the representative values for the monozone comment."""
        rep_value_table = {}
        for bloc, data in self.reduction.items():
            if isinstance(data, dict):
                data_dict = {
                    k: v
                    for k, v in data.items()
                    if k not in ["start", "stop", "centroid", "period"]
                }
                if data_dict:
                    rep_value_table[f"{bloc}_val"] = data_dict

        final_rep_value = {
            key: RepValueBuilder.compute_all(
                self, {k: v for k, v in value.items() if k != "level"}
            )
            for key, value in rep_value_table.items()
            if value
        }
        self.text = self.text.format(**final_rep_value)
        self.clean_text()

    def post_process_multizone(self):
        """Processes the representative values for the multizone comment."""
        self.text += " " + RepValueBuilder.compute_all(
            self, self.reducer.get_critical_values()
        )

    def post_process_snow(self):
        """Processes the representative values for the snow comment."""
        self.post_process_multizone()

        # Put the LPN (if present) at the 2nd line (#41905)
        if "LPN__SOL" in self.reducer.get_critical_values():
            text = self.text.split("\n")
            self.text = "\n".join([text[0], text[-1]] + text[1:-1])

    def post_process_gusts_under_thunderstorm(self):
        if self.reducer.final_risk_max_level == 0:
            return

        event = self._gusts_under_thunderstorm_event
        if event.values_ds["occurrence_event"].any():
            self.text += "\n" + self._("Rafales plus fortes sous orage.")

    def post_process(self):
        """Make a post-process operation on the text."""
        if not self.parent.hazard_name.startswith("ME_"):
            if self.parent.hazard_name == "Neige":
                self.post_process_snow()
            elif self.is_multizone or self.parent.hazard_name == "Pluies":
                self.post_process_multizone()
            else:
                self.post_process_monozone()

            if self.is_gusts_under_thunderstorm:
                self.post_process_gusts_under_thunderstorm()
        super().post_process()
