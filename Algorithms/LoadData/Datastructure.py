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
    
class Separatrix:
    def __init__(self, origin, destination, dimension, path, separatrix_persistence):
        # integer indices
        self.origin = origin
        self.destination = destination
        
        # minimal lines: dim = 1
        # maximal lines: dim = 2
        if dimension == 1 or dimension == 2:
            self.dimension = dimension
        else:
            raise ValueError('Dimension must be 1 (minimal line) or 2 (maximal line)!')
        
        # list
        self.path = path
        
        # float
        self.separatrix_persistence = separatrix_persistence
        
    def __str__(self):
        if self.dimension == 1:
            return "Minimal line from saddle" + str(self.origin) + " to minimum" + str(self.destination) + " in " + str(len(path)) + " pathpoints"
        elif self.dimension == 2:
            return "Maximal line from maximum" + str(self.origin) + " to saddle" + str(self.destination) + " in " + str(len(path)) + " pathpoints"
    
    
class MorseComplex:
    def __init__(self, persistence=0, filename=None):
        self.CritVertices = {}
        self.CritEdges = {}
        self.CritFaces = {}
        
        self.Separatrices = []
        
        self._flag_BettiNumbers = False
        self.BettiNumbers = None
        
        self.maximalReduced = False
        self.persistence = persistence
        self.filename = filename
        
    def add_vertex(self, vert):
        critvert = CritVertex(vert)
        self.CritVertices[vert.index] = critvert
        
        
    def info(self):
        print("+-------------------------------------------------------")
        print("| MorseComplex Info")
        print("+-------------------------------------------------------")
        if self.filename != None:
            print("| Filename: ", self.filename)
        if self.persistence != None:
            print("| Persistence of this Complex: ", self.persistence)
            print("+-------------------------------------------------------")
        print("| Number of Vertices: ", len(self.CritVertices))
        print("| Number of Edges: ", len(self.CritEdges))
        print("| Number of Faces: ", len(self.CritFaces))
        print("+-------------------------------------------------------")
        print("| Euler characteristic: ", len(self.CritVertices) - len(self.CritEdges) +len(self.CritFaces))
        if self._flag_BettiNumbers:
            print("| Betti numbers: ", self.BettiNumbers)
        print("+-------------------------------------------------------")
        