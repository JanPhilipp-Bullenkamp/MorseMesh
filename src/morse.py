"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp, Theresa Häberle

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""! @brief Morse Theory Framework."""
##
# @mainpage Morse Theory Framework
#
# @section description_main Description
# A framework for using discrete Morse Theory on 3D triangluar meshes. 
# Can be used for segmentation when loading in a suitable scalar function 
# (e.g. curvature values on each vertex).
#
# @section contains_main Contains
# A morse class that can load a 3D mesh (ply files only at the moment) 
# and perform various Morse Theory computations, as well as a segmentation 
# method and various plotting functions.
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
from src.Algorithms.process_lower_stars import process_lower_stars
from src.Algorithms.conforming_gradient import conforming_gradient
from src.Algorithms.extract_morse_complex import extract_morse_complex
from src.Algorithms.reduce_morse_complex import cancel_critical_pairs
from src.Algorithms.reduce_morse_complex import cancel_critical_conforming_pairs

from src.Algorithms.morse_cells import get_morse_cells
from src.Algorithms.edge_detection import ridge_detection, valley_detection

from src.Algorithms.cluster import cluster_mesh, merge_cluster
from src.plot_data.labels_read_write import Labels 

from src.mesh import Mesh

from src.timer import timed

# import libraries
import timeit
import itertools

class Morse(Mesh):
    def __init__(self):
        super().__init__()

    @timed()
    def seed_cluster_mesh(self, bd_pts: set, num_seeds: int) -> dict:
        return cluster_mesh(self.Vertices, bd_pts, num_seeds)

    @timed()
    def cluster_segmentation(self, cluster: dict, bd_points: set, threshold: float):
        return merge_cluster(cluster, bd_points, threshold)
        
    ''' MORSE THEORY'''
    
    @timed(False)
    def process_lower_stars(self, conforming=False):
        """! @brief Runs the process_lower_stars algorithm to get a discrete 
        vector field representing the gradient of the discrete Morse function.

        @details Implementation of the algorithm described in Robins et al......
        """
        # reset if has been computed already
        if self._flag_process_lower_stars:
            self.reset_morse()
            
        if conforming:
            conforming_gradient(self.Vertices, 
                                self.Edges, 
                                self.Faces, 
                                self.UserLabels,
                                self.C, 
                                self.V12, 
                                self.V23)
        else:
            process_lower_stars(self.Vertices, 
                                self.Edges, 
                                self.Faces, 
                                self.C, 
                                self.V12, 
                                self.V23)
        self._flag_process_lower_stars = True
        
    @timed(False)
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

            self.MorseComplex = extract_morse_complex(self.Vertices, 
                                                      self.Edges, 
                                                      self.Faces, 
                                                      self.V12, 
                                                      self.V23, 
                                                      self.C)
            self.reducedMorseComplexes[0] = self.MorseComplex
            self.MorseComplex.filename = self.filename
            self._flag_MorseComplex = True
        
    @timed(False)
    def reduce_morse_complex(self, persistence: float, conforming = False):
        """! @brief Reduces the Morse complex up to the given persistence.
        @details Always cancels two critical simplices of consectutive dimensions 
        if their function values are closer than the given persistence. The 
        resulting simplified Morse Complex is stored as a copy under 
        reducedMorseComplexes[persistence].
        
        @param persistence The persistence up to which the Morse complex 
               should be simplified.
        
        @return The reduced Morse Complex object.
        """
        if not self._flag_MorseComplex:
            print("Need to call extract_morse_complex first...")
            self.extract_morse_complex()
        if persistence in self.reducedMorseComplexes.keys():
            print("This persistence has already been calculated!")
            print("You can access it via .reducedMorseComplexes[persistence] ") 
        else:
            if conforming:
                self.reducedMorseComplexes[persistence] = cancel_critical_conforming_pairs(self.MorseComplex, persistence, 
                                                                              self.Vertices, self.Edges, self.Faces, self.UserLabels)
            else:
                self.reducedMorseComplexes[persistence] = cancel_critical_pairs(self.MorseComplex, 
                                                                            persistence, 
                                                                            self.Vertices, 
                                                                            self.Edges, 
                                                                            self.Faces)
            if persistence >= self.range and not self._flag_SalientEdge:
                self.maximalReducedComplex = self.reducedMorseComplexes[persistence]
                self.maximalReducedComplex.maximalReduced = True
                self._flag_SalientEdge = True
                separatrix_persistences = [pers for pers,_ in 
                                           self.maximalReducedComplex.Separatrices]
                self.min_separatrix_persistence = min(separatrix_persistences)
                self.max_separatrix_persistence = max(separatrix_persistences)
                self.maximalReducedComplex.min_separatrix_persistence = min(separatrix_persistences)
                self.maximalReducedComplex.max_separatrix_persistence = max(separatrix_persistences)
                print("Persistence was high enough that this complex is maximally reduced.")
        return self.reducedMorseComplexes[persistence]

    @timed(False)
    def reduce_morse_complex_salient_edge(self, 
                                          thresh_high: float, 
                                          thresh_low: float = None, 
                                          salient_edge_pts: set = None, 
                                          pers: float = None):
        if not self._flag_MorseComplex:
            print("Need to call extract_morse_complex first...")
            self.extract_morse_complex() 
        if not self._flag_SalientEdge:
            print("Need to reduce maximally first...")
            self.reduce_morse_complex(self.range)
        if salient_edge_pts == None:
            salient_edge_pts = self.get_salient_ridges(thresh_high, thresh_low)

        if pers == None:
            self.salient_reduced_morse_complexes[(thresh_high, thresh_low)] = cancel_critical_pairs(self.MorseComplex, 
                                                                                                    self.range, 
                                                                                                    self.Vertices, 
                                                                                                    self.Edges, 
                                                                                                    self.Faces, 
                                                                                                    salient_edge_pts=salient_edge_pts)
            return self.salient_reduced_morse_complexes[(thresh_high, thresh_low)]
        else:
            self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)] = cancel_critical_pairs(self.MorseComplex, 
                                                                                                          pers,
                                                                                                          self.Vertices, 
                                                                                                          self.Edges,
                                                                                                          self.Faces, 
                                                                                                          salient_edge_pts)
            return self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)]

    @timed(False)
    def extract_cells_salient_complex(self, 
                                      thresh_high: float,
                                      thresh_low: float = None, 
                                      pers: float = None):
        """! @brief Extracts the Morse Cells of the salient reduced Morse complex.
        
        @details The extract_cells_salient_complex method extracts cells from 
        a salient reduced Morse complex. It takes in two parameters: 
        thresh_high and thresh_low. If a Morse complex with the given thresholds 
        has not been reduced yet, it will be reduced using the 
        reduce_morse_complex_salient_edge method. The method then calls the 
        get_morse_cells function on the reduced Morse complex, and returns 
        the resulting MorseCells object.

        @param thresh_high The higher threshold for the salient edges.
        @param thresh_low (Optional) The lower threshold for the salient edges.

        @return Morse Cells object containing the cells of the salient 
                reduced Morse Complex.
        """
        if pers == None:
            if (thresh_high, thresh_low) not in self.salient_reduced_morse_complexes.keys():
                print("Need to reduce with these edge thresholds first...")
                self.reduce_morse_complex_salient_edge(thresh_high, thresh_low)
            get_morse_cells(self.salient_reduced_morse_complexes[(thresh_high,thresh_low)], 
                            self.Vertices, 
                            self.Edges, 
                            self.Faces)
            return self.salient_reduced_morse_complexes[(thresh_high,thresh_low)].MorseCells
        else:
            if (pers, thresh_high, thresh_low) not in self.salient_reduced_morse_complexes.keys():
                print("Need to reduce with these edge thresholds and persistence first...")
                self.reduce_morse_complex_salient_edge(thresh_high, thresh_low, pers=pers)
            get_morse_cells(self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)], 
                            self.Vertices, 
                            self.Edges, 
                            self.Faces)
            return self.salient_reduced_morse_complexes[(pers, thresh_high, thresh_low)].MorseCells
    
    @timed(False)
    def extract_morse_cells(self, persistence: float):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce Morse complex to this persistence first...")
            self.reduce_morse_complex(persistence)
        if not self.reducedMorseComplexes[persistence]._flag_MorseCells:
            get_morse_cells(self.reducedMorseComplexes[persistence], 
                            self.Vertices, 
                            self.Edges, 
                            self.Faces)
            return self.reducedMorseComplexes[persistence].MorseCells
        else:
            print("MorseCells for the MorseComplex with this "
                  "persistence have already been calculated!")
    
    ''' SEGMENTATION'''
    
    @timed(False)
    def segmentation(self, 
                     persistence: float, 
                     thresh_large: float, 
                     thresh_small: float, 
                     merge_threshold: float, 
                     minimum_labels: int = 3, 
                     size_threshold: int = 500,
                     separatrix_type: str = "all",
                     conforming = False,
                     plotting=False):
        if persistence not in self.reducedMorseComplexes.keys():
            print("Need to reduce Morse complex to this persistence first...")
            self.reduce_morse_complex(persistence, conforming=conforming)
        if self.reducedMorseComplexes[persistence]._flag_MorseCells == False:
            print("No Morse Cells computed for this persistence, computing now...")
            self.extract_morse_cells(persistence)
        if not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges...")
            self.reduce_morse_complex(self.range, conforming=conforming)
            
        salient_edge_points = self.get_salient_ridges(thresh_large, 
                                                      thresh_small, 
                                                      separatrix_type=separatrix_type)
        
        self.reducedMorseComplexes[persistence].create_segmentation(salient_edge_points, 
                                                                    thresh_large, 
                                                                    thresh_small, 
                                                                    merge_threshold, 
                                                                    minimum_labels=minimum_labels, 
                                                                    size_threshold=size_threshold,
                                                                    conforming=conforming, 
                                                                    UserLabels=self.UserLabels,
                                                                    plotting=plotting)
        
        return self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, thresh_small)][merge_threshold]

    @timed(False)
    def segmentation_salient_reduction(self, 
                                       thresh_large: float, 
                                       thresh_small: float, 
                                       merge_threshold: float, 
                                       persistence: float = None, 
                                       minimum_labels: int = 3):
        salient_edge_points = self.get_salient_ridges(thresh_large, thresh_small)

        if persistence == None:
            self.reduce_morse_complex_salient_edge(thresh_large, 
                                                   thresh_small, 
                                                   salient_edge_points)
            self.extract_cells_salient_complex(thresh_large, thresh_small)
            self.salient_reduced_morse_complexes[(thresh_large,
                                                  thresh_small)].create_segmentation(salient_edge_points, 
                                                                                     thresh_large, 
                                                                                     thresh_small,
                                                                                     merge_threshold, 
                                                                                     minimum_labels)
            return self.salient_reduced_morse_complexes[(thresh_large,
                                                         thresh_small)].Segmentations[(thresh_large, 
                                                                                       thresh_small)][merge_threshold]
        else:
            self.reduce_morse_complex_salient_edge(thresh_large, 
                                                   thresh_small, 
                                                   salient_edge_points, 
                                                   pers=persistence)
            self.extract_cells_salient_complex(thresh_large, 
                                               thresh_small, 
                                               persistence)
            self.salient_reduced_morse_complexes[(persistence,
                                                  thresh_large,
                                                  thresh_small)].create_segmentation(salient_edge_points, 
                                                                                     thresh_large, 
                                                                                     thresh_small,
                                                                                     merge_threshold, 
                                                                                     minimum_labels)
            return self.salient_reduced_morse_complexes[(persistence,
                                                         thresh_large,
                                                         thresh_small)].Segmentations[(thresh_large, 
                                                                                       thresh_small)][merge_threshold]
    
    @timed(False)
    def segmentation_no_pers(self, 
                             thresh_large: float, 
                             thresh_small: float, 
                             merge_threshold: float, 
                             minimum_labels: int = 3):
        if self.MorseComplex._flag_MorseCells == False:
            print("No Morse Cells computed for initial complex, computing now...")
            self.extract_morse_cells(0)
        if not self._flag_SalientEdge:
            print("Need maximally reduced complex for salient edges...")
            self.reduce_morse_complex(self.range)
            
        salient_edge_points = self.get_salient_ridges(thresh_large, thresh_small)
        
        self.MorseComplex.create_segmentation(salient_edge_points, 
                                              thresh_large, 
                                              thresh_small, 
                                              merge_threshold, 
                                              minimum_labels=minimum_labels)
        
        return self.MorseComplex.Segmentations[(thresh_large, 
                                                thresh_small)][merge_threshold]
    
    @timed(False)
    def get_salient_ridges(self, 
                           thresh_high: float, 
                           thresh_low: float = None, 
                           min_length: int = 1, 
                           max_length: int = None,
                           separatrix_type: str = "all"):
        # if only one threshold given: use same strong and weak edge threshold
        if thresh_low == None:
            thresh_low = thresh_high
        # if no maximally reduced MorseComplex has been calculated: do that now
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.reduce_morse_complex(self.range)
        ridges = ridge_detection(self.maximalReducedComplex, 
                                 thresh_high, 
                                 thresh_low, 
                                 self.Vertices, 
                                 self.Edges, 
                                 self.Faces, 
                                 min_length=min_length, 
                                 max_length=max_length,
                                 separatrix_type=separatrix_type)
        return ridges

    @timed(False)
    def get_salient_valleys(self, 
                            thresh_high: float, 
                            thresh_low: float = None, 
                            min_length: int = 1, 
                            max_length: int = None,
                            separatrix_type: str = "all"):
        # if only one threshold given: use same strong and weak edge threshold
        if thresh_low == None:
            thresh_low = thresh_high
        # if no maximally reduced MorseComplex has been calculated: do that now
        if not self._flag_SalientEdge:
            print("Need to maximally reduce MorseComplex first...")
            self.reduce_morse_complex(self.range)
        valleys = valley_detection(self.maximalReducedComplex, 
                                   thresh_high, 
                                   thresh_low, 
                                   self.Vertices, 
                                   self.Edges, 
                                   self.Faces, 
                                   min_length=min_length, 
                                   max_length=max_length,
                                   separatrix_type=separatrix_type)
        return valleys

    @timed(False)
    def clean_lines(self, line_points: set):
        print("Pts before cleaning",len(line_points))
        cleaned_lines = set()
        for pt in line_points:
            #print(len(self.Vertices[pt].neighbors.intersection(line_points)))
            if len(self.Vertices[pt].neighbors.intersection(line_points)) > 1:
                cleaned_lines.add(pt)
        print("Pts after cleaning",len(cleaned_lines))
        return cleaned_lines
                
    @timed(False)
    def get_connected_components_lines(self, line_points: set):
        components = {}
        index = 1
        while len(line_points) != 0:
            start = line_points.pop()
            connected = set()
            component_length = 0
            queue = [start]
            while len(queue) != 0:
                p = queue.pop()
                connected.add(p)
                for elt in self.Vertices[p].neighbors.intersection(line_points):
                    queue.append(elt)
                    line_points.remove(elt)
                    component_length += self.Vertices[p].distance_to_vertex(self.Vertices[elt])
            components[index] = connected, component_length
            index += 1

        print("Number of lines: ",len(components))
        for nb, comp in components.items():
            pts, leng = comp
            print("Index: ", nb)
            print("Length: ",leng)
            print("nb points: ", len(pts))
        return components

    @timed(False)
    def change_separatrix_persistences_start_end_average(self):
        if not self._flag_SalientEdge:
            self.reduce_morse_complex(self.range)
        self.maximalReducedComplex.change_separatrix_persistences(self.Vertices, 
                                                                  self.Edges, 
                                                                  self.Faces)

    @timed(False)
    def pipeline_salient_segmentation(self, 
                                      infilename: str, 
                                      outfilename: str, 
                                      quality_index: int, 
                                      inverted: bool, 
                                      high_thresh: float, 
                                      low_thresh: float, 
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
            f.write("\tSegmentation (high,low,merge): time\n")
            for high, low, merge in list(itertools.product(high_thresh, 
                                                           low_thresh, 
                                                           merge_thresh)):
                if high > low:
                    t9 = timeit.default_timer()
                    self.segmentation_salient_reduction(high, 
                                                       low, 
                                                       merge, 
                                                       minimum_labels=5)
                    t10 = timeit.default_timer()
                    f.write("\t"+str(high)+" "+str(low)+" "+str(merge)+": "+str(t10-t9)+"\n")
                    self.plot_segmentation_salient_edge_label_txt(high, 
                                                                  low, 
                                                                  merge, 
                                                                  outfilename+str(high)+"H_"+str(low)+"L_"+str(merge)+"M")
    
    @timed(False)
    def pipeline(self, 
                 infilename: str, 
                 outfilename: str, 
                 inverted: bool, 
                 persistence: float, 
                 high_thresh: float, 
                 low_thresh: float, 
                 merge_thresh: float):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_new(infilename, morse_function="quality", inverted=inverted)
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
                for high, low, merge in list(itertools.product(high_thresh, 
                                                               low_thresh, 
                                                               merge_thresh)):
                    if high > low:
                        t9 = timeit.default_timer()
                        self.segmentation(pers, 
                                          high, 
                                          low, 
                                          merge, 
                                          minimum_labels=5)
                        t10 = timeit.default_timer()
                        f.write("\t"+str(high)+" "+str(low)+" "+str(merge)+": "+str(t10-t9)+"\n")
                        self.plot_segmentation_label_txt(pers, 
                                                         high, 
                                                         low, 
                                                         merge, 
                                                         outfilename)

    @timed(False)
    def pipeline_cluster_segmentation(self, 
                                      infilename: str, 
                                      outfilename: str, 
                                      inverted: bool,
                                      high_threshs: list[float], 
                                      low_threshs: list[float], 
                                      merge_thresholds: list[float],
                                      separatrix_type: str = "all"):
        
        with open(outfilename+"_timings.txt", "w") as f:
            t1 = timeit.default_timer()
            self.load_mesh_new(infilename, morse_function="quality", inverted=inverted)
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
            for high, low in list(itertools.product(high_threshs, low_threshs)):
                t6 = timeit.default_timer()
                bd_points = self.get_salient_ridges(high, low, separatrix_type=separatrix_type)
                cluster = self.seed_cluster_mesh(bd_points, 350)
                t7 = timeit.default_timer()
                f.write("Bd points and cluster: "+str(t7-t6)+"\n")

                for merge in merge_thresholds:
                    t9 = timeit.default_timer()
                    segmented_dict = self.cluster_segmentation(cluster, bd_points, merge)
                    t10 = timeit.default_timer()
                    f.write("\t"+str(high)+" "+str(low)+" "+str(merge)
                            +": "+str(t10-t9)+"\n")
                    self.plot_labels_txt(segmented_dict, 
                                         outfilename+"_"+str(high)+"H_"+str(low)+"L_"+str(merge)+"M")
    
    ''' PLOTTING'''

    @timed()
    def plot_segmentation_steps(self,
                                filename: str,
                                persistence: float, 
                                thresh_large: float, 
                                thresh_small: float, 
                                merge_threshold: float):
        self.load_mesh_new(filename, morse_function="quality", inverted=True)
        self.process_lower_stars()
        self.extract_morse_complex()
        self.reduce_morse_complex(self.range)
        self.reduce_morse_complex(persistence)
        self.extract_morse_cells(persistence)
        self.segmentation(persistence, 
                          thresh_large, 
                          thresh_small, 
                          merge_threshold, 
                          minimum_labels=5,
                          plotting=True)
    
    @timed()
    def plot_morse_cells_label_txt(self, persistence: float, filename: str):
        """! @brief Writes a txt label file (first col index, second col label) 
        that can be read in by GigaMesh as labels. Each label is a Morse Cell 
        from the Morse Complex of the given persistence.
        
        @param persistence The persistence of the Morse Complex whose 
               Cells should be plotted.
        @param filename The name of the output file.
        """
        if persistence not in self.reducedMorseComplexes.keys():
            raise ValueError("No reduced Morse Complex calculated for this persistence!")
        elif self.reducedMorseComplexes[persistence]._flag_MorseCells == False:
            raise ValueError("No Morse cells computed for the Morse "
                             "complex with this persistence!")
        else:
            labels = Labels()
            labels.load_from_cells(self.reducedMorseComplexes[persistence].MorseCells.Cells)
            labels.write_labels_txt(filename)
    
    @timed()  
    def plot_segmentation_label_txt(self, 
                                    persistence: float, 
                                    thresh_large: float, 
                                    thresh_small: float, 
                                    merge_threshold: float, 
                                    filename: str):
        """! @brief Writes a txt label file (first col index, second col label) 
        that can be read in by GigaMesh as labels. Each label is a Cell from 
        the Segmentation of the given parameter combination. 
        
        @details The parameters used are also stored in the header of the file.
        
        @param persistence The persistence used for the segmentation.
        @param thresh_large The thresh_large used for the segmentation.
        @param thresh_small The thresh_small used for the segmentation.
        @param merge_threshold The merge_threshold used for the segmentation.
        @param filename The name of the output file. The parameters will 
               be added to the filename.
        """
        if persistence not in self.reducedMorseComplexes.keys():
            raise ValueError("Segmentation for this persistence "
                             "has not been calculated!")
        if (thresh_large, thresh_small) not in self.reducedMorseComplexes[persistence].Segmentations.keys():
            raise ValueError("Segmentation for this salient edge "
                             "threshold pair has not been calculated!")
        if merge_threshold not in self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, 
                                                                                         thresh_small)].keys():
            raise ValueError("Segmentation for this merge percentage "
                             "threshold has not been calculated!")
        else:
            labels = Labels()
            labels.load_from_cells(self.reducedMorseComplexes[persistence].Segmentations[(thresh_large, 
                                                                                              thresh_small)][merge_threshold].Cells)
            labels.load_parameters(persistence, thresh_large, thresh_small, merge_threshold)
            labels.write_labels_txt(filename+ "_" + str(persistence) + "P_" + str(thresh_large) + "-" + str(thresh_small) 
                                       + "T_" + str(merge_threshold))
            
    @timed()
    def plot_segmentation_salient_edge_label_txt(self, 
                                                 thresh_large: float, 
                                                 thresh_small: float, 
                                                 merge_threshold: float, 
                                                 filename: str):
        labels = Labels()
        labels.load_from_cells(self.salient_reduced_morse_complexes[(thresh_large,thresh_small)].Segmentations[(thresh_large, thresh_small)][merge_threshold].Cells)
        labels.load_parameters(None, thresh_large, thresh_small, merge_threshold)
        labels.write_labels_txt(filename)

    @timed()
    def plot_labels_txt(self, 
                        label_dict: dict, 
                        filename: str):
        labels = Labels()
        labels.load_from_cells(label_dict)
        labels.write_labels_txt(filename)