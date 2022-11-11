"""! @brief Morse Theory Framework."""
##
# @mainpage Morse Theory Framework
#
# @section description_main Description
# A framework for using discrete Morse Theory on 3D triangluar meshes. Can be used for segmentation 
# when loading in a suitable scalar function (e.g. curvature values on each vertex).
#
# @section contains_main Contains
# A morse class that can load a 3D mesh (ply files only at the moment) and perform various Morse Theory
# computations, as well as a segmentation method and various plotting functions.
#
# @section libraries_install_main Libraries to install
# - plyfile library (https://github.com/dranjan/python-plyfile)
#   - Required for reading ply file
#
# @section libraries_standard_main Standard Libraries
# - numpy
# - collections
# - timeit
# - os
# - copy
# - itertools
#
# @section notes_main Notes
# - Currently worked on.

##
# @file morse.py
#
# @brief Stores the Morse dataclass used for all Morse Theory related computations.


# import stuff
from src.Algorithms.LoadData.read_ply import read_ply
from src.Algorithms.LoadData.read_funvals import read_funvals
from src.Algorithms.ProcessLowerStars import ProcessLowerStars
from src.Algorithms.ExtractMorseComplex import ExtractMorseComplex
from src.Algorithms.ReduceMorseComplex import CancelCriticalPairs
from src.Algorithms.BettiNumbers import BettiViaPairCells

from src.Algorithms.MorseCells import get_MorseCells
from src.Algorithms.EdgeDetection import get_salient_edge_indices, edge_detection

from src.Algorithms.PersistenceDiagram import PersistenceDiagram

from src.PlotData.write_MSComplex_overlay_ply_file import write_MSComplex_overlay_ply_file
from src.PlotData.write_Cell_labels_overlay_ply_file import write_Cell_labels_overlay_ply_file

from src.PlotData.write_SalientEdge_overlay_ply import write_SalientEdge_overlay_ply_file, plot_salient_edge_histogramm
from src.PlotData.write_salient_edge_pline import write_salient_edge_pline

from src.PlotData.write_Cell_labels_txt import write_Cell_labels_txt_file, write_funval_thresh_labels_txt_file
from src.PlotData.plot_fun_val_statistics import plot_fun_val_histogramm, plot_critical_fun_val_histogramm

from src.Algorithms.plot_bdpts import write_overlay_bd

from src.mesh import Mesh

# import libraries
import timeit
import os
import numpy as np
from copy import deepcopy
import itertools


class Morse(Mesh):
    def __init__(self):
        super().__init__()
    
    ''' DATALOADING'''
    
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
        
    ''' MORSE THEORY'''
    
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
    
    def ExtractMorseCells(self, persistence):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce Morse complex to this persistence first...")
            self.ReduceMorseComplex(persistence)
        if not self.reducedMorseComplexes[persistence]._flag_MorseCells:
            get_MorseCells(self.reducedMorseComplexes[persistence], self.Vertices, self.Edges, self.Faces)
            return self.reducedMorseComplexes[persistence].MorseCells
        else:
            print("MorseCells for the MorseComplex with this persistence have already been calculated!")
            
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
    
    ''' SEGMENTATION'''
    
    def Segmentation(self, persistence, thresh_large, thresh_small, merge_threshold, minimum_labels=3):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce Morse complex to this persistence first...")
            self.ReduceMorseComplex(persistence)
        if self.reducedMorseComplexes[persistence]._flag_MorseCells == False:
            print("No Morse Cells computed for this persistence, computing now...")
            self.ExtractMorseCells(persistence)
        if not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges...")
            self.ReduceMorseComplex(self.range)
            
        salient_edge_points = self.get_salient_edges(thresh_large, thresh_small)
        
        self.reducedMorseComplexes[persistence].create_segmentation(salient_edge_points, thresh_large, thresh_small, merge_threshold, minimum_labels=minimum_labels)
        
        return self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, thresh_small)][merge_threshold]
    
    def get_salient_edges(self, thresh_high, thresh_low=None):
        # if only one threshold given: use same strong and weak edge threshold
        if thresh_low == None:
            thresh_low = thresh_high
        # if no maximally reduced MorseComplex has been calculated: do that now
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.ReduceMorseComplex(self.range)
        edges = edge_detection(self.maximalReducedComplex, thresh_high, thresh_low, 
                               self.Vertices, self.Edges, self.Faces)
        return edges
    
    def Pipeline(self, infilename, outfilename, quality_index, inverted, 
                 persistences, high_thresh, low_thresh, merge_thresh):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_ply(infilename, quality_index, inverted)
            t2 = timeit.default_timer()
            f.write("ReadData: "+str(t2-t1)+"\n")
            self.ProcessLowerStars()
            t3 = timeit.default_timer()
            f.write("ProcessLowerStars: "+str(t3-t2)+"\n")
            self.ExtractMorseComplex()
            t4 = timeit.default_timer()
            f.write("ExtractMorseComplex: "+str(t4-t3)+"\n")
            self.ReduceMorseComplex(self.range)
            t5 = timeit.default_timer()
            f.write("ReduceMaximally: "+str(t5-t4)+"\n")

            for pers in persistences:
                t6 = timeit.default_timer()
                self.ReduceMorseComplex(pers)
                t7 = timeit.default_timer()
                f.write("\tReduce "+str(pers)+": "+str(t7-t6)+"\n")
                self.ExtractMorseCells(pers)
                t8 = timeit.default_timer()
                f.write("\tMorseCells "+str(pers)+": "+str(t8-t7)+"\n")
                
                f.write("\t\tSegmentation (high,low,merge): time\n")
                for high, low, merge in list(itertools.product(high_thresh, low_thresh, merge_thresh)):
                    if high > low:
                        t9 = timeit.default_timer()
                        self.SalientEdgeSegmentation_DualThresh(pers, high, low, merge)
                        t10 = timeit.default_timer()
                        f.write("\t\t"+str(high)+" "+str(low)+" "+str(merge)+": "+str(t10-t9)+"\n")
                        self.write_DualSegmentationLabels(pers, high, low, merge, outfilename)
                        
    def Pipeline_semiAuto(self, infilename, outfilename, quality_index, inverted, 
                          merge_thresh):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_ply(infilename, quality_index, inverted)
            t2 = timeit.default_timer()
            f.write("ReadData: "+str(t2-t1)+"\n")
            self.ProcessLowerStars()
            t3 = timeit.default_timer()
            f.write("ProcessLowerStars: "+str(t3-t2)+"\n")
            self.ExtractMorseComplex()
            t4 = timeit.default_timer()
            f.write("ExtractMorseComplex: "+str(t4-t3)+"\n")
            self.ReduceMorseComplex(self.range)
            t5 = timeit.default_timer()
            f.write("ReduceMaximally: "+str(t5-t4)+"\n")
            
            # automated threshold finding (parameters might need changes)
            stats = self.plot_funval_histogram(nb_bins = 3, show = False)
            sorted_funvals = sorted(stats['fun_vals'])
            newlen_pers=int(0.08*len(sorted_funvals))
            newlen_high_thresh=int(0.065*len(sorted_funvals))
            newlen_low_thresh=int(0.09*len(sorted_funvals))
            
            pers = sorted_funvals[-newlen_pers]
            high_thresh = sorted_funvals[-newlen_high_thresh]
            low_thresh = sorted_funvals[-newlen_low_thresh]

            t6 = timeit.default_timer()
            self.ReduceMorseComplex(pers)
            t7 = timeit.default_timer()
            f.write("\tReduce "+str(pers)+": "+str(t7-t6)+"\n")
            self.ExtractMorseCells(pers)
            t8 = timeit.default_timer()
            f.write("\tMorseCells "+str(pers)+": "+str(t8-t7)+"\n")

            f.write("\t\tSegmentation (high,low,merge): time\n")
            for merge in merge_thresh:
                t9 = timeit.default_timer()
                self.SalientEdgeSegmentation_DualThresh(pers, high_thresh, low_thresh, merge)
                t10 = timeit.default_timer()
                f.write("\t\t"+str(high_thresh)+" "+str(low_thresh)+" "+str(merge)+": "+str(t10-t9)+"\n")
                self.write_DualSegmentationLabels(pers, high_thresh, low_thresh, merge, outfilename)
    
    ''' PLOTTING'''
        
    def plot_funval_histogram(self, nb_bins = 15, log=False, save = False, filepath = None, show = True):
        stats = plot_fun_val_histogramm(self.Vertices, nb_bins=nb_bins, log=log, save=save, filepath=filepath, show=show)
        return stats
    
    def plot_critical_funval_histogramm(self, persistence, nb_bins=15, log=False, save = False, filepath = None, show = True):
        stats = plot_critical_fun_val_histogramm(self.reducedMorseComplexes[persistence], nb_bins=nb_bins, log=log, save=save, filepath=filepath, show=show)
        return stats
    
    def write_funval_thresh_labels(self, thresh, filename):
        write_funval_thresh_labels_txt_file(self.Vertices, thresh, filename)
 
    def plot_MorseComplex_ply(self, persistence, filename, path_color=[255,0,255]):
        """! @brief Writes a ply file that contains colored points to be viewed on top of the original mesh. 
        Visualizes the Morse Complex at the given persistence level with red = minima, green = saddles, 
        blue = maxima, and separatrix = given color (default pink).
        
        @param persistence The persistence of the Morse Complex to be plotted.
        @param filename The name of the output file. "_(persistence)P_OverlayMorseComplex" will be added.
        @param path_color (Optional) A 3-array (RGB) which gives the color of the separatrices. 
        Default is pink (255,0,255)
        """
        write_MSComplex_overlay_ply_file(self.reducedMorseComplexes[persistence], 
                                         self.Vertices, self.Edges, self.Faces, 
                                         filename, color_paths=path_color)
        
    def plot_MorseCells_ply(self, persistence, filename):
        """! @brief Writes a ply file that contains colored points to be viewed on top of the original mesh.
        Visualizes the MorseCells for the MorseComplex of the given persistence in 13 different colors. (Cannot 
        guarantee that neighboring labels have different colors!).
        
        @param persistence The persistence of the Morse Complex whose Cells should be plotted.
        @param filename The name of the output file. "_(persistence)P_OverlayCells" will be added.
        """
        if persistence not in self.reducedMorseComplexes.keys():
            raise ValueError('No reduced Morse Complex calculated for this persistence!')
        elif self.reducedMorseComplexes[persistence]._flag_MorseCells == False:
            raise ValueError('No Morse cells computed for the Morse complex with this persistence!')
        else:
            write_Cell_labels_overlay_ply_file(self.reducedMorseComplexes[persistence].MorseCells.Cells, 
                                               self.Vertices, filename + "_"+str(persistence)+"P")
            
    def plot_MorseCells_label_txt(self, persistence, filename):
        """! @brief Writes a txt label file (first col index, second col label) that can be read in by GigaMesh as labels.
        Each label is a Morse Cell from the Morse Complex of the given persistence.
        
        @param persistence The persistence of the Morse Complex whose Cells should be plotted.
        @param filename The name of the output file.
        """
        if persistence not in self.reducedMorseComplexes.keys():
            raise ValueError('No reduced Morse Complex calculated for this persistence!')
        elif self.reducedMorseComplexes[persistence]._flag_MorseCells == False:
            raise ValueError('No Morse cells computed for the Morse complex with this persistence!')
        else:
            write_Cell_labels_txt_file(self.reducedMorseComplexes[persistence].MorseCells.Cells, filename)
            
    def plot_Segmentation_label_txt(self, persistence, thresh_large, thresh_small, merge_threshold, filename):
        """! @brief Writes a txt label file (first col index, second col label) that can be read in by GigaMesh as labels.
        Each label is a Cell from the Segmentation of the given parameter combination. 
        
        @details The parameters used are also stored in the header of the file.
        
        @param persistence The persistence used for the segmentation.
        @param thresh_large The thresh_large used for the segmentation.
        @param thresh_small The thresh_small used for the segmentation.
        @param merge_threshold The merge_threshold used for the segmentation.
        @param filename The name of the output file. The parameters will be added to the filename.
        """
        if persistence not in self.reducedMorseComplexes.keys():
            raise ValueError('Segmentation for this persistence has not been calculated!')
        if (thresh_large, thresh_small) not in self.reducedMorseComplexes[persistence].Segmentations.keys():
            raise ValueError('Segmentation for this salient edge threshold pair has not been calculated!')
        if merge_threshold not in self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, thresh_small)].keys():
            raise ValueError('Segmentation for this merge percentage threshold has not been calculated!')
        else:
            write_Cell_labels_txt_file(self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, thresh_small)][merge_threshold].Cells, 
                                       filename+ "_" + str(persistence) + "P_" + str(thresh_large) + "-" + str(thresh_small) 
                                       + "T_" + str(merge_threshold),
                                       params = [persistence, thresh_large, thresh_small, merge_threshold])
            
    def plot_SalientEdges_ply(self, filename, thresh_high, thresh_low = None):
        """! @brief Writes a ply file that contains colored points to be viewed on top of the original mesh.
        Visualizes the (double) threshold salient edges. Points belonging to a strong edge are colored red, points
        from weak edges are colored blue.
        
        @param filename The name of the output file. "_()Tlow_()Thigh_OverlaySalientEdge" will be added to the filename.
        @param thresh_high The high threshold for salient edges (or single threshold)
        @param thresh_low (Optional) The low threshold for salient edges. Not necessary if single threshold is wished. 
        """
        if thresh_low == None:
            thresh_low = thresh_high
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.ReduceMorseComplex(self.range)
        write_SalientEdge_overlay_ply_file(self.maximalReducedComplex, 
                                            self.Vertices, self.Edges, self.Faces,
                                            thresh_high, thresh_low, 
                                            filename, color_high=[255,0,0], color_low=[0,0,255])
      
    def plot_PersistenceDiagram(self, pointsize = 4, save = False, filepath = None):
        if self._flag_BettiNumbers:
            PersistenceDiagram(self.MorseComplex, self.partner, self.max, self.min, pointsize = pointsize, save = save, filepath = filepath)
        else:
            raise ValueError('Can not calculate Persistence Diagram before Betti Numbers!')
            
    def plot_salient_edge_histogram(self, nb_bins = 15, log=False, filename = None):
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.ReduceMorseComplex(self.range)
        if filename == None:
            plot_salient_edge_histogramm(self.maximalReducedComplex, nb_bins, log=log)
        else:
            plot_salient_edge_histogramm(self.maximalReducedComplex, nb_bins, 
                                         log=log, save=True, filename=filename)
    
    