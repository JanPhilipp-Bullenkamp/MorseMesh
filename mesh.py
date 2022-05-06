from LoadData.Datastructure import Vertex, Edge, Face
from LoadData.read_ply import read_ply
from ProcessLowerStarts2 import ProcessLowerStars2
from ExtractMorseComplex2 import ExtractMorseComplex2
from MorseAlgorithms.ReduceMorseComplex import CancelCriticalPairs2

from MorseCells import get_MorseCells

from PlotData.write_overlay_ply_file import write_overlay_ply_file
from PlotData.write_labeled_cells_overlay import write_cells_overlay_ply_file

import timeit
import os
import numpy as np

class Mesh:
    def __init__(self):
        self.filename = None
        
        self.min = None
        self.max = None

        self.Vertices = {}
        self.Edges = {}
        self.Faces = {}
        
        self._flag_ProcessLowerStars = False
        self._flag_MorseComplex = False

        self.V12 = {}
        self.V23 = {}

        self.C = {}
        self.C[0] = set()
        self.C[1] = set()
        self.C[2] = set()
        
        self.MorseComplex = None
        
        self.reducedMorseComplexes = {}
        
        self.MorseCells = {}


    def load_mesh_ply(self, filename, quality_index):
        min_val, max_val = read_ply(filename, quality_index, self.Vertices, self.Edges, self.Faces)
        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val

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
        print("+-------------------------------------------------------")
        
    def ProcessLowerStars(self):
        # reset if has been computed already
        if self._flag_ProcessLowerStars:
            self.V12 = {}
            self.V23 = {}

            self.C = {}
            self.C[0] = set()
            self.C[1] = set()
            self.C[2] = set()
            
        ProcessLowerStars2(self.Vertices, self.Edges, self.Faces, self.C, self.V12, self.V23)
        self._flag_ProcessLowerStars = True
        
    # returns full MorseComplex   
    def only_return_ExtractMorseComplex(self):
        if not self._flag_ProcessLowerStars:
            raise ValueError('Need to call ProcessLowerStars first, cannot calculate MorseComplex otherwise!')
        else:
            return ExtractMorseComplex2(self.Vertices, self.Edges, self.Faces, self.V12, self.V23, self.C)
    
    def ExtractMorseComplex(self):
        if not self._flag_ProcessLowerStars:
            raise ValueError('Need to call ProcessLowerStars first, cannot calculate MorseComplex otherwise!')
        else:
            if self._flag_MorseComplex:
                self.MorseComplex = None

            self.MorseComplex = ExtractMorseComplex2(self.Vertices, self.Edges, self.Faces, self.V12, self.V23, self.C)
            self.MorseComplex.filename = self.filename
            self._flag_MorseComplex = True
        
    def only_return_ReducedMorseComplex(self, persistence):
        if not self._flag_MorseComplex:
            raise ValueError('Need to call ExtractMorseComplex first, cannot reduce MorseComplex otherwise!')
        elif persistence in self.reducedMorseComplexes.keys():
            print("This persistence has already been calculated!")
            print("You can access it via .reducedMorseComplexes[persistence] ") 
        else:
            # in these cases we need to calculate it from the original Morse Complex
            if len(self.reducedMorseComplexes.keys())==0:
                return CancelCriticalPairs2(self.MorseComplex, persistence)
            elif min(self.reducedMorseComplexes.keys()) > persistence:
                return CancelCriticalPairs2(self.MorseComplex, persistence)
                
            # else: choose the closest already calculated persistence and start from there
            else:
                key_array = np.array([list(self.reducedMorseComplexes.keys())])
                closest_smaller = key_array[key_array < persistence].max()
                return CancelCriticalPairs2(self.reducedMorseComplexes[closest_smaller], persistence)
        
    def ReducedMorseComplex(self, persistence):
        if not self._flag_MorseComplex:
            raise ValueError('Need to call ExtractMorseComplex first, cannot reduce MorseComplex otherwise!')
        elif persistence in self.reducedMorseComplexes.keys():
            print("This persistence has already been calculated!")
            print("You can access it via .reducedMorseComplexes[persistence] ") 
        else:
            # in these cases we need to calculate it from the original Morse Complex
            if len(self.reducedMorseComplexes.keys())==0:
                self.reducedMorseComplexes[persistence] = CancelCriticalPairs2(self.MorseComplex, persistence)
            elif min(self.reducedMorseComplexes.keys()) > persistence:
                self.reducedMorseComplexes[persistence] = CancelCriticalPairs2(self.MorseComplex, persistence)
                
            # else: choose the closest already calculated persistence and start from there
            else:
                key_array = np.array([list(self.reducedMorseComplexes.keys())])
                closest_smaller = key_array[key_array < persistence].max()
                #print("Calculated reduced complex (",persistence,") from closest smaller already calculated persistence: ", closest_smaller)
                self.reducedMorseComplexes[persistence] = CancelCriticalPairs2(self.reducedMorseComplexes[closest_smaller], persistence)
                 
        return self.reducedMorseComplexes[persistence]
    
    def plot_MorseComplex(self, MorseComplex, filename, path_color=[255,0,255]):
        write_overlay_ply_file(MorseComplex, self.Vertices, self.Edges, self.Faces, filename, color_paths=path_color)
        
        
    def ExtractMorseCells(self, MorseComplex):
        if MorseComplex.persistence not in self.MorseCells.keys():
            self.MorseCells[MorseComplex.persistence] = get_MorseCells(MorseComplex, self.Vertices, self.Edges, self.Faces)
            return self.MorseCells[MorseComplex.persistence]
        else:
            print("MorseCells for the MorseComplex with this persistence have already been calculated!")
            print("You can access the MorseCells dictionary via: .MorseCells[persistence]")
            print("where the persistence can be retrieved from MorseComplex.persistence") 
            
    def plot_MorseCells(self, persistence, filename):
        if persistence not in self.MorseCells.keys():
            raise ValueError('No MorseCell calculated for this persistence!')
        else:
            write_cells_overlay_ply_file(self.MorseCells[persistence], self.Vertices, filename)
    
    