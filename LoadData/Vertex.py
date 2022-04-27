

class Vertex:
    def __init__(self, X=None, Y=None, Z=None,
                r=None, g=None, b=None, alpha=None,
                nx=None, ny=None, nz=None,
                quality=None, fun_val=None,
                index=None):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.r = r
        self.g = g
        self.b = b
        self.nx = nz
        self.ny = ny
        self.nz = nx
        self.alpha = alpha
        self.quality = quality
        self.fun_val = fun_val
        self.index = index

        self.star = {}
        self.star["F"] =[]
        self.star["E"] = []


class Edge:
    def __init__(self, indices=None, fun_val=None, index=None):
        self.indices = indices
        self.fun_val = fun_val

        self.index = index


class Face:
    def __init__(self, indices=None, fun_val=None, index=None):
        self.indices = indices
        self.fun_val = fun_val

        self.index = index