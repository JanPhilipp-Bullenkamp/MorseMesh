class Mesh:
    def __init__(self):
        self.filename = None
        
        self.min = None
        self.max = None
        self.range = None

        self.Vertices = {}
        self.Edges = {}
        self.Faces = {}
        
        self.Links = {}
        
        self._flag_ProcessLowerStars = False
        self._flag_MorseComplex = False
        self._flag_SalientEdge = False
        self._flag_BettiNumbers = False
        
        self.partners = None  # filled by betti numbers calculation (for persistence diagram needed)
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
        
        self.MorseCells = {}
        
        self.Segmentation = {}
        
        self.SegmentationDual = {}
        
    def info(self):
        print("+-------------------------------------------------------")
        print("| Mesh Info")
        print("+-------------------------------------------------------")
        print("| Filename: ", self.filename)
        print("| Morse function values range: ", [self.min,self.max])
        print("+-------------------------------------------------------")
        print("| Number of Vertices: ", len(self.Vertices))
        print("| Number of Edges: ", len(self.Edges))
        print("| Number of Faces: ", len(self.Faces))
        print("+-------------------------------------------------------")
        print("| Euler characteristic: ", len(self.Vertices) + len(self.Faces) -len(self.Edges))
        if self._flag_BettiNumbers:
            print("| Betti numbers: ", self.BettiNumbers)
        print("+-------------------------------------------------------")
        