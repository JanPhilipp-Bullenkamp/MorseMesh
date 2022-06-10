from Algorithms.LoadData.Datastructure import Vertex, Edge, Face
from Algorithms.LoadData.read_ply import read_ply, read_normals_from_ply
from Algorithms.LoadData.read_funvals import read_funvals
from Algorithms.ProcessLowerStars import ProcessLowerStars
from Algorithms.ExtractMorseComplex import ExtractMorseComplex
from Algorithms.ReduceMorseComplex import CancelCriticalPairs
from Algorithms.BettiNumbers import BettiViaPairCells

from Algorithms.MorseCells import get_MorseCells, create_SalientEdgeCellConnectivityGraph
from Algorithms.SalientEdgeIndices import get_salient_edge_indices, get_salient_edge_indices_dual_thr

from Algorithms.PersistenceDiagram import PersistenceDiagram

from PlotData.write_overlay_ply_file import write_overlay_ply_file, write_overlay_ply_file_thresholded
from PlotData.write_labeled_cells_overlay import write_cells_overlay_ply_file
from PlotData.write_salient_edge_overlay import write_salient_edge_file, write_dual_thresh_salient_edge_file, write_improved_salient_edge_file, plot_salient_edge_histogramm
from PlotData.write_salient_edge_pline import write_salient_edge_pline
from PlotData.write_labels_txt import write_labels_txt_file, write_funval_thresh_labels_txt_file
from PlotData.write_pline_file import write_pline_file, write_pline_file_thresholded
from PlotData.plot_fun_val_statistics import plot_fun_val_histogramm


from Algorithms.plot_bdpts import write_overlay_bd

import timeit
import os
import numpy as np
from copy import deepcopy
import itertools

from mesh import Mesh

class Morse(Mesh):
    def __init__(self):
        super().__init__()

    def load_mesh_ply(self, filename, quality_index, inverted=False):
        min_val, max_val = read_ply(filename, quality_index, self.Vertices, 
                                    self.Edges, self.Faces, inverted=inverted)
        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        
    def load_new_funvals(self, filename):
        min_val, max_val = read_funvals(filename, self.Vertices, self.Edges, self.Faces)
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        
    def load_normals_ply(self, filename):
        read_normals_from_ply(filename, self.Vertices)
        
    def plot_funval_histogram(self, nb_bins = 15, log=False, save = False, filepath = None):
        plot_fun_val_histogramm(self.Vertices, nb_bins = nb_bins, log=log, save = save, filepath = filepath)
        
    def write_funval_thresh_labels(self, thresh, filename):
        write_funval_thresh_labels_txt_file(self.Vertices, thresh, filename)
 
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
    
    def ExtractMorseComplex(self):
        if not self._flag_ProcessLowerStars:
            raise ValueError('Need to call ProcessLowerStars first, cannot calculate MorseComplex otherwise!')
        else:
            if self._flag_MorseComplex:
                self.MorseComplex = None

            self.MorseComplex = ExtractMorseComplex(self.Vertices, self.Edges, self.Faces, 
                                                    self.V12, self.V23, self.C)
            self.reducedMorseComplexes[0] = self.MorseComplex
            self.MorseComplex.filename = self.filename
            self._flag_MorseComplex = True
        
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
                    print("Persistence was high enough that this complex is maximally reduced.")
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
                    print("Persistence was high enough that this complex is maximally reduced.")
                 
        return self.reducedMorseComplexes[persistence]
    
    def plot_MorseComplex(self, persistence, filename, path_color=[255,0,255]):
        write_overlay_ply_file(self.reducedMorseComplexes[persistence], 
                               self.Vertices, self.Edges, self.Faces, 
                               filename, color_paths=path_color)
        
    def plot_MorseComplex_thresholded(self, persistence, filename, threshold, path_color=[255,0,255]):
        write_overlay_ply_file_thresholded(self.reducedMorseComplexes[persistence], 
                                           self.Vertices, self.Edges, self.Faces, 
                                           filename, threshold, color_paths=path_color)
        
    def plot_MorseComplex_pline(self, persistence, filename):
        write_pline_file(self.reducedMorseComplexes[persistence], 
                         self.Vertices, self.Edges, self.Faces, filename)
        
    def plot_MorseComplex_thresholded_pline(self, persistence, filename, minimum_length=3, thresh=0.1):
        write_pline_file_thresholded(self.reducedMorseComplexes[persistence], 
                                     minimum_length, thresh, 
                                     self.Vertices, self.Edges, self.Faces, filename)
        
        
    def ExtractMorseCells(self, persistence):
        if persistence not in self.MorseCells.keys():
            self.MorseCells[persistence] = get_MorseCells(self.reducedMorseComplexes[persistence], 
                                                          self.Vertices, self.Edges, self.Faces)
            return self.MorseCells[persistence]
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
            
    def plot_double_thresh_salient_edge(self, filename, thresh_high, thresh_low):
        if self._flag_SalientEdge:
            write_dual_thresh_salient_edge_file(self.maximalReducedComplex, 
                                                self.Vertices, self.Edges, self.Faces,
                                                thresh_high, thresh_low, 
                                                filename, color_high=[255,0,0], color_low=[0,0,255])
        else:
            print("Need to calculate maximally reduced MorseComplex first for Salient Edges:")
            self.ReduceMorseComplex(self.range)
            
            write_dual_thresh_salient_edge_file(self.maximalReducedComplex, 
                                                self.Vertices, self.Edges, self.Faces, 
                                                thresh_high, thresh_low, 
                                                filename, color_high=[255,0,0], color_low=[0,0,255])
            
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
            
            
    def SalientEdgeSegmentation(self, persistence, thresh,  edge_percent):
        if persistence not in self.MorseCells.keys():
            raise ValueError('No MorseCell calculated for this persistence!')
        elif not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges!")
            print("Computing maximally reduced complex ...")
            self.ReduceMorseComplex(self.range)
        
        if persistence not in self.Segmentation.keys():
            self.Segmentation[persistence] = {}
            
        if thresh not in self.Segmentation[persistence].keys():
            self.Segmentation[persistence][thresh] = {}
            
        if edge_percent in self.Segmentation[persistence][thresh].keys():
            print("Segmentation for these parameters has been calculated already: Persistence", persistence, ", SalientEdge Threshold",thresh, ", Edge Percentage", edge_percent)
        else:
            salient_edge_points = get_salient_edge_indices(self.maximalReducedComplex, thresh, self.Vertices, self.Edges, self.Faces)
            
            Cells = deepcopy(self.MorseCells[persistence])
            
            self.Segmentation[persistence][thresh][edge_percent] = {}
            self.Segmentation[persistence][thresh][edge_percent]["Graph"] = create_SalientEdgeCellConnectivityGraph(Cells, 
                                                                                                                    salient_edge_points,
                                                                                                                    self.Vertices,
                                                                                                                    self.Edges)
            start_time = timeit.default_timer()
            # merge cells 40 iterations:
            for i in range(40):
                Cells = self.Segmentation[persistence][thresh][edge_percent]["Graph"].simplify_cells(Cells, edge_percent, salient_edge_points, self.Vertices)
            # remove small components:
            Cells = self.Segmentation[persistence][thresh][edge_percent]["Graph"].remove_small_components(Cells, size_thresh=300)
            
            self.Segmentation[persistence][thresh][edge_percent]["Cells"] = Cells
            
            end_time = timeit.default_timer() - start_time
            print('Time merging and simplifying Cells:', end_time)
            
            print("Segmented for",persistence, "persistence Complex with", thresh, "salient edge threshold and", edge_percent*100, "% edge percentage merging threshold")
            print("Got ",len(self.Segmentation[persistence][thresh][edge_percent]["Graph"].conncomps),"differnt cell labels")
        
        return self.Segmentation[persistence][thresh][edge_percent]
    
    def SalientEdgeSegmentation_DualThresh(self, persistence, thresh_high, thresh_low,  edge_percent):
        if persistence not in self.MorseCells.keys():
            raise ValueError('No MorseCell calculated for this persistence!')
        elif not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges!")
            print("Computing maximally reduced complex ...")
            self.ReduceMorseComplex(self.range)
        
        if persistence not in self.SegmentationDual.keys():
            self.SegmentationDual[persistence] = {}
            
        if thresh_high not in self.SegmentationDual[persistence].keys():
            self.SegmentationDual[persistence][thresh_high] = {}
            
        if thresh_low not in self.SegmentationDual[persistence][thresh_high].keys():
            self.SegmentationDual[persistence][thresh_high][thresh_low] = {}
            
        if edge_percent in self.SegmentationDual[persistence][thresh_high][thresh_low].keys():
            print("Segmentation for these parameters has been calculated already: Persistence", persistence, ", SalientEdge Threshold",thresh_high, thresh_low, ", Edge Percentage", edge_percent)
        else:
            salient_edge_points = self.dual_thresh_edges(thresh_high, thresh_low)
            
            Cells = deepcopy(self.MorseCells[persistence])
            
            self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent] = {}
            self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"] = create_SalientEdgeCellConnectivityGraph(Cells, 
                                                                                                                    salient_edge_points,
                                                                                                                    self.Vertices,
                                                                                                                    self.Edges)
            start_time = timeit.default_timer()
            # merge cells 40 iterations:
            for i in range(40):
                Cells = self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].simplify_cells(Cells, edge_percent, salient_edge_points, self.Vertices)
            # remove small components:
            Cells = self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].remove_small_components(Cells, size_thresh=300)
            
            # remove enclosures
            Cells = self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].remove_small_enclosures(Cells)
            
            
            self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Cells"] = Cells
            
            end_time = timeit.default_timer() - start_time
            print('Time merging and simplifying Cells:', end_time)
            
            print("Segmented for",persistence, "persistence Complex with", thresh_high, thresh_low, "salient edge threshold and", edge_percent*100, "% edge percentage merging threshold")
            print("Got ",len(self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].conncomps),"differnt cell labels")
        
        return self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]
    
    def write_SegmentationLabels(self, persistence, thresh, edge_percent, filename):
        if persistence not in self.Segmentation.keys():
            raise ValueError('Segmentation for this persistence has not been calculated!')
        if thresh not in self.Segmentation[persistence].keys():
            raise ValueError('Segmentation for this salient edge threshold has not been calculated!')
        if edge_percent not in self.Segmentation[persistence][thresh].keys():
            raise ValueError('Segmentation for this edge percentage threshold has not been calculated!')
        else:
            write_labels_txt_file(self.Segmentation[persistence][thresh][edge_percent]["Cells"], 
                                  filename+"_"+str(persistence)+"P_"+str(thresh)+"T_"+str(edge_percent)+"EP_smallRem")
            
    def write_DualSegmentationLabels(self, persistence, thresh_high, thresh_low, edge_percent, filename):
        if persistence not in self.SegmentationDual.keys():
            raise ValueError('Segmentation for this persistence has not been calculated!')
        if thresh_high not in self.SegmentationDual[persistence].keys():
            raise ValueError('Segmentation for this high salient edge threshold has not been calculated!')
        if thresh_low not in self.SegmentationDual[persistence][thresh_high].keys():
            raise ValueError('Segmentation for this low salient edge threshold has not been calculated!')
        if edge_percent not in self.SegmentationDual[persistence][thresh_high][thresh_low].keys():
            raise ValueError('Segmentation for this edge percentage threshold has not been calculated!')
        else:
            write_labels_txt_file(self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Cells"], 
                                  filename+"_"+str(persistence)+"P_"+str(thresh_high)+"-"+str(thresh_low)+"T_"+str(edge_percent)+"EP_smallRem")
            
    def _get_neighbors(self, vert):
        neighbors_ind = set()
        for star_edge in vert.star["E"]:
            neighbors_ind.update(self.Edges[star_edge].indices)

        neighbors_ind.remove(vert.index)
        return neighbors_ind
            
    def dual_thresh_edges(self, thresh_high, thresh_low):
        #self.ReduceMorseComplex(self.range)
        strong_edge, weak_edge = get_salient_edge_indices_dual_thr(self.maximalReducedComplex, 
                                                                thresh_high, thresh_low, 
                                                                self.Vertices, self.Edges, self.Faces)
        
        queue = []
        for ind in strong_edge:
            neighbors = self._get_neighbors(self.Vertices[ind])
            for nei in neighbors:
                if nei in weak_edge:
                    queue.append(nei)
                    weak_edge.remove(nei)
                    
        added = len(queue)
        for elt in queue:
            strong_edge.add(elt)
        
        while len(queue) != 0:
            ind = queue.pop(0)
            neighbors = self._get_neighbors(self.Vertices[ind])
            for nei in neighbors:
                if nei in weak_edge:
                    queue.append(nei)
                    strong_edge.add(nei)
                    weak_edge.remove(nei)
                    added+=1
        #write_overlay_bd(strong_edge, self.Vertices, "test_"+str(thresh_low)+"-"+str(thresh_high))            
        #print("Added", added, "points by weak threshold in", thresh_low, thresh_high)
        return strong_edge
    
    def Pipeline(self, filename, filename_normals, quality_index, inverted, 
                 persistences, high_thresh, low_thresh, merge_thresh):
        
        self.load_mesh_ply(filename, quality_index, inverted)
        self.load_normals_ply(filename_normals)
        self.ProcessLowerStars()
        self.ExtractMorseComplex()
        self.ReduceMorseComplex(self.range)
        
        for pers in persistences:
            self.ReduceMorseComplex(pers)
            self.ExtractMorseCells(pers)
            
            for high, low, merge in list(itertools.product(high_thresh, low_thresh, merge_thresh)):
                if high > low:
                    self.SalientEdgeSegmentation_DualThresh(pers, high, low, merge)
                    self.write_DualSegmentationLabels(pers, high, low, merge, str(self.filename))