##
# @file Datastructure.py
#
# @brief Stores data classes we will use in the mesh class.
#
# @section normal_mesh_parts Normal Mesh Parts
# - Vertex class
# - Simplex class
#
# @section critical_simplices Critical Simplices
# - CritVertex class
# - CritEdge class
# - CritFace class
#
# @section morse_complex_related Morse Complex Related
# - Separatrix class
# - MorseComplex class
#
# @section segmentation_related Segmentation Related
# - Cell class
# - MorseCells class

# imports
from copy import deepcopy
import numpy as np

from .weight_metrics import compute_weight_saledge
from ..cancellation_queue import CancellationQueue


class Vertex:
    """! @brief Vertex class used for normal vertices and their properties.
    
    @details Stores the following properties of a vertex:
    - x,y and z coordinate
    - a quality value
    - a function value
    - an index
    
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
    
    ##  @var star 
    # The surrounding faces "F" and edges "E" in a dictionary with keys "F" and "E".
    ##  @var neighbors 
    # A set containing all neighbor vertices (their indices).
    
    ## @var label
    # needed for Morse cell computation
    ## @var boundary
    # needed for Morse cell computation
    
    __slots__ = ("x", "y", "z", "quality", "fun_val", "index", "star", "neighbors", "label", "boundary")
    
    def __init__(self, x: int = None, y: int = None, z: int = None,
                quality: int = None, fun_val: int = None,
                index: int = None):
        """! @brief The Constructor of a Vertex
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
        
        self.star = {"F": [], "E": []}
        self.neighbors = set() #set
        
        # needed for Morse Cells
        self.label = -1 #int
        self.boundary = False #bool
        
    def has_neighbor_label(self, vert_dict: dict) -> tuple[set, list]:
        neighbor_labels = set()
        neighbor_indices = []
        for elt in self.neighbors:
            if vert_dict[elt].label != -1 and vert_dict[elt].label != self.label:
                neighbor_indices.append([elt, vert_dict[elt].label])
                neighbor_labels.add(vert_dict[elt].label)
        return neighbor_labels, neighbor_indices

    def compute_gradient(self, vert_dict: dict) -> float:
        grad = 0
        for vert_ind in self.neighbors:
            dist = np.linalg.norm(np.array((self.x, self.y, self.z)) - np.array((vert_dict[vert_ind].x, vert_dict[vert_ind].y, vert_dict[vert_ind].z)))
            grad += (self.fun_val - vert_dict[vert_ind].fun_val)/dist
        return grad/len(self.neighbors)

    def average_gradient_on_star(self, vert_dict: dict, face_dict: dict):
        """! @brief Average Gradient on Star method from paper Gradient Field Estimation
                    on Triangle Meshes 2018 Mancinelli et al.
        """
        star_area = 0
        sum_grads = 0
        for f_index in self.star["F"]:
            f_area = face_dict[f_index].area(vert_dict)
            star_area += f_area
            sum_grads += f_area * face_dict[f_index].face_gradient(vert_dict, f_area)
            print("face_grad: ",face_dict[f_index].face_gradient(vert_dict, f_area))

        print("average_gradient_star: ",sum_grads/star_area)
        return sum_grads/star_area

    def get_n_neighborhood(self, vert_dict: dict, n: int) -> set:
        n_rings = {}
        n_rings[0] = self.neighbors
        for i in range(1,n):
            n_rings[i] = set()
            for ind in n_rings[i-1]:
                n_rings[i].update(vert_dict[ind].neighbors)

            for j in range(0,i):
                n_rings[i] -= n_rings[j]

        n_neighborhood = set()
        n_neighborhood.add(self.index)
        for i in range(0,n):
            n_neighborhood.update(n_rings[i])

        return n_neighborhood

    def coordinates(self):
        return [self.x, self.y, self.z]

    def __str__(self) -> str:
        """! @brief Retrieves the index of the vertex.
        @return A string of the index of the vertex.
        """
        return str(self.index)
    
def compare_heights(small: tuple, big: tuple) -> bool:
    """! @brief Compares two tuples of sorted values.
    
    @details Compares two sorted tuples of possibly different length and returns True if the second
    one is considered larger and False if the first one is considered larger. Tuples are higher
    if their highest (first) value is larger than the highest value of the other tuple and shorter
    tuples are higher than longer if all values are equal up to the length of the shorter tuple.
    For example the following tuples are sorted from high to low:
    
    (4), (4,3), (3,2,2), (3,2,1), (2), (2,9), (2,7), (2,9,15)
    
    @param small First tuple to be compared.
    @param big Second tuple to be compared.
    
    @return True if small is smaller than big according to the metric. False otherwise.
    """
    # return True if small is smaller than big, False otherwise
    if len(small) == len(big):
        for i in range(len(small)):
            if small[i] < big[i]:
                return True
            elif small[i] > big[i]:
                return False
        return False
    if len(small) < len(big):
        for i in range(len(small)):
            if small[i] < big[i]:
                return True
            elif small[i] > big[i]:
                return False
        return False
    if len(small) > len(big):
        for i in range(len(big)):
            if small[i] < big[i]:
                return True
            elif small[i] > big[i]:
                return False
        return True   
     
class Simplex:
    """! @brief Simplex class used for normal edges and faces.
    
    @details Stores an edge or face as a set of two/ three indices (representing two/ three vertices). 
    Each simplex has an own index (edge-index or face-index). 
    
    Can set the function value of the simplex by taking the function values of the 
    vertices and storing them in a list, sorted such that the higher function value
    is at the first position.    
    """
    ## @var indices
    # A set of two/three indices representing the simplex
    ## @var fun_val
    # A sorted list of two/three floats, where the first value is the highest
    ## @var index
    # The index of this simplex (edge-index or face-index)
    
    __slots__ = ("indices", "fun_val", "index", "max_fun_val_index", "area")
    
    def __init__(self, indices: set = None, index: int = None):
        """! The Constructor of a Simplex
        @param indices A set of indices representing the vertices of the simplex. Default is None.
        @param index The index of this simplex. Default is None. 
        """
        self.indices = indices #set
        self.fun_val = None #list
        self.max_fun_val_index = None

        self.index = index #int

        self.area = None
    
    def set_fun_val(self, vertices_dict: dict):
        """! @brief Sets the function value of the simplex.
        @details Uses the function values of the vertices and sorts them such 
        that the first value is the larger function value.
        
        @param vertices_dict The dictionary, where the vertices are stored. Keys should be the 
        indices of the vertices.
        """
        self.fun_val = []

        tmp = {ind: vertices_dict[ind].fun_val for ind in self.indices}
        self.max_fun_val_index = max(tmp, key=tmp.get)
        self.fun_val = sorted(list(tmp.values()), reverse=True)
        
        #for ind in self.indices:
        #    self.fun_val.append(vertices_dict[ind].fun_val)
        #    if vertices_dict[ind].fun_val == max(self.fun_val):
        #        self.max_fun_val_index = ind
        #self.fun_val.sort(reverse=True)
        
    def has_face(self, other_simplex) -> bool:
        """! @brief Checks if a given other simplex is a face of this simplex.
        @details Another simplex is a face of this simplex, if its vertices are a real subset of this simplex
        vertices and there is only one vertex not contained. (e.g. an edge with 2 indices can be the face of a
        triangle with 3 indices.
        
        @param other_simplex Another Simplex object that we want to know of whether it is a face of this simplex.
        
        @return Bool. True if the other simplex is a face of this simplex, False otherwise.
        """
        if len(self.indices) - len(other_simplex.indices) == 1 and other_simplex.indices.issubset(self.indices):
            return True
        else:
            return False

    def compute_area(self, vert_dict: dict):
        if len(self.indices) != 3:
            raise TypeError("This is not a Triangle-Simplex. Area only defined for triangles atm!")
        vectors = np.diff([vert_dict[ind].coordinates() for ind in self.indices], axis = 0)
        cross = np.cross(vectors[0], vectors[1])
        area = (np.sum(cross**2)**.5) * .5
        return area

    def face_gradient(self, vert_dict: dict, area: float = None):
        """! @brief bla bla

        @details If the face has vertices v_i, v_j, v_k with function values f_i, f_j, f_k and Area A_f, the gradient of th face
        is computed as 
            grad(face) = (f_j - f_i) x (v_i - v_k)^rot/2A_f + (f_k - f_i) x (v_j - v_i)^rot/2A_f 
        where ^rot means the edge is rotated by 90 degrees 
        \TODO which direction 90 deg??? currently not done...
        """
        if len(self.indices) != 3:
            raise TypeError("This is not a Triangle-Simplex. face_gradient only defined for triangles atm!")
        if area == None:
            area = self.compute_area(vert_dict)

        v_data = [[vert_dict[ind].coordinates(), ind, vert_dict[ind].fun_val] for ind in self.indices]

        vectors = np.diff([v[0] for v in v_data], axis = 0)
        fun_diffs = np.diff([v[2] for v in v_data], axis=0)
        grad_face = fun_diffs[1]/(2 * area) * vectors[0] + (-1) * fun_diffs[0]/(2 * area) * vectors[1]
        return grad_face
        
       
    def get_max_fun_val_index(self) -> int:
        return self.max_fun_val_index
        
    def __lt__(self, other_simplex) -> bool:
        """! @brief Checks if another simplex has a smaller function value (according to the metric described in compare_heights)
        
        @param other_simplex The simplex we want to know of whether it has a higher function value than this simplex.
        
        @return Bool. Returns True if this simplex has a smaller function value than the other simplex. False otherwise.
        """
        # return true if own fun_val is smaller than the fun_val of other_simplex
        return compare_heights(self.fun_val, other_simplex.fun_val)
        
    def __str__(self) -> str:
        """! Retrieves the index of the simplex.
        @return A string of the index of the simplex.
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
    
    __slots__ = ("index", "fun_val", "connected_saddles")
    
    def __init__(self, vert: Vertex):
        """! The Constructor of a CritVertex.
        @param vert A Vertex class object.
        """
        self.index = vert.index #int
        self.fun_val = vert.fun_val #float
        
        self.connected_saddles = []

    def __eq__(self, other):
        return self.index == other.index and self.fun_val == other.fun_val and self.connected_saddles == other.connected_saddles
        
    def __str__(self) -> str:
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
    
    
    __slots__ = ("indices", "fun_val", "index", "connected_minima", "connected_maxima", "paths")
    
    def __init__(self, edge: Simplex):
        """! The Constructor of a CritEdge.
        @param edge An Simplex class object representing an edge.
        """
        self.indices = edge.indices #set
        self.fun_val = edge.fun_val #list
        
        self.index = edge.index #int
        
        self.connected_minima = []
        self.connected_maxima = []
        
        self.paths = {}

    def __eq__(self, other):
        equal = True
        if not self.indices == other.indices:
            equal = False
        if not self.fun_val == other.fun_val:
            equal = False 
        if not self.index == other.index:
            equal = False 
        if not self.connected_minima == other.connected_minima:
            equal = False
        if not self.connected_maxima == other.connected_maxima:
            equal = False
        if not self.paths == other.paths:
            equal == False
        return equal
        
    def __str__(self) -> str:
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
    
    __slots__ = ("indices", "fun_val", "index", "connected_saddles", "paths")
    
    def __init__(self, face: Simplex):
        """! The Constructor of a CritFace.
        @param face A Simplex class object representing a face.
        """
        self.indices = face.indices #set
        self.fun_val = face.fun_val #list
        
        self.index = face.index #int
        
        self.connected_saddles = []
        
        self.paths = {}

    def __eq__(self, other):
        equal = True
        if not self.indices == other.indices:
            equal = False
        if not self.fun_val == other.fun_val:
            equal = False 
        if not self.index == other.index:
            equal = False 
        if not self.connected_saddles == other.connected_saddles:
            equal = False
        if not self.paths == other.paths:
            equal == False
        return equal
        
    def __str__(self) -> str:
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
    
    
    __slots__ = ("origin", "destination", "dimension", "path", "separatrix_persistence")
    
    def __init__(self, origin: int, destination: int, dimension: int, path: list, separatrix_persistence: float):
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

    def get_indices(self, edge_dict: dict, face_dict: dict) -> set:
        """! @brief Returns a set of indices that make up this separatrix.
        @param edge_dict A dictionary containing the edges.
        @param face_dict A dictionary containing the faces.

        @return indices A set of (vertex) indices that make up this separatrix.
        """
        indices = set()
        # edge-vert separatrix -> only need to add edge indices
        if self.dimension == 1:
            for i, elt in enumerate(self.path):
                if i%2 == 0:
                    indices.add(edge_dict[elt].indices)
        # face-edge separatrix -> only need to add face indices        
        elif self.dimension == 2:
            for i, elt in enumerate(self.path):
                if i%2 == 0:
                    indices.add(face_dict[elt].indices)
        return indices
        
    def __str__(self) -> str:
        """! Retrieves information on this separatrix.
        @return A string telling wether its a minimal or maximal line, origin, destination and the length of the path.
        """
        if self.dimension == 1:
            return "Minimal line from saddle" + str(self.origin) + " to minimum" + str(self.destination) + " in " + str(len(self.path)) + " pathpoints"
        elif self.dimension == 2:
            return "Maximal line from maximum" + str(self.origin) + " to saddle" + str(self.destination) + " in " + str(len(self.path)) + " pathpoints"
        
    
class MorseComplex:
    """! @brief A Morse Complex, that stores a reduced skeleton of the original mesh/simplicial complex 
    and has the same topology. Also stores MorseCells and various Segmentations for this persistence level.
    
    @details A Morse Complex consists of critical vertices, edges and faces, representing minima, saddles and maxima of the 
    assigned scalar Morse function on the mesh. These critical simplices are connected via separatrices, that give 
    information on how the gradient "flows" from the maxima to the saddles and from the saddles to the minima. 
    This gives a topological skelton of the mesh which can be noise reduced using a parameter called persistence. 
    The topologicallly relveant Betti numbers can be stored as well.
    Since the skeleton provides us with enclosed areas on a mesh as well, each Morse Complex can also contain 
    MorseCells, which give a segmentation in between the skeleton of the mathematical complex, as well as different 
    segmentations that started from the MorseCells of the MorseComplex and got reduced based on defined ridges.
    """
    ## @var CritVertices
    # A dictionary storing the critical vertices. Key is the vertex index and value the CritVertex class object.
    ## @var CritEdges
    # A dictionary storing the critical edges. Key is an edge index and value the CritEdge class object.
    ## @var CritFaces
    # A dictionary storing the critical faces. Key is the face index and value the CritFace class object.
    ## @var Separatrices
    # A list storing the Separatrix class objects.
    ## @var _flag_MorseCells
    # Boolean whether the Morse Cells for this Morse Complex have been calculated.
    ## @var MorseCells
    # A MorseCells class object storing the MorseCells for this MorseComplex persistence.
    ## @var Segmentations
    # A dictionary storing different Segmentations at this persistence level. 
    # Can be accessed via .Segmentations[(large_thr, small_thr)][merge_thr] and contains Morse Cell objects.
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
    
    __slots__ = ("CritVertices", "CritEdges", "CritFaces", "Separatrices", "_flag_MorseCells", "MorseCells", "Segmentations", "_flag_BettiNumbers", "BettiNumbers", "partners", "maximalReduced", "max_separatrix_persistence", "min_separatrix_persistence", "persistence", "filename")
        
    def __init__(self, persistence: float = 0, filename: str = None):
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
        
        self.Segmentations = {}
        
        self._flag_BettiNumbers = False
        self.BettiNumbers = None
        self.partners = None # gives betti numbers and needed for persistence diagram
        
        self.maximalReduced = False
        self.max_separatrix_persistence = None
        self.min_separatrix_persistence = None
        self.persistence = persistence
        self.filename = filename
        
    def add_vertex(self, vert: Vertex):
        """! @brief Adds a critical vertex to the Morse Complex.
        @param vert A Vertex class object.
        """
        critvert = CritVertex(vert)
        self.CritVertices[vert.index] = critvert
        
    def create_segmentation(self, salient_edge_points: set, thresh_large: float, thresh_small: float, 
                                merge_threshold: float, minimum_labels: int = 3, size_threshold: int = 500):
        """! @brief Creates a segmentation from this MorseComplex with the given double edge threshold 
        and the merging threshold.
        
        @details Creates a copy of the Morse cells at this persistence level and than segments 
        based on the given parameters. Segemntation stops when either no more cells can be
        merged due to no more adjacent cells having a weight below the merge threshold, or 
        reaching the optional minimum number of labels (which is defaulted to 3).
        
        @param salient_edge_points The salient edge points that have been calcualted from the double threshold
        @param thresh_large The larger threshold of the double threshold that was used to get the edge points.
        @param thresh_small The smaller threshold of the double threshold that was used to get the edge points.
        @param merge_threshold The threshold that determines when to stop merging cells. Weights in the 
        neighborhood graph of the Morse cells will be above this threshold.
        @param minimum_labels The minimum number of labels we want to keep. Default is set to 3
        """
        if self._flag_MorseCells == False:
            raise AssertionError("No Morse Cells calculated yet...")
        SegmentationCells = deepcopy(self.MorseCells)
        
        SegmentationCells.add_salient_edge_points(salient_edge_points, (thresh_large, thresh_small))
        
        SegmentationCells.segment(merge_threshold, minimum_labels=minimum_labels, size_threshold=size_threshold)
        
        if (thresh_large, thresh_small) not in self.Segmentations.keys():
            self.Segmentations[(thresh_large, thresh_small)] = {}
        if merge_threshold in self.Segmentations[(thresh_large, thresh_small)].keys():
            raise AssertionError("This parameter combination has already been calculated...")
        else:
            self.Segmentations[(thresh_large, thresh_small)][merge_threshold] = SegmentationCells
            
        
    def __repr__(self) -> str:
        """! @brief Prints out an info block about this Morse Complex.
        @return Info as string.
        """
        return("+-------------------------------------------------------\n"
                "| MorseComplex Info\n"
                "+-------------------------------------------------------\n"
                "| Filename: " + str(self.filename) + "\n"
                "| Persistence of this Complex: " + str(self.persistence) + "\n"
                "+-------------------------------------------------------\n"
                "| Number of Vertices: " + str(len(self.CritVertices)) + "\n"
                "| Number of Edges: " + str(len(self.CritEdges)) + "\n"
                "| Number of Faces: " + str(len(self.CritFaces)) + "\n"
                "+-------------------------------------------------------\n"
                "| Euler characteristic: " + str(len(self.CritVertices) - len(self.CritEdges) +len(self.CritFaces)) + "\n"
                "| Betti numbers: " + str(self.BettiNumbers) + "\n"
                "+-------------------------------------------------------")
        
        
class Cell:
    """! @brief A single cell that will be used in the MorseCells. Stores one connected component and
    the relations to adjacent cells.
    """
    ## @var label
    # The label of this cell.
    ## @var vertices
    # A set of vertices making up this cell
    ## @var boundary
    # A set of the boundary vertices of this cell. (also contained in vertices)
    ## @var neighbors
    # A dictionary storing neighbor_label, boundary_to_neighbor pairs. boundary_to_neighbor is a set
    # the vertices that border the cell with the neighbor_label.
    ## @var neighbors_weights
    # A dictionary storing neighbor_label, weight pairs, where the weight gives the weight for the 
    # connection between these two cells.
    
    __slots__ = ("label", "vertices", "boundary", "neighbors", "neighbors_weights")
    
    def __init__(self, label: int):
        """! @brief The constructor of a Cell object.
        @param label The label of this cell object.
        """
        self.label = label
        
        self.vertices = set()
        self.boundary = set()
        
        self.neighbors = {}
        self.neighbors_weights = {}
        
    def __repr__(self) -> str:
        """! @brief Gives info on this Cell.
        @return Info as string.
        """
        return("+-----------------------\n"
               "| Cell info for label: " +str(self.label) + "\n"
               "+-----------------------\n"
               "| Number of vertices: " + str(len(self.vertices)) + "\n"
               "| Neighbors: " + str(list(self.neighbors.keys())) + "\n"
               "+-----------------------\n")
        
class MorseCells:
    """! @brief An object storing Morse Cells that segment the given mesh. Also allows to use further 
    segmentation than the original MorseComplex provides.
    
    @details ....
    """
    ## @var Cells
    # A dictionary of Cell objects, with the labels as keys.
    ## @var salient_edge_points
    # Edge points that are used for further segmentation.
    ## @var threshold
    # Double threshold that was used to get these edge points. A tuple of (large_thr, small_thr).
    ## @var merge_threshold
    # The merge threhsold that was used in the segmentation.
    
    __slots__ = ("Cells", "salient_edge_points", "threshold", "merge_threshold")
    
    def __init__(self):
        """! @brief The constructor of the MorseCells object.
        """
        self.Cells = {}
        
        # only for segmentation cells:
        self.salient_edge_points = None # will be set of indices
        self.threshold = None # will be tuple of (large_thr, small_thr)
        
        self.merge_threshold = None # stores the merge threshold, is a float
        
        
    def add_salient_edge_points(self, salient_edge_points: set, threshold: tuple[float, float]):
        """! @brief Adds salient edge points for a given threshold to this MorseCells object.
        
        @param salient_edge_points The salient edge points we want to use for further segmentation.
        @param threshold The double threshold that was used to get these edge points. 
        A tuple of (large_thr, small_thr).
        """
        if self.salient_edge_points != None:
            raise AssertionError("This MorseCell object already contains salient edge points ...")
        if self.threshold != None:
            raise AssertionError("This MorseCell object already stores a threshold (but probably no salient edge points) shouldnt be possible...")
        self.salient_edge_points = salient_edge_points
        self.threshold = threshold
        
    def add_cell(self, cell: Cell):
        """! @brief Adds a cell to the MorseCells.
        
        @param cell A Cell object that is added the the MorseCells.
        """
        self.Cells[cell.label] = cell
        
    def add_vertex_to_label(self, label: int, index: int):
        """! @brief Adds a vertex to a cell with a given label.
        
        @param label The label of the cell that the vertex should be added to.
        @param index The index of the vertex that should be added to the cell. 
        """
        if label not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label)
        self.Cells[label].vertices.add(index)
        
    def add_boundary_to_label(self, label: int, index: int):
        """! @brief Adds a boundary vertex to a cell with a given label.
        
        @param label The label of the cell that the vertex should be added to.
        @param index The index of the vertex that should be added as boundary to the cell. 
        """
        if label not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label)
        self.Cells[label].vertices.add(index)
        self.Cells[label].boundary.add(index)
        
    def add_neighboring_cell_labels(self, label1: int, v1: int, label2: int, v2: int):
        """! @brief Connects two cells if necessary and updates their boundray points.
        
        @details Connects label 1 and label 2 if necessary and stores the vertices v1 and v2 as
        the according neighboring points.
        
        @param label1 One of the labels that should be connected.
        @param v1 The vertex for label1 neighboring label2.
        @param label2 One of the labels that should be connected.
        @param v2 The vertex for label2 neighboring label1.
        """
        if label1 not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label1)
        if label2 not in self.Cells.keys():
            raise ValueError("This label is not part of the Morse cells: ", label2)
            
        # create neighbor keys if necessary
        if label2 not in self.Cells[label1].neighbors.keys():
            self.Cells[label1].neighbors[label2] = set()
            #self.Cells[label1].neighborlist.append(label2)
            self.Cells[label1].neighbors_weights[label2] = 0
        if label1 not in self.Cells[label2].neighbors.keys():
            self.Cells[label2].neighbors[label1] = set()
            #self.Cells[label2].neighborlist.append(label1)
            self.Cells[label2].neighbors_weights[label1] = 0
            
        # mark the indices as boundary in their cell
        self.Cells[label2].boundary.add(v2)
        self.Cells[label1].boundary.add(v1)
        # (also need to be added to vertices of the cell
        self.Cells[label2].vertices.add(v2)
        self.Cells[label1].vertices.add(v1)
        # add the indices to the correct neighbor boundary
        self.Cells[label2].neighbors[label1].add(v1)
        self.Cells[label1].neighbors[label2].add(v2)
        
    def calculate_all_weights(self):
        """! @brief Calculate all weights between neighboring cells. """
        for label, cell in self.Cells.items():
            for nei_label, points_here in cell.neighbors.items():
                # need points on both sides of the bopundary
                points_there = self.Cells[nei_label].neighbors[label]
                
                weight = compute_weight_saledge(points_here.union(points_there), self.salient_edge_points)
                # add weight to both cells
                cell.neighbors_weights[nei_label] = weight
                self.Cells[nei_label].neighbors_weights[label] = weight
                
    def calculate_weight_between_two_cells(self, label1: int, label2: int):
        """! @brief Calculate weights between two adjacent labels.
        
        @param label1 One of the neigboring labels.
        @param label2 One of the neigboring labels.
        
        @return weight The calculated weight between the two cells.
        """
        points1 = self.Cells[label1].neighbors[label2]
        points2 = self.Cells[label2].neighbors[label1]
        
        weight = compute_weight_saledge(points1.union(points2), self.salient_edge_points)
        
        self.Cells[label1].neighbors_weights[label2] = weight
        self.Cells[label2].neighbors_weights[label1] = weight
        
        return weight
                
    def merge_cells(self, label1: int, label2: int, pop_label2: bool = True) -> list:
        """! @brief Merges the label2 cell into the label1 cell and updates the weights and surrounding
        adjacencies.
        
        @details Merges the label2 cell into the label1 cell. The weights and surrounding
        adjacencies are updated accordingly, such that all former connections of label2 are now 
        connected to label1 and have their weights updated. Label2 is removed from all neighbor 
        dictionaries and the label 2 cell is deleted after all its points were tramsferred to label 1.
        
        @param label1 The cell label that will remain and be merged into.
        @param label2 The cell label that will be merged into the other cell and deleted.
        @param pop_label2 Boolean. Default is True. If False, all adjacencies are updated, but the
        label 2 cell is not popped yet. This allows to loop over the Cells dictionary and removing the 
        labels later
        
        @return updated_weights A list containing triples (new_weight, label1, neighbor) that give the 
        updated weights. (Weights are updated, if the two merging cells have a common neighbor, as the 
        new boundary than contains unknown parts of both labels) 
        """
        updated_weights = []
        
        # do 1. and 2.:
        self.Cells[label1].vertices.update(self.Cells[label2].vertices)
        self.Cells[label1].boundary.update(self.Cells[label2].boundary)
        # remove boundary between the two
        self.Cells[label1].boundary = self.Cells[label1].boundary - (self.Cells[label1].neighbors[label2].union(self.Cells[label2].neighbors[label1]))
        
        # iterate over neighbors of label2:
        for neighbor, indices in self.Cells[label2].neighbors.items():
            if neighbor == label1:
                continue
            # common neighbor -> adjust boundaries and recomupte weights
            elif neighbor in self.Cells[label1].neighbors.keys():
                # extend boundaries on both sides
                self.Cells[label1].neighbors[neighbor].update(indices)
                self.Cells[neighbor].neighbors[label1].update(self.Cells[neighbor].neighbors[label2])
                
                # remove label 2 from neighbor
                self.Cells[neighbor].neighbors.pop(label2)
                self.Cells[neighbor].neighbors_weights.pop(label2)
                
                # recompute weight:
                new_weight = self.calculate_weight_between_two_cells(label1, neighbor)
                
                # fill updated_weights list for cancellation queue later
                updated_weights.append(tuple((new_weight, label1, neighbor)))
                
            elif neighbor not in self.Cells[label1].neighbors.keys():
                # add new neighbor to label 1 and copy weight from label 2
                self.Cells[label1].neighbors[neighbor] = indices
                self.Cells[label1].neighbors_weights[neighbor] = self.Cells[label2].neighbors_weights[neighbor]
                
                # add label 1 as new neighbor to neighbor and copy weight
                self.Cells[neighbor].neighbors[label1] = self.Cells[neighbor].neighbors[label2]
                self.Cells[neighbor].neighbors_weights[label1] = self.Cells[neighbor].neighbors_weights[label2]
                
                # remove label 2 from neighbor:
                self.Cells[neighbor].neighbors.pop(label2)
                self.Cells[neighbor].neighbors_weights.pop(label2)
                
            else:
                raise AssertionError("Shouldnt happen. One of the above cases always should be fulfilled.")
        
        # remove label 2 from label 1:
        self.Cells[label1].neighbors.pop(label2)
        self.Cells[label1].neighbors_weights.pop(label2)
        
        # remove label 2 cell completely (optional due to dictionary size change) need to remove after looping sometimes
        if pop_label2:
            self.Cells.pop(label2)
        
        return updated_weights
        
        
    def remove_small_enclosures(self, size_threshold: int = 15):
        """! @brief Removes small cells, that are fully enclosed by a single other label.
        
        @param size_threshold (Optional) Default is set to 15. If cells have fewer than this parameter
        vertices, they are merged into their surrounding cell.
        """
        remove = set()
        for label, cell in self.Cells.items():
            if len(cell.neighbors.keys()) == 1 and len(cell.vertices) < size_threshold:
                # merge cell into surrounding cell
                neighbor = next(iter(cell.neighbors))
                # just have to add vertices, as boundary will vanish once merged (and boundary is contained in vertices)
                self.Cells[neighbor].vertices.update(cell.vertices)
                
                # remove enclosure from neighborhood of surrounding
                self.Cells[neighbor].neighbors.pop(label)
                self.Cells[neighbor].neighbors_weights.pop(label)
                
                # remove enclosure completely (outside the dictionary loop, cause cant change dictionary size)
                remove.add(label)
                
        for label in remove:
            self.Cells.pop(label)
            
    def remove_small_patches(self, size_threshold: int = 15):
        """! @brief Removes small cells, that have fewer than a threshold vertices.
        
        @param size_threshold (Optional) Default is set to 15. If cells have fewer than this parameter
        vertices, they are merged into their their lowest weight neighboring cell.
        """
        remove = set()
        for label, cell in self.Cells.items():
            if len(cell.vertices) < size_threshold:
                lowest_weight_neighbor = [nei_label for nei_label, weight in sorted(cell.neighbors_weights.items(), key=lambda item: abs(item[1]))][0]
                
                if lowest_weight_neighbor not in remove:
                    self.merge_cells(lowest_weight_neighbor, label, pop_label2=False)
                    remove.add(label)
                
        for label in remove:
            self.Cells.pop(label)

    def segment(self, merge_threshold: float, minimum_labels: int, size_threshold: int = 500):
        """! @brief Makes this MorseCells object a Segmentation, based on the salient edge points stored 
        in this MorseCells object and a given merge_threshold and minim_labels number.
        
        @details Requires this MorseCells object to contain salient edge points. Based on those, the 
        weights between neighboring cells are calculated and then cells are merged using a Priority 
        Queue to make sure to merge cells first if they have a low weight. Merging stops if either 
        no more cell adjacencies have a weight below the threshold or the minimum number of labels 
        is reached. This MorseCell object then becomes the segmentation.
        
        @param merge_threshold The threshold for weights between adjacent cells to stop merging.
        @param minimum_labels A minimum number of labels that will stop the merging process if it is reached.
        (Otherwise the merge threshold is the stopping criterium)
        """
        if self.salient_edge_points == None or self.threshold == None:
            raise AssertionError("Cannot segment if no salient edge points are loaded to these Morse cells!")
        if self.merge_threshold != None:
            raise AssertionError("Already has a merge threshold assigned... Shouldnt be so, probably messed up the order of functions somewhere.")
           
        # 1. calculate weights between cells
        self.calculate_all_weights()
        '''
        # 2. create and fill Cancellation Queue
        queue = CancellationQueue()
        
        for label, cell in self.Cells.items():
            for neighbor, weight in cell.neighbors_weights.items():
                if weight < merge_threshold:
                    queue.insert(tuple((weight,label, neighbor)))
               '''     
        still_changing = True
        # pop from queue until no more elements are below the merge threshold or we reach the minimum number of labels
        while len(self.Cells) > minimum_labels and still_changing: #and queue.length() != 0:
            # 2. create and fill Cancellation Queue
            queue = CancellationQueue()
            before = len(self.Cells)
            for label, cell in self.Cells.items():
                for neighbor, weight in cell.neighbors_weights.items():
                    if weight < merge_threshold:
                        queue.insert(tuple((weight,label, neighbor)))

            while queue.length() != 0:
                weight, label1, label2 = queue.pop_front()
                
                # need to make sure the popped tuple is still available for merging and their weight is also the same.
                if label1 in self.Cells.keys() and label2 in self.Cells.keys():
                    if label2 in self.Cells[label1].neighbors.keys():
                        if weight == self.Cells[label1].neighbors_weights[label2]:
                            # can merge cells
                            updated_weights = self.merge_cells(label1, label2)
            after = len(self.Cells)
            if before == after:
                still_changing = False
                        
        # remove small patches
        self.remove_small_patches(size_threshold=size_threshold)    
        # remove small enclosures
        self.remove_small_enclosures(size_threshold=size_threshold)   