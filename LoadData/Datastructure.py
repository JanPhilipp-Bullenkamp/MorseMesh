class Vertex:
    def __init__(self, x=None, y=None, z=None,
                quality=None, fun_val=None,
                index=None):
        self.x = x
        self.y = y
        self.z = z
        self.quality = quality
        self.fun_val = fun_val
        self.index = index

        self.star = {}
        self.star["F"] = []
        self.star["E"] = []
        
    def __str__(self):
        return str(self.index)

# indices will be read in as sets
class Edge:
    def __init__(self, indices=None, fun_val=None, index=None):
        self.indices = indices
        self.fun_val = fun_val

        self.index = index
        
    def set_fun_val(self, vertices_dict):
        self.fun_val = []
        for ind in self.indices:
            self.fun_val.append(vertices_dict[ind].fun_val)
        self.fun_val.sort(reverse=True)
        
    def __str__(self):
        return str(self.indices)


# indices will be read in as sets
class Face:
    def __init__(self, indices=None, fun_val=None, index=None):
        self.indices = indices
        self.fun_val = fun_val

        self.index = index
        
    def set_fun_val(self, vertices_dict):
        self.fun_val = []
        for ind in self.indices:
            self.fun_val.append(vertices_dict[ind].fun_val)
        self.fun_val.sort(reverse=True)
        
        
    def __str__(self):
        return str(self.indices)
    
    
class CritVertex:
    def __init__(self, vert):
        self.index = vert.index
        self.fun_val = vert.fun_val
        
        self.connected_saddles = []
        
    def __str__(self):
        return str(self.index)

# indices will be read in as sets   
class CritEdge:
    def __init__(self, edge):
        self.indices = edge.indices
        self.fun_val = edge.fun_val
        
        self.index = edge.index
        
        self.connected_minima = []
        self.connected_maxima = []
        
        self.paths = {}
        
    def __str__(self):
        return str(self.indices)
        

# indices will be read in as sets    
class CritFace:
    def __init__(self, face):
        self.indices = face.indices
        self.fun_val = face.fun_val
        
        self.index = face.index
        
        self.connected_saddles = []
        
        self.paths = {}
        
    def __str__(self):
        return str(self.indices)
    
    
class MorseComplex:
    def __init__(self, persistence=None):
        self.CritVertices = {}
        self.CritEdges = {}
        self.CritFaces = {}
        
    def add_vertex(self, vert):
        critvert = CritVertex(vert)
        self.CritVertices[vert.index] = critvert
        