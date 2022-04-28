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