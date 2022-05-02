from LoadData.Datastructure import Vertex, Edge, Face
from LoadData.read_ply import read_ply
from ProcessLowerStarts2 import ProcessLowerStars2
from ExtractMorseComplex2 import ExtractMorseComplex2

import timeit

class Mesh:
    def __init__(self, simplicial=True, cubical=False):
        if (simplicial and cubical) or (not simplicial and not cubical):
            raise ValueError("Mesh needs to be either cubical or simplicial!")
        self.simplicial = simplicial
        self.cubical = cubical

        self.filename = None

        self.Vertices = {}
        self.Edges = {}
        self.Faces = {}
        
        self.flag_ProcessLowerStars = False
        self.flag_MorseComplex = False

        self.V12 = {}
        self.V23 = {}

        self.C = {}
        self.C[0] = set()
        self.C[1] = set()
        self.C[2] = set()


    def load_mesh_ply(self, filename, quality_index):
        self.filename = filename
        
        start_time  = timeit.default_timer()
        read_ply(self.filename, quality_index, self.Vertices, self.Edges, self.Faces)
        
        end_time = timeit.default_timer() - start_time
        print('Time read and prepare data:', end_time)
        
    def info(self):
        print("Mesh Info")
        print("-------------------------------------")
        print("Filename: ", self.filename)
        print("Number of Vertices: ", len(self.Vertices))
        print("Number of Edges: ", len(self.Edges))
        print("Number of Faces: ", len(self.Faces))
        print("-------------------------------------")
        print("Euler characteristic: ", len(self.Vertices) + len(self.Faces) -len(self.Edges))
        print("-------------------------------------")
        
    def info_Morse(self):
        print("MorseComplex Info")
        print("-------------------------------------")
        print("Number of Vertices: ", len(self.C[0]))
        print("Number of Edges: ", len(self.C[1]))
        print("Number of Faces: ", len(self.C[2]))
        print("-------------------------------------")
        print("Euler characteristic: ", len(self.C[0]) + len(self.C[2]) -len(self.C[1]))
        print("-------------------------------------")
        
    def ProcessLowerStars(self):
        # reset if has been computed already
        if self.flag_ProcessLowerStars:
            self.V12 = {}
            self.V23 = {}

            self.C = {}
            self.C[0] = set()
            self.C[1] = set()
            self.C[2] = set()
            
        ProcessLowerStars2(self.Vertices, self.Edges, self.Faces, self.C, self.V12, self.V23)
        self.flag_ProcessLowerStars = True
        
    # returns MorseComplex (a reduced complex)    
    def ExtractMorseComplex(self):
        return ExtractMorseComplex2(self.Vertices, self.Edges, self.Faces, self.V12, self.V23, self.C)
    