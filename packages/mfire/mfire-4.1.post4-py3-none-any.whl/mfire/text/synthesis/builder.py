from __future__ import annotations

from abc import abstractmethod
from typing import Optional

import numpy as np

from mfire.composite.component import SynthesisModule
from mfire.text.base.builder import BaseBuilder


class SynthesisBuilder(BaseBuilder):
    """
    SynthesisBuilder class that must build synthesis texts
    """

    module_name: str = "synthesis"
    parent: Optional[SynthesisModule] = None

    def compute(self) -> Optional[str]:
        """
        Generate the text according to the weather composite

        Returns:
            Built text.
        """
        return super().compute() if self.parent.check_condition(self.geo_id) else None

    @property
    @abstractmethod
    def template_name(self) -> str:
        """
        Get the template name.

        Returns:
            str: The template name.
        """

    @property
    @abstractmethod
    def template_key(self) -> Optional[str | np.ndarray]:
        """
        Get the template key.

        Returns:
            str | np.ndarray: The template key.
        """
