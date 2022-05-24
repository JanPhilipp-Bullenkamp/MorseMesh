from Algorithms.LoadData.Datastructure import Vertex, Edge, Face
from Algorithms.LoadData.read_ply import read_ply
from Algorithms.ProcessLowerStars import ProcessLowerStars
from Algorithms.ExtractMorseComplex import ExtractMorseComplex
from Algorithms.ReduceMorseComplex import CancelCriticalPairs
from Algorithms.BettiNumbers import BettiViaPairCells

from Algorithms.MorseCells import get_MorseCells, create_CellConnectivityGraph, create_SalientEdgeCellConnectivityGraph
from Algorithms.SalientEdgeIndices import get_salient_edge_indices

from Algorithms.PersistenceDiagram import PersistenceDiagram

from PlotData.write_overlay_ply_file import write_overlay_ply_file, write_overlay_ply_file_thresholded
from PlotData.write_labeled_cells_overlay import write_cells_overlay_ply_file
from PlotData.write_salient_edge_overlay import write_salient_edge_file, write_improved_salient_edge_file, plot_salient_edge_histogramm
from PlotData.write_salient_edge_pline import write_salient_edge_pline
from PlotData.write_labels_txt import write_labels_txt_file
from PlotData.write_pline_file import write_pline_file, write_pline_file_thresholded

import timeit
import os
import numpy as np

class Mesh:
    def __init__(self):
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


    def load_mesh_ply(self, filename, quality_index, inverted=False):
        min_val, max_val = read_ply(filename, quality_index, self.Vertices, 
                                    self.Edges, self.Faces, inverted=inverted)
        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val

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
        
    def ProcessLowerStars(self):
        # reset if has been computed already
        if self._flag_ProcessLowerStars:
            self.V12 = {}
            self.V23 = {}

            self.C = {}
            self.C[0] = set()
            self.C[1] = set()
            self.C[2] = set()
            
        ProcessLowerStars(self.Vertices, self.Edges, self.Faces, self.C, self.V12, self.V23)
        self._flag_ProcessLowerStars = True
        
    # returns full MorseComplex   
    def only_return_ExtractMorseComplex(self):
        if not self._flag_ProcessLowerStars:
            raise ValueError('Need to call ProcessLowerStars first, cannot calculate MorseComplex otherwise!')
        else:
            return ExtractMorseComplex(self.Vertices, self.Edges, self.Faces, 
                                       self.V12, self.V23, self.C)
    
    def ExtractMorseComplex(self):
        if not self._flag_ProcessLowerStars:
            raise ValueError('Need to call ProcessLowerStars first, cannot calculate MorseComplex otherwise!')
        else:
            if self._flag_MorseComplex:
                self.MorseComplex = None

            self.MorseComplex = ExtractMorseComplex(self.Vertices, self.Edges, self.Faces, 
                                                    self.V12, self.V23, self.C)
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
                return CancelCriticalPairs(self.MorseComplex, persistence, 
                                           self.Vertices, self.Edges, self.Faces)
            elif min(self.reducedMorseComplexes.keys()) > persistence:
                return CancelCriticalPairs(self.MorseComplex, persistence, 
                                           self.Vertices, self.Edges, self.Faces)
                
            # else: choose the closest already calculated persistence and start from there
            else:
                key_array = np.array([list(self.reducedMorseComplexes.keys())])
                closest_smaller = key_array[key_array < persistence].max()
                return CancelCriticalPairs(self.reducedMorseComplexes[closest_smaller], persistence, 
                                           self.Vertices, self.Edges, self.Faces)
        
    def ReduceMorseComplex(self, persistence):
        if not self._flag_MorseComplex:
            raise ValueError('Need to call ExtractMorseComplex first, cannot reduce MorseComplex otherwise!')
        elif persistence in self.reducedMorseComplexes.keys():
            print("This persistence has already been calculated!")
            print("You can access it via .reducedMorseComplexes[persistence] ") 
        else:
            # in these cases we need to calculate it from the original Morse Complex
            if len(self.reducedMorseComplexes.keys())==0:
                self.reducedMorseComplexes[persistence] = CancelCriticalPairs(self.MorseComplex, persistence, 
                                                                              self.Vertices, self.Edges, self.Faces)
                if persistence >= self.range and not self._flag_SalientEdge:
                    self.maximalReducedComplex = self.reducedMorseComplexes[persistence]
                    self.maximalReducedComplex.maximalReduced = True
                    self._flag_SalientEdge = True
                    print("Persistence was higher than the range of function values,") 
                    print("therefore this complex is maximally reduced and can be used for salient edge extraction.")
            elif min(self.reducedMorseComplexes.keys()) > persistence:
                self.reducedMorseComplexes[persistence] = CancelCriticalPairs(self.MorseComplex, persistence, 
                                                                              self.Vertices, self.Edges, self.Faces)
                
            # else: choose the closest already calculated persistence and start from there
            else:
                key_array = np.array([list(self.reducedMorseComplexes.keys())])
                closest_smaller = key_array[key_array < persistence].max()
                self.reducedMorseComplexes[persistence] = CancelCriticalPairs(self.reducedMorseComplexes[closest_smaller], 
                                                                              persistence, self.Vertices, self.Edges, self.Faces)
                
                if persistence >= self.range and not self._flag_SalientEdge:
                    self.maximalReducedComplex = self.reducedMorseComplexes[persistence]
                    self.maximalReducedComplex.maximalReduced = True
                    self._flag_SalientEdge = True
                    print("Persistence was higher than the range of function values,")
                    print("therefore this complex is maximally reduced and can be used for salient edge extraction.")
                 
        return self.reducedMorseComplexes[persistence]
    
    def plot_MorseComplex(self, MorseComplex, filename, path_color=[255,0,255]):
        write_overlay_ply_file(MorseComplex, self.Vertices, self.Edges, self.Faces, filename, color_paths=path_color)
        
    def plot_MorseComplex_thresholded(self, MorseComplex, filename, threshold, path_color=[255,0,255]):
        write_overlay_ply_file_thresholded(MorseComplex, self.Vertices, self.Edges, self.Faces, filename, threshold, color_paths=path_color)
        
    def plot_MorseComplex_pline(self, persistence, filename):
        write_pline_file(self.reducedMorseComplexes[persistence], self.Vertices, self.Edges, self.Faces, filename)
        
    def plot_MorseComplex_thresholded_pline(self, persistence, filename, minimum_length=3, thresh=0.1):
        write_pline_file_thresholded(self.reducedMorseComplexes[persistence], 
                                     minimum_length, thresh, 
                                     self.Vertices, self.Edges, self.Faces, filename)
        
        
    def ExtractMorseCells(self, MorseComplex):
        if MorseComplex.persistence not in self.MorseCells.keys():
            self.MorseCells[MorseComplex.persistence] = get_MorseCells(MorseComplex, self.Vertices, 
                                                                       self.Edges, self.Faces)
            return self.MorseCells[MorseComplex.persistence]
        else:
            print("MorseCells for the MorseComplex with this persistence have already been calculated!")
            print("You can access the MorseCells dictionary via: .MorseCells[persistence]")
            print("where the persistence can be retrieved from MorseComplex.persistence") 
            
    def GetConnectivityGraph(self, persistence):
        if persistence not in self.MorseCells.keys():
            raise ValueError('No MorseCell calculated for this persistence!')
        else:
            return create_CellConnectivityGraph(self.MorseCells[persistence], self.Vertices, self.Edges)
            
    def plot_MorseCells(self, persistence, filename):
        if persistence not in self.MorseCells.keys():
            raise ValueError('No MorseCell calculated for this persistence!')
        else:
            write_cells_overlay_ply_file(self.MorseCells[persistence], self.Vertices, filename)
            
    def write_MorseCellLabels(self, persistence, filename):
        if persistence not in self.MorseCells.keys():
            raise ValueError('Morse Cells for this persistence have not been calculated!')
        else:
            write_labels_txt_file(self.MorseCells[persistence], filename)
            
    def plot_salient_edge_histogram(self, nb_bins = 15, log=False, filename = None):
        if not self._flag_SalientEdge:
            raise ValueError('Cannot plot histogram, since complex is not maximal reduced (at least flag is not set).')
        if filename == None:
            plot_salient_edge_histogramm(self.maximalReducedComplex, nb_bins, log=log)
        else:
            plot_salient_edge_histogramm(self.maximalReducedComplex, nb_bins, 
                                         log=log, save=True, filename=filename)
            
    def plot_salient_edge(self, filename, thresh):
        if self._flag_SalientEdge:
            write_salient_edge_file(self.maximalReducedComplex, self.Vertices, self.Edges, self.Faces, 
                                    thresh, filename, color_paths=[255,0,255])
        else:
            print("Need to calculate maximally reduced MorseComplex first for Salient Edges:")
            self.ReduceMorseComplex(self.range)
            
            write_salient_edge_file(self.maximalReducedComplex, self.Vertices, self.Edges, self.Faces, 
                                    thresh, filename, color_paths=[255,0,255])
            
    def plot_salient_edge_pline(self, filename, thresh):
        if self._flag_SalientEdge:
            write_salient_edge_pline(self.maximalReducedComplex, self.Vertices, self.Edges, self.Faces, 
                                    thresh, filename)
        else:
            print("Need to calculate maximally reduced MorseComplex first for Salient Edges:")
            self.ReduceMorseComplex(self.range)
            
            write_salient_edge_pline(self.maximalReducedComplex, self.Vertices, self.Edges, self.Faces, 
                                    thresh, filename)
            
            
    def plot_improved_salient_edge(self, filename, thresh, min_thresh, max_thresh):
        if self._flag_SalientEdge:
            write_improved_salient_edge_file(self.maximalReducedComplex, min_thresh, max_thresh, self.Vertices, 
                                             self.Edges, self.Faces, thresh, filename, color_paths=[255,0,255])
        else:
            print("Need to calculate maximally reduced MorseComplex first for Salient Edges:")
            self.ReduceMorseComplex(self.range)
            
            write_improved_salient_edge_file(self.maximalReducedComplex, min_thresh, max_thresh, self.Vertices, 
                                             self.Edges, self.Faces, thresh, filename, color_paths=[255,0,255])
    
    def calculate_BettiNumbers(self):
        if not self._flag_BettiNumbers:
            betti, partner0, partner1, partner2 = BettiViaPairCells(self.MorseComplex)
            self.BettiNumbers = betti
            self.MorseComplex.BettiNumbers = betti
            self.MorseComplex._flag_BettiNumbers = True
            
            self.partner = {}
            self.partner[0] = partner0
            self.partner[1] = partner1
            self.partner[2] = partner2
            self._flag_BettiNumbers = True
        print("Betti Numbers: ", betti)
        
    def plot_PersistenceDiagram(self, pointsize = 4, save = False, filepath = None):
        if self._flag_BettiNumbers:
            PersistenceDiagram(self.MorseComplex, self.partner, self.max, self.min, pointsize = pointsize, save = save, filepath = filepath)
        else:
            raise ValueError('Can not calculate Persistence Diagram before Betti Numbers!')
            
            
    def SalientEdgeConnectivityGraph(self, thresh, persistence):
        if persistence not in self.MorseCells.keys():
            raise ValueError('No MorseCell calculated for this persistence!')
        elif not self._flag_SalientEdge:
            raise ValueError('Need maximally reduced complex for salient edges!')
        else:
            salient_edge_points = get_salient_edge_indices(self.maximalReducedComplex, thresh, self.Vertices, self.Edges, self.Faces)
            
            return create_SalientEdgeCellConnectivityGraph(self.MorseCells[persistence], salient_edge_points, self.Vertices, self.Edges), salient_edge_points
    
    