from abc import abstractmethod
from typing import Dict, Generator

from server.models.data import Data

from ..base_node import BaseNode

"""
Base class for For loop begin nodes.
"""

class ForBaseBeginNode(BaseNode):
    """
    Marks the beginning of a for loop.
    """

    @abstractmethod
    def iter_loop(self, inputs: Dict[str, Data]) -> Generator[Dict[str, Data], None, None]:
        """
        An iterator that yields loop variables for each iteration.
        """
        pass

class ForBaseEndNode(BaseNode):
    """
    Marks the end of a for loop.
    """
    
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
