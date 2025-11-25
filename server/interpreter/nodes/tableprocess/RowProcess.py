from ..base_node import BaseNode, register_node

"""
A series of nodes to manipulate table rows.
"""

@register_node
class TableRowAppendNode(BaseNode):
    """
    A node to append rows from one table to another.
    Both tables must have the same columns.
    """
    pass

@register_node
class TableSortNode(BaseNode):
    """
    A node to sort rows of a table by given column.
    """
    pass
