##
# @file Datastructure.py
#
# @brief Stores data classes we will use in the mesh class.
#
# @section normal_mesh_parts Normal Mesh Parts
# - Vertex class
# - Edge class
# - Face class
#
# @section critical_simplices Critical Simplices
# - CritVertex class
# - CritEdge class
# - CritFace class
#
# @section morse_complex_related Morse Complex Related
# - Separatrix
# - MorseComplex


class Vertex:
    """! @brief Vertex class used for normal vertices and their properties.
    
    @details Stores the following properties of a vertex:
    - x,y and z coordinate
    - a quality value
    - a function value
    - an index
    
    - two angles theta and phi (for normals e.g.)
    
    - a star dictionary with keys "F", which can store the adjacent face-indices in a list, 
      and "E", which can store the adjacent edge-indices in a list
    - a set .neighbors to store the neighbors of the vertex
    """
    ## @var x 
    # The x coordinate. Should be a float or None.
    ##  @var y 
    # The y coordinate. Should be a float or None.
    ##  @var z 
    # The z coordinate. Should be a float or None.
    ##  @var quality 
    # The quality field. Should be a float or None.
    ##  @var fun_val 
    # The function value used for the Morse function. Should be a float or None.
    ##  @var index 
    # The index of the vertex. Should be an int or None.
    
    ##  @var theta 
    # An angle for a normal direction e.g. Should be a float or None.
    ##  @var phi 
    # An angle for a normal direction e.g. Should be a float or None.
    
    ##  @var star 
    # The surrounding faces "F" and edges "E" in a dictionary with keys "F" and "E".
    ##  @var neighbors 
    # A set containing all neighbor vertices (their indices).
    
    def __init__(self, x=None, y=None, z=None,
                quality=None, fun_val=None,
                index=None):
        """! The Constructor of a Vertex
        @param x The x coordinate of the vertex. Default is None.
        @param y The y coordinate of the vertex. Default is None.
        @param z The z coordinate of the vertex. Default is None.
        @param quality The quality of the vertex. Default is None.
        @param fun_val The function value of the vertex. Default is None.
        @param index The index of the vertex. Default is None.
        """
        self.x = x #float
        self.y = y #float
        self.z = z #float
        self.quality = quality #float
        self.fun_val = fun_val #float
        self.index = index #int
        
        self.theta = None #float
        self.phi = None #float

        self.star = {}
        self.star["F"] = [] #list
        self.star["E"] = [] #list
        self.neighbors = set() #set
        
        # needed for Morse Cells
        self.label = -1 #int
        self.boundary = False #bool
        
    def has_neighbor_label(self, vert_dict):
        neighbor_labels = set()
        neighbor_indices = []
        for elt in self.neighbors:
            if vert_dict[elt].label != -1 and vert_dict[elt].label != self.label:
                neighbor_indices.append([elt, vert_dict[elt].label])
                neighbor_labels.add(vert_dict[elt].label)
        return neighbor_labels, neighbor_indices
        
    def __str__(self):
        """! Retrieves the index of the vertex.
        @return A string of the index of the vertex.
        """
        return str(self.index)

class Edge:
    """! @brief Edge class used for normal edges.
    
    @details Stores an edge as a set of two indices (representing two vertices). 
    Each edge has an own index (edge-index). 
    
    Can set the function value of the edge by taking the two function values of the 
    vertices and storing them in a list, sorted such that the higher function value
    is at the first position.    
    """
    ## @var indices
    # A set of two indices representing the edge
    ## @var fun_val
    # A sorted list of two floats, where the first value is the highest
    ## @var index
    # The index of this edge (edge-index)
    
    def __init__(self, indices=None, index=None):
        """! The Constructor of an Edge.
        @param indices A set of two indices representing the two vertices of the edge. Default is None.
        @param index The index of this edge. Default is None. 
        """
        self.indices = indices #set
        self.fun_val = None #list

        self.index = index #int
        
    def set_fun_val(self, vertices_dict):
        """! @brief Sets the function value of the edge.
        @details Uses the two function values of the vertices and sorts them such 
        that the first value is the larger function value.
        
        @param vertices_dict The dictionary, where the vertices are stored. Keys should be the 
        indices of the vertices.
        """
        self.fun_val = []
        for ind in self.indices:
            self.fun_val.append(vertices_dict[ind].fun_val)
        self.fun_val.sort(reverse=True)
        
    def __str__(self):
        """! Retrieves the index of the edge.
        @return A string of the index of the edge.
        """
        return str(self.indices)

class Face:
    """! @brief Face class used for normal faces.
    
    @details Stores a face as a set of three indices (representing three vertices). 
    Each face has an own index (face-index). 
    
    Can set the function value of the face by taking the three function values of the 
    vertices and storing them in a list, sorted such that the highest function value
    is at the first position.    
    """
    ## @var indices
    # A set of three indices representing the face
    ## @var fun_val
    # A sorted list of three floats, where the first value is the highest
    ## @var index
    # The index of this face (face-index)
    
    def __init__(self, indices=None, index=None):
        """! The Constructor of a Face.
        @param indices A set of three indices representing the three vertices of the edge. Default is None.
        @param index The index of this face. Default is None. 
        """
        self.indices = indices #set
        self.fun_val = None #list

        self.index = index #int
        
    def set_fun_val(self, vertices_dict):
        """! @brief Sets the function value of the face.
        @details Uses the three function values of the vertices and sorts them such 
        that the first value is the largest function value.
        
        @param vertices_dict The dictionary, where the vertices are stored. Keys should be the 
        indices of the vertices.
        """
        self.fun_val = []
        for ind in self.indices:
            self.fun_val.append(vertices_dict[ind].fun_val)
        self.fun_val.sort(reverse=True)
        
        
    def __str__(self):
        """! Retrieves the index of the face.
        @return A string of the index of the face.
        """
        return str(self.indices)
    
class CritVertex:
    """! @brief CritVertex class used for critical vertices.
    
    @details Stores the index and function value of a critical vertex. Further 
    contains a list with saddles (critical edges) connected to this critical 
    vertex (.connected_saddles).
    """
    ## @var index
    # The index of the original Vertex that now becomes a critical vertex.
    ## @var fun_val
    # The function value of the original Vertex that now becomes a critical vertex.
    ## @var connected_saddles
    # A list with saddles (critical edges) which are connected to this critical vertex
    # via separatrices.
    
    def __init__(self, vert):
        """! The Constructor of a CritVertex.
        @param vert A Vertex class object.
        """
        self.index = vert.index #int
        self.fun_val = vert.fun_val #float
        
        self.connected_saddles = []
        
    def __str__(self):
        """! Retrieves the index of the critical vertex.
        @return A string of the index of the critical vertex.
        """
        return str(self.index)
    
class CritEdge:
    """! @brief CritEdge class used for critical edges.
    
    @details Stores the indices, function values and edge-index of a critical edge. Further 
    contains a list with minima and a list with maxima (critical vertices and faces) 
    connected to this critical edge (.connected_minima and .connected_maxima). Also contains
    a paths dictionary (.paths) (?needed for MorseComplex computations?).
    """
    ## @var indices
    # The indices representing the original edge that now becomes a critical edge.
    ## @var index
    # The index of the original Edge that now becomes a critical edge.
    ## @var fun_val
    # The function values list of the original Edge that now becomes a critical edge.
    ## @var connected_minima
    # A list with minima (critical vertices) which are connected to this critical edge
    # via separatrices.
    ## @var connected_maxima
    # A list with maxima (critical faces) which are connected to this critical edge
    # via separatrices.
    ## @var paths
    # A dictionary used in MorseComplex computation, to create the breadth first search
    # to find the critical vertices that are connected to this edge.
    
    def __init__(self, edge):
        """! The Constructor of a CritEdge.
        @param edge An Edge class object.
        """
        self.indices = edge.indices #set
        self.fun_val = edge.fun_val #list
        
        self.index = edge.index #int
        
        self.connected_minima = []
        self.connected_maxima = []
        
        self.paths = {}
        
    def __str__(self):
        """! Retrieves the index of the critical edge.
        @return A string of the index of the critical edge.
        """
        return str(self.indices)
    
class CritFace:
    """! @brief CritFace class used for critical faces.
    
    @details Stores the indices, function values and face-index of a critical face. 
    Further contains a list with saddles (critical edges) connected to this critical 
    vertex (.connected_saddles) and a paths dictionary (.paths) (?needed for 
    MorseComplex computations?).
    """
    ## @var indices
    # The indices representing the original face that now becomes a critical face.
    ## @var index
    # The index of the original Face that now becomes a critical face.
    ## @var fun_val
    # The function values list of the original Face that now becomes a critical face.
    ## @var connected_saddles
    # A list with saddles (critical edges) which are connected to this critical face
    # via separatrices.
    ## @var paths
    # A dictionary used in MorseComplex computation, to create the breadth first search
    # to find the critical edges that are connected to this face.
    
    def __init__(self, face):
        """! The Constructor of a CritFace.
        @param face A Face class object.
        """
        self.indices = face.indices #set
        self.fun_val = face.fun_val #list
        
        self.index = face.index #int
        
        self.connected_saddles = []
        
        self.paths = {}
        
    def __str__(self):
        """! Retrieves the index of the critical face.
        @return A string of the index of the critical face.
        """
        return str(self.indices)
    
class Separatrix:
    """! @brief Separatrix class used for separatrices from maxima to saddles and from saddles to minima.
    
    @details Stores a separatrix between maximum and saddle (dimension 2) or between saddle and minimum 
    (dimension 1). Origin and destination are stored, as well as the path (alternating sequence of 1-/2- or 
    0-/1-simplices) and a float for the separatrix persistence, that gives a value for the significance 
    of this separatrix line.
    """
    ## @var origin 
    # The higher dimensional critical simplex where this separatrix starts from.
    ## @var destination 
    # The lower dimensional critical simplex where this separatrix is going to.
    ## @var dimension 
    # Can be 1 or 2: 1 for minimal lines (saddle-minimum) and 2 for maximal lines:
    # (maximum-saddle).
    ## @var path 
    # A list containing the alternating (1-2-1-2... or 0-1-0-1...) indices of a vertex/edge/face 
    # that give the path from the origin to the destination.
    ## @var separatrix_persistence 
    # A float that gives a measure of importance for this separatrix.
    
    def __init__(self, origin, destination, dimension, path, separatrix_persistence):
        """! The Constructor of a Separatrix.
        @param origin The higher dimensional critical simplex where this separatrix starts from.
        @param destination The lower dimensional critical simplex where this separatrix is going to.
        @param dimension Can be 1 or 2: 1 for minimal lines (saddle-minimum) and 2 for maximal lines:
        (maximum-saddle).
        @param path A list containing the alternating (1-2-1-2... or 0-1-0-1...) indices of a vertex/edge/face 
        that give the path from the origin to the destination.
        @param separatrix_persistence A float that gives a measure of importance for this separatrix.
        """
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
        """! Retrieves information on this separatrix.
        @return A string telling wether its a minimal or maximal line, origin, destination and the length of the path.
        """
        if self.dimension == 1:
            return "Minimal line from saddle" + str(self.origin) + " to minimum" + str(self.destination) + " in " + str(len(path)) + " pathpoints"
        elif self.dimension == 2:
            return "Maximal line from maximum" + str(self.origin) + " to saddle" + str(self.destination) + " in " + str(len(path)) + " pathpoints"
        
    
class MorseComplex:
    """! @brief A Morse Complex, that stores a reduced skeleton of the original mesh/simplicial complex and has the same topology.
    
    @details A Morse Complex consists of critical vertices, edges and faces, representing minima, saddles and maxima of the 
    assigned scalar Morse function on the mesh. These critical simplices are connected via separatrices, that give information on 
    how the gradient "flows" from the maxima to the saddles and from the saddles to the minima. This gives a topological skelton 
    of the mesh which can be noise reduced using a parameter called persistence. The topologicallly relveant Betti numbers can be 
    stored as well.
    """
    ## @var CritVertices
    # A dictionary storing the critical vertices. Key is the vertex index and value the CritVertex class object.
    ## @var CritEdges
    # A dictionary storing the critical edges. Key is an edge index and value the CritEdge class object.
    ## @var CritFaces
    # A dictionary storing the critical faces. Key is the face index and value the CritFace class object.
    ## @var Separatrices
    # A list storing the Separatrix class objects.
    ## @var _flag_BettiNumbers
    # Boolean wether the Betti numbers have been calculated or not.
    ## @var BettiNumbers
    # Betti Numbers if calculated, otherwise None.
    ## @var maximalReduced
    # Boolean wether this complex is maximally reduced, e.g. no more cancellations are possible and the persistence is maximal.
    ## @var persistence
    # The persistence level up to which this complex has been reduced to.
    ## @var filename
    # The filenmae of the underlying mesh.
        
    def __init__(self, persistence=0, filename=None):
        """! The Constructor of a MorseComplex.
        @param persistence The persistence up to which this complex has been reduced to. Optional, default is 0 (not reduced at all).
        @param filename The filename of the original mesh. Optional, default is None.
        """
        self.CritVertices = {}
        self.CritEdges = {}
        self.CritFaces = {}
        
        self.Separatrices = []
        
        self._flag_MorseCells = False
        self.MorseCells = MorseCells()
        
        self._flag_BettiNumbers = False
        self.BettiNumbers = None
        
        self.maximalReduced = False
        self.persistence = persistence
        self.filename = filename
        
    def add_vertex(self, vert):
        """! @brief Adds a critical vertex to the Morse Complex.
        @param vert A Vertex class object.
        """
        critvert = CritVertex(vert)
        self.CritVertices[vert.index] = critvert
        
    def info(self):
        """! @brief Prints out an info block about this Morse Complex."""
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
        
        
class Cell:
    
    def __init__(self, label):
        self.label = label
        
        self.vertices = set()
        self.boundary = set()
        
        self.neighbors = {}
        self.neighbors_weights = {}
        
        self.neighborlist = []
        
        
class MorseCells:
    def __init__(self):
        self.Cells = {}
        
    def add_cell(self, cell):
        self.cells[cell.label] = cell
        
    def add_vertex_to_label(self, label, index):
        if label not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label)
            
        self.Cells[label].vertices.add(index)
        
    def add_boundary_to_label(self, label, index):
        if label not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label)
            
        self.Cells[label].boundary.add(index)
        
    def add_neighboring_cell_labels(self, label1, v1, label2, v2):
        if label1 not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label1)
        if label2 not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label2)
            
        # create neighbor keys if necessary
        if label2 not in self.Cells[label1].neighbors.keys():
            self.Cells[label1].neighbors[label2] = set()
            self.Cells[label1].neighborlist.append(label2)
            self.Cells[label1].neighbors_weights[label2] = 0
        if label1 not in self.Cells[label2].neighbors.keys():
            self.Cells[label2].neighbors[label1] = set()
            self.Cells[label2].neighborlist.append(label1)
            self.Cells[label2].neighbors_weights[label1] = 0
            
        # mark the indices as boundary in their cell
        self.Cells[label2].boundary.add(v2)
        self.Cells[label1].boundary.add(v1)
        # add the indices to the correct neighbor boundary
        self.Cells[label2].neighbors[label1].add(v1)
        self.Cells[label1].neighbors[label2].add(v2)