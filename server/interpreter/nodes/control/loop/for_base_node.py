from abc import abstractmethod
from typing import Dict, Generator, Literal, override

from server.models.data import Data

from ..control_struc_base_node import ControlStrucBaseNode

"""
Base class for For loop begin nodes.
"""

class ForBaseBeginNode(ControlStrucBaseNode):
    """
    Marks the beginning of a for loop.
    """

    @property
    @override
    def pair_type(self) -> Literal["BEGIN", "END"]:
        return "BEGIN"

    @abstractmethod
    def iter_loop(self, inputs: Dict[str, Data]) -> Generator[Dict[str, Data], None, None]:
        """
        An iterator that yields loop variables for each iteration.
        """
        pass

class ForBaseEndNode(ControlStrucBaseNode):
    """
    Marks the end of a for loop.
    """

    @property
    @override
    def pair_type(self) -> Literal["BEGIN", "END"]:
        return "END"

    @abstractmethod
    def end_iter_loop(self, loop_outputs: Dict[str, Data]) -> None:
        """
        Aggregates outputs collected from each iteration of the loop.
        This method will be called each iteration
        """
        pass

    @abstractmethod
    def finalize_loop(self) -> Dict[str, Data]:
        """
        Finalizes the loop after all iterations are complete.
        This method will be called once after the loop ends.
        """
        pass
