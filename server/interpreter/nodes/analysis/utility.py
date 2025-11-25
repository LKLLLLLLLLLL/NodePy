from ..base_node import BaseNode, register_node

"""
A series of utility help nodes.
"""

@register_node()
class SeqAnalyseNode(BaseNode):
    """
    A node to analyze sequence data, cumulate the frequency of each element in sepecified column.
    Import must be a table.
    Export a new table with two columns: element and frequency.
    """

@register_node()
class AccumulateNode(BaseNode):
    """
    A node to accumulate values in a specified columns.
    Import must be a table.
    Export a new table with specified columns and one row, containing the accumulated values.
    The accumulated operation can be sum, average, max, min.
    """

@register_node()
class RowDifNode(BaseNode):
    """
    A node to calculate the difference of specified column between each row and the previous row.
    Export a new table with the specific column, and n-1 rows, where n is the number of rows in the input table.
    """
