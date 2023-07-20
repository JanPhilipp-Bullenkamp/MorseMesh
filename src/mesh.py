"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp

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

##
# @file mesh.py
#
# @brief Stores the Mesh dataclass.
#
# @section normal_mesh_structures Normal Mesh Structures
# - filename
# - min
# - max
# - range
# - Vertices
# - Edges
# - Faces
#
# @section morse_theoretic_structures Morse-Theoretic Structures
# - _flag_process_lower_stars
# - _flag_MorseComplex
# - _flag_SalientEdge
# - _flag_BettiNumbers
# - partners
# - BettiNumbers
# - V12
# - V23
# - C
# - MorseComplex
# - reducedMorseComplexes
# - maximalReducedComplex


from src.Algorithms.load_data.read_ply import read_ply

from src.Algorithms.load_data.read_ply_test import load_ply

from src.Evaluation.read_labels_txt import read_labels_txt

from src.Algorithms.load_data.anisotropic_diffusion import smooth_function_values
from src.Algorithms.load_data.read_or_process_funvals import (read_funvals, 
                                                              apply_perona_malik_diffusion)

from src.timer import timed
from collections import Counter

import os
import numpy as np

class Box:
    def __init__(self, 
                 min_x: float, 
                 min_y: float, 
                 min_z: float, 
                 max_x: float, 
                 max_y: float, 
                 max_z: float):
        self.min_x = min_x
        self.min_y = min_y
        self.min_z = min_z
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z


class Mesh:
    """! @brief Mesh class used to store mesh, Morse Theory 
    and Segmentation related structures.
    """
    ## @var filename
    # The filename of the underlying mesh.
    ## @var min
    # The minimal function value.
    ## @var max
    # The maximal function value
    ## @var range
    # The range of function values. (max-min)
    ## @var Vertices
    # A dictionary to store the vertices. Stored as key-value with key: vertex 
    # index and value: Vertex class object
    ## @var Edges
    # A dictionary to store the edges. Stored as key-value with key: edge index 
    # and value: Simplex class object
    ## @var Faces
    # A dictionary to store the faces. Stored as key-value with key: face index 
    # and value: Simplex class object
    
    ## @var _flag_process_lower_stars
    # Boolean whether the discrete vector field V has been calculated.
    ## @var _flag_MorseComplex
    # Boolean whether the initial Morse complex has been calculated.
    ## @var _flag_SalientEdge
    # Boolean whether a maximally reduced Morse complex has been calculated 
    # for salient edge extraction.
    ## @var _flag_BettiNumbers
    # Boolean whether the Betti numbers have been calculated.
    ## @var partners
    # Filled from Betti number calculation; needed for persistence diagram plotting.
    ## @var BettiNumbers
    # The Betti numbers stored as an array.
    ## @var V12
    # Discrete vectors/ pairings dictionary between vertices and edges.
    ## @var V23
    # Discrete vectors/ pairings dictionary between edges and faces.
    ## @var C
    # Dictionary with critical simplices: has keys 0,1 and 2. Each of these 
    # contains a set with critical simplices of the respective dimension
    ## @var MorseComplex
    # The initial Morse complex.
    ## @var reducedMorseComplexes
    # A dictionary of reduced Morse complexes. The keys are the persistences of 
    # the respective reduced Morse complex in value.
    ## @var maximalReducedComplex
    # The maximally reduced Morse complex
    def __init__(self):
        self.reset()
    
    def reset(self):
        """! @brief Constructor for the Mesh class. """
        self.reset_morse()

        self.filename = None
        
        self.min = None
        self.max = None
        self.range = None

        self.Vertices = {}
        self.Edges = {}
        self.Faces = {}

        self.InitialLabels = {}
        self.UserLabels = {}
        

    def reset_morse(self):
        """! @brief Resets all the Morse related things. """
        self.min_separatrix_persistence = None
        self.max_separatrix_persistence = None

        self._flag_process_lower_stars = False
        self._flag_MorseComplex = False
        self._flag_SalientEdge = False
        self._flag_BettiNumbers = False
        
        self.BettiNumbers = None

        self.V12 = {}
        self.V23 = {}

        self.C = {0: set(), 1: set(), 2: set()}
        
        self.MorseComplex = None
        
        self.reducedMorseComplexes = {}

        self.salient_reduced_morse_complexes = {}
        
        self.maximalReducedComplex = None

    @timed()
    def get_center(self):
        """! @brief Calculates the center of mass of the Vertices stored.
        with poke needleer of mass.
        """
        sum_x, sum_y, sum_z = 0, 0, 0
        for v in self.Vertices.values():
            sum_x += v.x
            sum_y += v.y
            sum_z += v.z
        center = [sum_x, sum_y, sum_z] / len(self.Vertices)
        return center

    def get_bounding_box(self):
        vertices = [np.array((v.x,v.y,v.z)) for v in self.Vertices.values()]
        min_x, min_y, min_z = np.min(vertices, axis=0)
        max_x, max_y, max_z = np.max(vertices, axis=0)
        return Box(min_x, min_y, min_z, max_x, max_y, max_z)

    ''' DATALOADING'''
    @timed(False)
    def load_mesh_new(self, 
                      filename: str, 
                      morse_function: str = "quality", 
                      inverted: bool = False):
        self.reset()

        file_obj = open(filename, 'rb')
        min_val, max_val = load_ply(file_obj, 
                                    self.Vertices, 
                                    self.Edges, 
                                    self.Faces, 
                                    morse_function=morse_function, 
                                    inverted=inverted)
        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
    
    @timed()
    def load_mesh_ply(self, filename: str, quality_index: int, inverted: bool = False):
        """! @brief Loads a .ply file with a Morse function taken from the given index.

        @param filename The location and filename of the ply file that should be loaded.
        @param quality_index The index position where the Morse function should 
               be taken from in the vertices.
        @param inverted (Optional) Boolean, whether the Morse function should be 
               inverted or not (multiplied with -1).
        """
        # Reset previously loaded data if necessary
        self.reset()
        min_val, max_val = read_ply(filename, quality_index, self.Vertices, 
                                    self.Edges, self.Faces, inverted=inverted)
        self.filename = os.path.splitext(filename)[0]
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val

    def load_labels(self, filename):
        info = read_labels_txt(filename)

        c = Counter(info.values())
        critLabels = c.most_common()[:0:-1]
    
        vertexLabels = info
        edgeLabels = {}
        faceLabels = {}

        for key in self.Edges.keys():
            edgeLabels[key] = set()
            for i in self.Edges[key].indices:
                edgeLabels[key].add(vertexLabels[i])

        for key in self.Faces.keys():
            faceLabels[key] = set()
            for i in self.Faces[key].indices:
                faceLabels[key].add(vertexLabels[i])

        self.UserLabels = {'vertices': vertexLabels, 'edges': edgeLabels, 'faces': faceLabels, 'crit': set(a for (a, b) in critLabels)}
        
    @timed() 
    def load_new_funvals(self, filename: str, operation: str = "max"):
        """! @brief Loads new function values into the Mesh. Currently expects a 
        feature vector file from Gigamesh i think.
        @param filename The location and filename of the feature vector file that 
               should give new Morse function values.
        @param operation Optionally change the function on the feature vector: 
               currently options are max, min, maxabs and minabs. Default is max.
        """
        min_val, max_val = read_funvals(filename, 
                                        self.Vertices, 
                                        self.Edges, 
                                        self.Faces, 
                                        operation=operation)
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        self.reset_morse()

    @timed()
    def get_area(self):
        area = sum([face.compute_area(self.Vertices) for face in self.Faces.values()])
        return area

    @timed()
    def smooth_fun_vals(self, n_neighboorhood: int = 1):
        smooth_function_values(self.Vertices, n_neighboorhood)

    @timed()
    def apply_perona_malik(self, iterations: int, lamb: float, k: float):
        min_val, max_val = apply_perona_malik_diffusion(self.Vertices, 
                                                        self.Edges, 
                                                        self.Faces, 
                                                        iterations, 
                                                        lamb, 
                                                        k)
        self.min = min_val
        self.max = max_val
        self.range = max_val - min_val
        self.reset_morse()

    def __repr__(self):
        """! @brief Prints out Mesh information.
        @return A string that gives information on the loaded mesh.
        """
        return ("+-------------------------------------------------------\n"
        "| Mesh Info\n"
        "+-------------------------------------------------------\n"
        "| Filename: " + self.filename + "\n"
        "| Morse function values range: " + str([self.min,self.max]) + "\n"
        "+-------------------------------------------------------\n"
        "| Number of Vertices: " + str(len(self.Vertices)) + "\n"
        "| Number of Edges: " + str(len(self.Edges)) + "\n"
        "| Number of Faces: " + str(len(self.Faces)) + "\n"
        "+-------------------------------------------------------\n"
        "| Euler characteristic: " + str(len(self.Vertices) 
                                         + len(self.Faces) -len(self.Edges)) + "\n"
        "| Betti numbers: " + str(self.BettiNumbers) + "\n" 
        "+-------------------------------------------------------")
        