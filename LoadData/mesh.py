

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


    def load_mesh_ply(self, filename):
        self.filename = filename

        