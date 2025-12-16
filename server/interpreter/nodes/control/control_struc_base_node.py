from abc import abstractmethod
from typing import Literal

from ..base_node import BaseNode


class ControlStrucBaseNode(BaseNode):
    """
    Base class for control flow nodes.
    Used for nodes that define control structures like loops.
    """

    pair_id: int  # ID to link with its corresponding pair node

    @property
    @abstractmethod
    def pair_type(self) -> Literal["BEGIN", "END"]:
        """
        Returns the type of the pair node: "BEGIN" or "END".
        """
        pass

    @property
    def pair_info(self) -> tuple[int, Literal["BEGIN", "END"]]:
        """
        Returns a tuple of (pair_id, pair_type) for this control node.
        """
        return self.pair_id, self.pair_type
