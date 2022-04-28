from .Datastructure import Vertex, Edge, Face
from .read_ply import read_ply

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

        self.V12 = {}
        self.V23 = {}

        self.C = {}
        self.C[0] = []
        self.C[1] = []
        self.C[2] = []


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
        
    def info_Morse(self):
        print("MorseComplex Info")
        print("-------------------------------------")
        print("Number of Vertices: ", len(self.C[0]))
        print("Number of Edges: ", len(self.C[1]))
        print("Number of Faces: ", len(self.C[2]))
        print("-------------------------------------")