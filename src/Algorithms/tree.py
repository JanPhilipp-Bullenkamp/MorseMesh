##
# @file Tree.py
#
# @brief Contains Tree and Node classes.

class Tree():
    """! @brief Tree class to store a tree for pathfinding."""
    ## @var root 
    # The root of the Tree. In our case: should be the index of a critical simplex.
    ## @var children 
    # A list of Node objects that form the children of the root Node.
    ## @var pathends
    # A list of Node objects that mark the end of a path.
    ## @var Qbfs
    # \todo LOOK UP AGAIN (Breadth first search queue or so .....)
    def __init__(self,root):
        """! @brief The constructor of a Tree
        @param root The root of the Tree 
        """
        self.root = root
        self.children = []
        self.pathends = []
        self.Qbfs = []
    def addNode(self,obj):
        """! @brief Adds a Node to the Tree.
        @param obj A Node object.
        """
        self.children.append(obj)
    def addEnd(self,obj):
        """! @brief Adds a Node that markks the end of a path to the Tree.
        @param obj A Node object that is the end of a path.
        """
        self.pathends.append(obj)
        
class Node():
    """! @brief A Node class. Contains info for pathfinding and creating a Tree """
    ## @var parent
    # The parent Node
    ## @var data 
    # The info for this Node.
    ## @var end_flag
    # Bool whether this is an end node.
    ## @var children
    # A list of Node objects that form the children of this Node.
    def __init__(self, data, parent, end_flag=False):
        """! @brief The constructor of a Node.
        @param data The index of the simplex assigned to this Node.
        @param parent The parent Node of this Node.
        @param end_flag (Optional) Boolean. Defualt is False. Tells whether this Node tís the end of a Path
        """
        self.parent = parent
        self.data = data
        self.end_flag = False
        self.children = []
    def addNode(self,obj):
        """! @brief Adds a Node to the Tree.
        @param obj A Node object.
        """
        self.children.append(obj)
        