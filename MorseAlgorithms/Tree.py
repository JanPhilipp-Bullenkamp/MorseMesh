class Tree():
    def __init__(self,root):
        self.root = root
        self.children = []
        self.pathends = []
        self.Qbfs = []
    def addNode(self,obj):
        self.children.append(obj)
    def addEnd(self,obj):
        self.pathends.append(obj)
        
class Node():
    def __init__(self, data, parent, end_flag=False):
        self.parent = parent
        self.data = data
        self.end_flag = False
        self.children = []
    def addNode(self,obj):
        self.children.append(obj)
        