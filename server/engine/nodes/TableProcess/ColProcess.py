from ..BaseNode import BaseNode, register_node

"""
A series of nodes which operate on columns of tables.
"""

@register_node
class SelectColNode(BaseNode):
    """
    Select specific columns from input table.
    
    The _index column is always preserved automatically and doesn't need to be
    specified in selected_columns.
    
    Parameters:
    - selected_columns: list of column names to keep (excluding _index which is automatic)
    """
    pass

@register_node
class SplitColNode(BaseNode):
    pass
    # todo

@register_node
class JoinColNode(BaseNode):
    """
    A node to join two tables with given condition.
    Only support simple compare condition(==, !=, >, >=, <, <=) between two columns of the two tables.
    If user provides none condition, meas Cartesian product.
    Only support inner join.
    This node implement can be very slow.
    """
    pass
    # todo

@register_node
class RenameColNode(BaseNode):
    pass

@register_node
class CopyColNode(BaseNode):
    pass
    # todo