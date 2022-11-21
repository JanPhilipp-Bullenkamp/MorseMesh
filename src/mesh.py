##
# @file mesh.py
#
# @brief Stores the Mesh dataclass.
#
# @section normal_mesh_structures Normal Mesh Structures
# - filename
# - min
# - max
# - range
# - Vertices
# - Edges
# - Faces
#
# @section morse_theoretic_structures Morse-Theoretic Structures
# - _flag_ProcessLowerStars
# - _flag_MorseComplex
# - _flag_SalientEdge
# - _flag_BettiNumbers
# - partners
# - BettiNumbers
# - V12
# - V23
# - C
# - MorseComplex
# - reducedMorseComplexes
# - maximalReducedComplex

class Mesh:
    """! @brief Mesh class used to store mesh, Morse Theory and Segmentation related structures."""
    ## @var filename
    # The filename of the underlying mesh.
    ## @var min
    # The minimal function value.
    ## @var max
    # The maximal function value
    ## @var range
    # The range of function values. (max-min)
    ## @var Vertices
    # A dictionary to store the vertices. Stored as key-value with key: vertex index and value: Vertex class object
    ## @var Edges
    # A dictionary to store the edges. Stored as key-value with key: edge index and value: Simplex class object
    ## @var Faces
    # A dictionary to store the faces. Stored as key-value with key: face index and value: Simplex class object
    
    ## @var _flag_ProcessLowerStars
    # Boolean whether the discrete vector field V has been calculated.
    ## @var _flag_MorseComplex
    # Boolean whether the initial Morse complex has been calculated.
    ## @var _flag_SalientEdge
    # Boolean whether a maximally reduced Morse complex has been calculated for salient edge extraction.
    ## @var _flag_BettiNumbers
    # Boolean whether the Betti numbers have been calculated.
    ## @var partners
    # Filled from Betti number calculation; needed for persistence diagram plotting.
    ## @var BettiNumbers
    # The Betti numbers stored as an array.
    ## @var V12
    # Discrete vectors/ pairings dictionary between vertices and edges.
    ## @var V23
    # Discrete vectors/ pairings dictionary between edges and faces.
    ## @var C
    # Dictionary with critical simplices: has keys 0,1 and 2. Each of these contains a set with critical 
    # simplices of the respective dimension
    ## @var MorseComplex
    # The initial Morse complex.
    ## @var reducedMorseComplexes
    # A dictionary of reduced Morse complexes. The keys are the persistences of the respective reduced Morse complex in value.
    ## @var maximalReducedComplex
    # The maximally reduced Morse complex
    
    def __init__(self):
        """! @brief Constructor for the Mesh class. """
        self.filename = None
        
        self.min = None
        self.max = None
        self.range = None

        self.Vertices = {}
        self.Edges = {}
        self.Faces = {}
        
        self._flag_ProcessLowerStars = False
        self._flag_MorseComplex = False
        self._flag_SalientEdge = False
        self._flag_BettiNumbers = False
        
        self.BettiNumbers = None

        self.V12 = {}
        self.V23 = {}

        self.C = {}
        self.C[0] = set()
        self.C[1] = set()
        self.C[2] = set()
        
        self.MorseComplex = None
        
        self.reducedMorseComplexes = {}
        
        self.maximalReducedComplex = None
        
    def __repr__(self):
        """! @brief Prints out Mesh information.
        @return A string that gives information on the loaded mesh.
        """
        return ("+-------------------------------------------------------\n"
        "| Mesh Info\n"
        "+-------------------------------------------------------\n"
        "| Filename: " + self.filename + "\n"
        "| Morse function values range: " + str([self.min,self.max]) + "\n"
        "+-------------------------------------------------------\n"
        "| Number of Vertices: " + str(len(self.Vertices)) + "\n"
        "| Number of Edges: " + str(len(self.Edges)) + "\n"
        "| Number of Faces: " + str(len(self.Faces)) + "\n"
        "+-------------------------------------------------------\n"
        "| Euler characteristic: " + str(len(self.Vertices) + len(self.Faces) -len(self.Edges)) + "\n"
        "| Betti numbers: " + str(self.BettiNumbers) + "\n" 
        "+-------------------------------------------------------")
        