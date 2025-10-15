from ..BaseNode import BaseNode

"""
A series of nodes which operate on columns of tables.
"""

class SelectColNode(BaseNode):
    """
    Select specific columns from input table.
    
    The _index column is always preserved automatically and doesn't need to be
    specified in selected_columns.
    
    Parameters:
    - selected_columns: list of column names to keep (excluding _index which is automatic)
    """
    pass


class SplitColNode(BaseNode):
    pass
    # todo

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

class RenameColNode(BaseNode):
    pass

class CopyColNode(BaseNode):
    pass
    # todo