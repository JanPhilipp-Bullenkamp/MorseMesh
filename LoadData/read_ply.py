from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import numpy as np

from Vertex import Vertex

def read_ply(filename):
    
    rawdata = PlyData.read(filename)

    proplist = []
    for ind, prop in enumerate(rawdata[0].properties):
        if prop.name == "red":
            proplist.append(ind)
        elif prop.name == "green":
            proplist.append(ind)
        elif prop.name == "blue":
            proplist.append(ind)
        elif prop.name == "nx":
            proplist.append(ind)
        elif prop.name == "ny":
            proplist.append(ind)
        elif prop.name == "nz":
            proplist.append(ind)
        elif prop.name == "alpha":
            proplist.append(ind)
        elif prop.name == "quality":
            proplist.append(ind)
        else:
            proplist.append(None)

    for index, pt in enumerate(rawdata['vertex']):
        vert = Vertex(pt[0], pt[1], pt[2])
        if proplist[3] != None:
            vert.r = pt[proplist[3]]
        if proplist[4] != None:
            vert.g = pt[proplist[4]]
        if proplist[5] != None:
            vert.b = pt[proplist[5]]
        if proplist[6] != None:
            vert.nx = pt[proplist[6]]
        if proplist[7] != None:
            vert.ny = pt[proplist[7]]
        if proplist[8] != None:
            vert.nz = pt[proplist[8]]
        if proplist[9] != None:
            vert.alpha = pt[proplist[9]]
        if proplist[10] != None:
            vert.quality = pt[proplist[10]]

        vert.index = index


