from ..BaseNode import BaseNode, register_node

"""
A series of nodes to manipulate table rows.
"""

@register_node
class TableFilterNode(BaseNode):
    """
    A node to filter rows of a table by given condition.
    Output two subtables of input table,
    one with rows satisfying the condition, 
    the other with rows not satisfying the condition.
    """
    pass

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
