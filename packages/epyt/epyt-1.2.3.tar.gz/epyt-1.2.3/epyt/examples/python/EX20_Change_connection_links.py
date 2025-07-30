""" Change connection of the links
 
    This example contains:
        Load network.
        Get all link node indices.
        Set link node indices for specific link index.
        Unload library.
        
"""
from epyt import epanet

d = epanet('Net1.inp')

# Examples: >> help d.getLinkNodesIndex
linkIndex = 3
# d.getLinkNameID  d.getNodeNameID

# Get all link node indices
linkNodes = d.getLinkNodesIndex(linkIndex)
print(linkNodes)

# Examples: >>> help (d.setLinkNodesIndex)
startNode = 2
endNode = 4
# Set link node indices for specific link index
d.setLinkNodesIndex(linkIndex, startNode, endNode)
print(d.getLinkNodesIndex(linkIndex))

# Unload library
d.unload()
