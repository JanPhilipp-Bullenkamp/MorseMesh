class Skeleton:
    def __init__(self) -> None:
        self.Nodes = []
        self.Edges = []

class Node:
    def __init__(self, index: int, dimension: int) -> None:
        self.index = index
        self.type = dimension
        self.neighbors = []

class Edge:
    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end
        self.path = []