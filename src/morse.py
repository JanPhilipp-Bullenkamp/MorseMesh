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
from src.Algorithms.load_data.read_ply import read_ply
from src.Algorithms.load_data.anisotropic_diffusion import smooth_function_values
from src.Algorithms.load_data.read_or_process_funvals import read_funvals, apply_perona_malik_diffusion
from src.Algorithms.process_lower_stars import process_lower_stars
from src.Algorithms.extract_morse_complex import extract_morse_complex
from src.Algorithms.reduce_morse_complex import cancel_critical_pairs
from src.Algorithms.betti_numbers import betti_via_pair_cells

from src.Algorithms.morse_cells import get_morse_cells
from src.Algorithms.edge_detection import ridge_detection, valley_detection

from src.Algorithms.cluster import cluster_mesh, merge_cluster

from src.Algorithms.roughness_test import variance_heat_map, extremal_points_ratio

from src.plot_data.persistence_diagram import persistence_diagram
from src.plot_data.write_overlay_ply_files import write_MSComplex_overlay_ply_file, write_MSComplex_detailed_overlay_ply_file, write_Cell_labels_overlay_ply_file, write_SalientEdge_overlay_ply_file
from src.plot_data.write_labels_txt import write_Cell_labels_txt_file, write_funval_thresh_labels_txt_file, write_variance_heat_map_labels_txt_file
from src.plot_data.statistics import fun_val_statistics, critical_fun_val_statistics, salient_edge_statistics

from src.plot_data.plot_points_for_debugging import write_overlay_points

from src.mesh import Mesh

from src.timer import timed

# import libraries
import timeit
import os
import numpy as np
import itertools

from src.Algorithms.load_data.read_ply_test import load_ply


class Morse(Mesh):
    def __init__(self):
        super().__init__()

    @timed
    def seed_cluster_mesh(self, bd_pts: set, num_seeds: int) -> dict:
        return cluster_mesh(self.Vertices, bd_pts, num_seeds)

    @timed
    def cluster_segmentation(self, cluster: dict, bd_points: set, threshold: float):
        return merge_cluster(cluster, bd_points, threshold)
    
    ''' DATALOADING'''
    @timed
    def load_mesh_new(self, filename: str, morse_function: str = "quality", inverted: bool = False):
        self.reset()

        file_obj = open(filename, 'rb')
        min_val, max_val = load_ply(file_obj, self.Vertices, self.Edges, self.Faces, morse_function=morse_function, inverted=inverted)

        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
    
    @timed
    def load_mesh_ply(self, filename: str, quality_index: int, inverted: bool = False):
        """! @brief Loads a .ply file with a Morse function taken from the given index.

        @param filename The location and filename of the ply file that should be loaded.
        @param quality_index The index position where the Morse function should be taken from in the vertices.
        @param inverted (Optional) Boolean, whether the Morse function should be inverted or not (multiplied with -1).
        """
        # Reset previously loaded data if necessary
        self.reset()
        min_val, max_val = read_ply(filename, quality_index, self.Vertices, 
                                    self.Edges, self.Faces, inverted=inverted)
        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        
    @timed    
    def load_new_funvals(self, filename: str, operation: str = "max"):
        """! @brief Loads new function values into the Mesh. Currently expects a feature vector file from Gigamesh i think.
        @param filename The location and filename of the feature vector file that should give new Morse function values.
        @param operation Optionally change the function on the feature vector: currently options are max, min, maxabs and minabs. Default is max.
        """
        min_val, max_val = read_funvals(filename, self.Vertices, self.Edges, self.Faces, operation=operation)
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        self.reset_morse()

    @timed
    def smooth_fun_vals(self, n_neighboorhood: int = 1):
        smooth_function_values(self.Vertices, n_neighboorhood)

    @timed
    def apply_perona_malik(self, iterations: int, lamb: float, k: float):
        min_val, max_val = apply_perona_malik_diffusion(self.Vertices, self.Edges, self.Faces, iterations, lamb, k)
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        self.reset_morse()
        
    ''' MORSE THEORY'''
    
    @timed
    def process_lower_stars(self):
        """! @brief Runs the process_lower_stars algorithm to get a discrete vector field representing the gradient of the discrete Morse function.

        @details Implementation of the algorithm described in Robins et al......
        """
        # reset if has been computed already
        if self._flag_process_lower_stars:
            self.reset_morse()
            
        process_lower_stars(self.Vertices, self.Edges, self.Faces, self.C, self.V12, self.V23)
        self._flag_process_lower_stars = True
        
    @timed
    def extract_morse_complex(self):
        """! @brief Runs the extract_morse_complex algorithm to get a Morse Complex.
        
        @details Implementation of the algorithm described in Robins et al ....
        """
        if not self._flag_process_lower_stars:
            print('Need to call process_lower_stars first...')
            self.process_lower_stars()
        else:
            if self._flag_MorseComplex:
                self.MorseComplex = None

            self.MorseComplex = extract_morse_complex(self.Vertices, self.Edges, self.Faces, 
                                                    self.V12, self.V23, self.C)
            self.reducedMorseComplexes[0] = self.MorseComplex
            self.MorseComplex.filename = self.filename
            self._flag_MorseComplex = True
        
    @timed
    def reduce_morse_complex(self, persistence: float):
        """! @brief Reduces the Morse complex up to the given persistence.
        @details Always cancels two critical simplices of consectutive dimensions if their function values are closer than the given 
        persistence. The resulting simplified Morse Complex is stored as a copy under reducedMorseComplexes[persistence].
        
        @param persistence The persistence up to which the Morse complex should be simplified.
        
        @return The reduced Morse Complex object.
        """
        if not self._flag_MorseComplex:
            print("Need to call extract_morse_complex first...")
            self.extract_morse_complex()
        if persistence in self.reducedMorseComplexes.keys():
            print("This persistence has already been calculated!")
            print("You can access it via .reducedMorseComplexes[persistence] ") 
        else:
            self.reducedMorseComplexes[persistence] = cancel_critical_pairs(self.MorseComplex, persistence, 
                                                                          self.Vertices, self.Edges, self.Faces)
            if persistence >= self.range and not self._flag_SalientEdge:
                self.maximalReducedComplex = self.reducedMorseComplexes[persistence]
                self.maximalReducedComplex.maximalReduced = True
                self._flag_SalientEdge = True
                separatrix_persistences = [pers for pers,_ in self.maximalReducedComplex.Separatrices]
                self.min_separatrix_persistence = min(separatrix_persistences)
                self.max_separatrix_persistence = max(separatrix_persistences)
                self.maximalReducedComplex.min_separatrix_persistence = min(separatrix_persistences)
                self.maximalReducedComplex.max_separatrix_persistence = max(separatrix_persistences)
                print("Persistence was high enough that this complex is maximally reduced.")
        return self.reducedMorseComplexes[persistence]

    @timed
    def reduce_morse_complex_salient_edge(self, thresh_high: float, thresh_low: float = None, salient_edge_pts: set = None, pers: float = None):
        if not self._flag_MorseComplex:
            print("Need to call extract_morse_complex first...")
            self.extract_morse_complex() 
        if not self._flag_SalientEdge:
            print("Need to reduce maximally first...")
            self.reduce_morse_complex(self.range)
        if salient_edge_pts == None:
            salient_edge_pts = self.get_salient_ridges(thresh_high, thresh_low)

        if pers == None:
            self.salient_reduced_morse_complexes[(thresh_high, thresh_low)] = cancel_critical_pairs(self.MorseComplex, self.range, 
                                                                            self.Vertices, self.Edges, self.Faces, salient_edge_pts=salient_edge_pts)
            return self.salient_reduced_morse_complexes[(thresh_high, thresh_low)]
        else:
            self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)] = cancel_critical_pairs(self.MorseComplex, pers,
                                                                                    self.Vertices, self.Edges, self.Faces, salient_edge_pts)
            return self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)]

    @timed
    def extract_cells_salient_complex(self, thresh_high: float, thresh_low: float = None, pers: float = None):
        """! @brief Extracts the Morse Cells of the salient reduced Morse complex.
        
        @details The extract_cells_salient_complex method extracts cells from a salient reduced Morse complex. It takes 
        in two parameters: thresh_high and thresh_low. If a Morse complex with the given thresholds has not been reduced 
        yet, it will be reduced using the reduce_morse_complex_salient_edge method. The method then calls the 
        get_morse_cells function on the reduced Morse complex, and returns the resulting MorseCells object.

        @param thresh_high The higher threshold for the salient edges.
        @param thresh_low (Optional) The lower threshold for the salient edges.

        @return Morse Cells object containing the cells of the salient reduced Morse Complex.
        """
        if pers == None:
            if (thresh_high, thresh_low) not in self.salient_reduced_morse_complexes.keys():
                print("Need to reduce with these edge thresholds first...")
                self.reduce_morse_complex_salient_edge(thresh_high, thresh_low)
            get_morse_cells(self.salient_reduced_morse_complexes[(thresh_high,thresh_low)], self.Vertices, self.Edges, self.Faces)
            return self.salient_reduced_morse_complexes[(thresh_high,thresh_low)].MorseCells
        else:
            if (pers, thresh_high, thresh_low) not in self.salient_reduced_morse_complexes.keys():
                print("Need to reduce with these edge thresholds and persistence first...")
                self.reduce_morse_complex_salient_edge(thresh_high, thresh_low, pers=pers)
            get_morse_cells(self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)], self.Vertices, self.Edges, self.Faces)
            return self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)].MorseCells
    
    @timed
    def extract_morse_cells(self, persistence: float):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce Morse complex to this persistence first...")
            self.reduce_morse_complex(persistence)
        if not self.reducedMorseComplexes[persistence]._flag_MorseCells:
            get_morse_cells(self.reducedMorseComplexes[persistence], self.Vertices, self.Edges, self.Faces)
            return self.reducedMorseComplexes[persistence].MorseCells
        else:
            print("MorseCells for the MorseComplex with this persistence have already been calculated!")
    
    @timed
    def calculate_betti_numbers(self, persistence: float = 0):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce to this persistence first...")
            self.reduce_morse_complex(persistence)
            
        betti, partner0, partner1, partner2 = betti_via_pair_cells(self.reducedMorseComplexes[persistence])

        self.reducedMorseComplexes[persistence].BettiNumbers = betti
        self.reducedMorseComplexes[persistence]._flag_BettiNumbers = True
        self.reducedMorseComplexes[persistence].partner = {}
        self.reducedMorseComplexes[persistence].partner[0] = partner0
        self.reducedMorseComplexes[persistence].partner[1] = partner1
        self.reducedMorseComplexes[persistence].partner[2] = partner2
        if persistence == 0:
            self.MorseComplex.BettiNumbers = betti
            self.MorseComplex._flag_BettiNumbers = True
            self.MorseComplex.partner = {}
            self.MorseComplex.partner[0] = partner0
            self.MorseComplex.partner[1] = partner1
            self.MorseComplex.partner[2] = partner2
        
        if self.BettiNumbers is not None:
            if betti[0]!=self.BettiNumbers[0] or betti[1]!=self.BettiNumbers[1] or betti[2]!=self.BettiNumbers[2]:
                raise AssertionError("Betti numbers have changed since last computation on this mesh... "
                                     "Shouldnt be possible as we do not change the mesh geometry")
        self.BettiNumbers = betti
        self._flag_BettiNumbers = True
        print("Betti Numbers: ", betti)
        return self.BettiNumbers
    
    ''' SEGMENTATION'''
    
    @timed
    def segmentation(self, persistence: float, thresh_large: float, thresh_small: float, merge_threshold: float, minimum_labels: int = 3, size_threshold: int = 500):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce Morse complex to this persistence first...")
            self.reduce_morse_complex(persistence)
        if self.reducedMorseComplexes[persistence]._flag_MorseCells == False:
            print("No Morse Cells computed for this persistence, computing now...")
            self.extract_morse_cells(persistence)
        if not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges...")
            self.reduce_morse_complex(self.range)
            
        salient_edge_points = self.get_salient_ridges(thresh_large, thresh_small)
        
        self.reducedMorseComplexes[persistence].create_segmentation(salient_edge_points, thresh_large, thresh_small, 
                                                                    merge_threshold, minimum_labels=minimum_labels, size_threshold=size_threshold)
        
        return self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, thresh_small)][merge_threshold]

    @timed
    def segmentation_salient_reduction(self, thresh_large: float, thresh_small: float, merge_threshold: float, persistence: float = None, minimum_labels: int = 3):
        salient_edge_points = self.get_salient_ridges(thresh_large, thresh_small)

        if persistence == None:
            self.reduce_morse_complex_salient_edge(thresh_large, thresh_small, salient_edge_points)
            self.extract_cells_salient_complex(thresh_large, thresh_small)
            self.salient_reduced_morse_complexes[(thresh_large,thresh_small)].create_segmentation(salient_edge_points, thresh_large, thresh_small,
                                                                                            merge_threshold, minimum_labels)
            return self.salient_reduced_morse_complexes[(thresh_large,thresh_small)].Segmentations[(thresh_large, thresh_small)][merge_threshold]
        else:
            self.reduce_morse_complex_salient_edge(thresh_large, thresh_small, salient_edge_points, pers=persistence)
            self.extract_cells_salient_complex(thresh_large, thresh_small, persistence)
            self.salient_reduced_morse_complexes[(persistence,thresh_large,thresh_small)].create_segmentation(salient_edge_points, thresh_large, thresh_small,
                                                                                            merge_threshold, minimum_labels)
            return self.salient_reduced_morse_complexes[(persistence,thresh_large,thresh_small)].Segmentations[(thresh_large, thresh_small)][merge_threshold]
    
    @timed
    def segmentation_no_pers(self, thresh_large: float, thresh_small: float, merge_threshold: float, minimum_labels: int = 3):
        if self.MorseComplex._flag_MorseCells == False:
            print("No Morse Cells computed for initial complex, computing now...")
            self.extract_morse_cells(0)
        if not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges...")
            self.reduce_morse_complex(self.range)
            
        salient_edge_points = self.get_salient_ridges(thresh_large, thresh_small)
        
        self.MorseComplex.create_segmentation(salient_edge_points, thresh_large, thresh_small, 
                                              merge_threshold, minimum_labels=minimum_labels)
        
        return self.MorseComplex.Segmentations[(thresh_large, thresh_small)][merge_threshold]
    
    @timed
    def get_salient_ridges(self, thresh_high: float, thresh_low: float = None, min_length: int = 1, max_length: int = None):
        # if only one threshold given: use same strong and weak edge threshold
        if thresh_low == None:
            thresh_low = thresh_high
        # if no maximally reduced MorseComplex has been calculated: do that now
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.reduce_morse_complex(self.range)
        ridges = ridge_detection(self.maximalReducedComplex, thresh_high, thresh_low, 
                               self.Vertices, self.Edges, self.Faces, min_length=min_length, max_length=max_length)
        return ridges

    @timed
    def get_salient_valleys(self, thresh_high: float, thresh_low: float = None, min_length: int = 1, max_length: int = None):
        # if only one threshold given: use same strong and weak edge threshold
        if thresh_low == None:
            thresh_low = thresh_high
        # if no maximally reduced MorseComplex has been calculated: do that now
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.reduce_morse_complex(self.range)
        valleys = valley_detection(self.maximalReducedComplex, thresh_high, thresh_low, 
                               self.Vertices, self.Edges, self.Faces, min_length=min_length, max_length=max_length)
        return valleys

    @timed
    def pipeline_salient_segmentation(self, infilename: str, outfilename: str, quality_index: int, inverted: bool, 
                                     high_thresh: float, low_thresh: float, merge_thresh: float):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_ply(infilename, quality_index, inverted)
            t2 = timeit.default_timer()
            f.write("ReadData: "+str(t2-t1)+"\n")
            self.process_lower_stars()
            t3 = timeit.default_timer()
            f.write("process_lower_stars: "+str(t3-t2)+"\n")
            self.extract_morse_complex()
            t4 = timeit.default_timer()
            f.write("extract_morse_complex: "+str(t4-t3)+"\n")
            self.reduce_morse_complex(self.range)
            t5 = timeit.default_timer()
            f.write("ReduceMaximally: "+str(t5-t4)+"\n")
            f.write("\tSegmentation (high,low,merge): time\n")
            for high, low, merge in list(itertools.product(high_thresh, low_thresh, merge_thresh)):
                if high > low:
                    t9 = timeit.default_timer()
                    self.Segmentation_SalientReduction(high, low, merge, minimum_labels=5)
                    t10 = timeit.default_timer()
                    f.write("\t"+str(high)+" "+str(low)+" "+str(merge)+": "+str(t10-t9)+"\n")
                    self.plot_segmentation_salient_edge_label_txt(high, low, merge, outfilename+str(high)+"H_"+str(low)+"L_"+str(merge)+"M")
    
    @timed
    def pipeline(self, infilename: str, outfilename: str, quality_index: int, inverted: bool, 
                 persistence: float, high_thresh: float, low_thresh: float, merge_thresh: float):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_ply(infilename, quality_index, inverted)
            t2 = timeit.default_timer()
            f.write("ReadData: "+str(t2-t1)+"\n")
            self.process_lower_stars()
            t3 = timeit.default_timer()
            f.write("process_lower_stars: "+str(t3-t2)+"\n")
            self.extract_morse_complex()
            t4 = timeit.default_timer()
            f.write("extract_morse_complex: "+str(t4-t3)+"\n")
            self.reduce_morse_complex(self.range)
            t5 = timeit.default_timer()
            f.write("ReduceMaximally: "+str(t5-t4)+"\n")
            
            for pers in persistence:
                self.reduce_morse_complex(pers)

                t7 = timeit.default_timer()
                self.extract_morse_cells(pers)
                t8 = timeit.default_timer()
                f.write("MorseCells: "+str(t8-t7)+"\n")

                f.write("\tSegmentation (high,low,merge): time\n")
                for high, low, merge in list(itertools.product(high_thresh, low_thresh, merge_thresh)):
                    if high > low:
                        t9 = timeit.default_timer()
                        self.Segmentation(pers, high, low, merge, minimum_labels=5)
                        t10 = timeit.default_timer()
                        f.write("\t"+str(high)+" "+str(low)+" "+str(merge)+": "+str(t10-t9)+"\n")
                        self.plot_segmentation_label_txt(pers, high, low, merge, outfilename)
     
    @timed
    def pipeline_semi_auto(self, infilename: str, outfilename: str, quality_index: int, inverted: bool, 
                          merge_thresh: float):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_ply(infilename, quality_index, inverted)
            t2 = timeit.default_timer()
            f.write("ReadData: "+str(t2-t1)+"\n")
            self.process_lower_stars()
            t3 = timeit.default_timer()
            f.write("process_lower_stars: "+str(t3-t2)+"\n")
            self.extract_morse_complex()
            t4 = timeit.default_timer()
            f.write("extract_morse_complex: "+str(t4-t3)+"\n")
            self.reduce_morse_complex(self.range)
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
            self.reduce_morse_complex(pers)
            t7 = timeit.default_timer()
            f.write("\tReduce "+str(pers)+": "+str(t7-t6)+"\n")
            self.extract_morse_cells(pers)
            t8 = timeit.default_timer()
            f.write("\tMorseCells "+str(pers)+": "+str(t8-t7)+"\n")

            f.write("\t\tSegmentation (high,low,merge): time\n")
            for merge in merge_thresh:
                t9 = timeit.default_timer()
                self.SalientEdgeSegmentation_DualThresh(pers, high_thresh, low_thresh, merge)
                t10 = timeit.default_timer()
                f.write("\t\t"+str(high_thresh)+" "+str(low_thresh)+" "+str(merge)+": "+str(t10-t9)+"\n")
                self.write_DualSegmentationLabels(pers, high_thresh, low_thresh, merge, outfilename)

    ''' SURFACE ROUGHNESS'''
    @timed
    def get_variance(self, n: int):
        fun_vals = [v.fun_val for v in self.Vertices.values()]
        mean_fun_val = np.mean(fun_vals)
        return variance_heat_map(self.Vertices, mean_fun_val, n)

    @timed
    def get_extremal_point_ratio(self, pers: float, n: int):
        self.reduce_morse_complex(pers)
        extremal_points = set()
        for ind in self.reducedMorseComplexes[pers].CritVertices.keys():
            extremal_points.add(ind)
        for edge_ind in self.reducedMorseComplexes[pers].CritEdges.keys():
            extremal_points.add(self.Edges[edge_ind].get_max_fun_val_index())
        for face_ind in self.reducedMorseComplexes[pers].CritFaces.keys():
            extremal_points.add(self.Faces[face_ind].get_max_fun_val_index())
        return extremal_points_ratio(self.Vertices, extremal_points, n)
    
    ''' PLOTTING'''
    @timed
    def write_variance_heat_map_labels(self, variance: dict, thresh1: float, thresh2: float, filename: str):
        write_variance_heat_map_labels_txt_file(variance, thresh1, thresh2, filename)
    
    @timed
    def write_funval_thresh_labels(self, thresh: float, filename: str):
        """! @brief Writes a txt label file (first col index, second col label) that can be read in by GigaMesh as labels.
        Labels vertices with a lower function value than the threshold blue, vertices above in green. (Labels 1 and 2).
        
        @param thresh The threshold where to distinguish the labels.
        @param filename The name of the output file. "_()thresh" will be added to the given filename
        """
        write_funval_thresh_labels_txt_file(self.Vertices, thresh, filename)
    
    @timed
    def plot_morse_complex_ply(self, persistence: float, filename: str, path_color: tuple[int, int, int] = [255,0,255], 
                              detailed: bool = False, separate_points_file: bool = False):
        """! @brief Writes a ply file that contains colored points to be viewed on top of the original mesh. 
        Visualizes the Morse Complex at the given persistence level with red = minima, green = saddles, 
        blue = maxima, and separatrix = given color (default pink).
        
        @param persistence The persistence of the Morse Complex to be plotted.
        @param filename The name of the output file. "_(persistence)P_OverlayMorseComplex" will be added.
        @param path_color (Optional) A 3-array (RGB) which gives the color of the separatrices. 
        Default is pink (255,0,255)
        @param detailed (Optional) Boolean which tells whether we want to visualize the separatrices connected
        or not. Default is false.
        @param separate_points_file (Optional) Boolean whether to write critical points into separate file (for 
        very nice visualization only, as it allows visualizing crit points without the points of the edges and faces
        in the Morse Complex. Default is False.
        """
        if detailed:
            write_MSComplex_detailed_overlay_ply_file(self.reducedMorseComplexes[persistence], 
                                                      self.Vertices, self.Edges, self.Faces, 
                                                      filename, color_paths=path_color,
                                                      separate_points_file=separate_points_file)
        else:
            write_MSComplex_overlay_ply_file(self.reducedMorseComplexes[persistence], 
                                             self.Vertices, self.Edges, self.Faces, 
                                             filename, color_paths=path_color)
    @timed  
    def plot_morse_cells_ply(self, persistence: float, filename: str):
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
    
    @timed
    def plot_morse_cells_label_txt(self, persistence: float, filename: str):
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
    
    @timed        
    def plot_segmentation_label_txt(self, persistence: float, thresh_large: float, thresh_small: float, 
                                    merge_threshold: float, filename: str):
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
    
    @timed
    def plot_segmentation_salient_edge_label_txt(self, thresh_large: float, thresh_small: float, merge_threshold: float, filename: str):
        write_Cell_labels_txt_file(self.salient_reduced_morse_complexes[(thresh_large,thresh_small)].Segmentations[(thresh_large, thresh_small)][merge_threshold].Cells, filename, params=[None, thresh_large, thresh_small, merge_threshold])

    @timed
    def plot_labels_txt(self, label_dict: dict, filename: str):
        write_Cell_labels_txt_file(label_dict, filename)
    
    @timed
    def plot_salient_edges_ply(self, filename: str, thresh_high: float, thresh_low: float = None, only_strong: bool = False):
        """! @brief Writes a ply file that contains colored points to be viewed on top of the original mesh.
        Visualizes the (double) threshold salient edges. Points belonging to a strong edge are colored red, points
        from weak edges are colored blue.
        
        @param filename The name of the output file. "_()Tlow_()Thigh_OverlaySalientEdge" will be added to the filename.
        @param thresh_high The high threshold for salient edges (or single threshold)
        @param thresh_low (Optional) The low threshold for salient edges. Not necessary if single threshold is wished. 
        @param only_strong (Optional) Whether to exclude weak edges that are not connected to a strong edge.
        """
        if thresh_low == None:
            thresh_low = thresh_high
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.reduce_morse_complex(self.range)
            
        if only_strong:
            edge_pts = self.get_salient_ridges(thresh_high, thresh_low)
            write_overlay_points(edge_pts, self.Vertices,filename)
        else:
            write_SalientEdge_overlay_ply_file(self.maximalReducedComplex, 
                                                self.Vertices, self.Edges, self.Faces,
                                                thresh_high, thresh_low, 
                                                filename, color_high=[255,0,0], color_low=[0,0,255])
    
    @timed
    def plot_persistence_diagram(self, persistence: float = 0, pointsize: int = 4, 
                                save: bool = False, filepath: str = 'persistence_diagram'):
        """! @brief Plots the persistence diagram for the Morse Complex of the given persistence.
        
        @param persistence (Optional) The persistence of the Morse Complex we want to get the persistence diagram from.
        Default is 0.
        @apram pointsize (Optional) The pointsize in the diagram. Default is 4. 
        @param save (Optional) Bool. Whether to save the diagram or not. Default is False.
        @param filepath (Optional) The filename under which the diagram should be stored. Default is 'persistence_diagram'.
        """
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce to this persistence first...")
            self.reduce_morse_complex(persistence)
            print("Need to calculate Betti Numbers...")
            self.calculate_betti_numbers(persistence)
            
        persistence_diagram(self.reducedMorseComplexes[persistence], self.reducedMorseComplexes[persistence].partner, 
                           self.max, self.min, pointsize = pointsize, save = save, filepath = filepath)
    
    @timed
    def salient_edge_statistics(self, nb_bins: int = 15, log: bool = False, save: bool = False, 
                                filepath: str = 'histogram', show: bool = True):
        """! @brief Creates statistics of the separatrix persistences of the cancelled separatrices in the maximally
        reduced Morse Complex and allows to optionally plot and save a histogram as well.

        @param nb_bins (Optional) Integer. The number of bins for the histogram. Default is 15.
        @param log (Optional) Bool. Use logarithmic scale for the counts /y-axis in the 
        histogram. Default is False.
        @param save (Optional) Bool. Whether to save the histogram as a file. Default is False.
        @param filepath (Optional) The filepath to use if the histogram should be saved. Default is 'histogram'.
        @param show (Optional) Bool. Whether to plot the histogram or not. Default is True.

        @return stats A dictionary containing the keys 'mean', 'std' and 'persistences' containing the mean, 
        the standard deviation and a list of the separatrix persistences.
        """
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.reduce_morse_complex(self.range)
        stats = salient_edge_statistics(self.maximalReducedComplex, nb_bins=nb_bins, 
                                        log=log, save=save, filepath=filepath, show=show)
        return stats
    
    @timed
    def funval_statistics(self, nb_bins: int = 15, log: bool = False, save: bool = False, 
                          filepath: str = 'histogram', show: bool = True):
        """! @brief Creates statistics of function values on all vertices and allows to optionally plot 
        and save a histogram as well.

        @param nb_bins (Optional) Integer. The number of bins for the histogram. Default is 15.
        @param log (Optional) Bool. Use logarithmic scale for the counts /y-axis in the 
        histogram. Default is False.
        @param save (Optional) Bool. Whether to save the histogram as a file. Default is False.
        @param filepath (Optional) The filepath to use if the histogram should be saved. Default is 'histogram'.
        @param show (Optional) Bool. Whether to plot the histogram or not. Default is True.

        @return stat A dictionary containing the keys 'mean', 'std' and 'fun_vals' containing the mean, 
        the standard deviation and a list of the function values.
        """
        stats = fun_val_statistics(self.Vertices, nb_bins=nb_bins, log=log, 
                                   save=save, filepath=filepath, show=show)
        return stats
    
    @timed
    def critical_funval_statistics(self, persistence: float, nb_bins: int = 15, log: bool = False, 
                                   save: bool = False, filepath: str = 'histogram', show: bool = True):
        """! @brief Creates statistics of function values on all critical vertices, edges and faces of the 
        Morse Complex at a given persitence separately and allows to optionally plot and save the histograms as well.

        @details The histograms will be plotted adding 'critV', 'critE' and 'critF' to the filepath.

        @param persistence The persistence of the Morse Complex we want to have the function value 
        statistics of (will use CritV, CritE and CritF).
        @param nb_bins (Optional) Integer. The number of bins for the histogram. Default is 15.
        @param log (Optional) Bool. Use logarithmic scale for the counts /y-axis in the 
        histogram. Default is False.
        @param save (Optional) Bool. Whether to save the histogram as a file. Default is False.
        @param filepath (Optional) The filepath to use if the histogram should be saved. Default is 'histogram'.
        @param show (Optional) Bool. Whether to plot the histogram or not. Default is True.

        @return stat A dictionary containing the keys 'V', 'E' and 'F' each containing dictionaries with keys 'mean', 
        'std' and 'fun_vals' containing the mean, the standard deviation and a list of the function values for the critical 
        vertices, edges or faces respectively.
        """
        stats = critical_fun_val_statistics(self.reducedMorseComplexes[persistence], nb_bins=nb_bins, 
                                            log=log, save=save, filepath=filepath, show=show)
        return stats
    
    