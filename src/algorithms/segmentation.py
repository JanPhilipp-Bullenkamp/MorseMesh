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

# imports
from copy import deepcopy
import numpy as np

from .datastructures import MorseComplex, MorseCells, Cell
from .weight_metrics import compute_weight_saledge
from .cancellation_queue import CancellationQueue
from ..evaluation_and_labels.labels_read_write import Labels


def create_segmentation(morse_complex: MorseComplex, 
                        salient_edge_points: set, 
                        thresh_large: float, 
                        thresh_small: float, 
                        merge_threshold: float, 
                        minimum_labels: int = 3, 
                        size_threshold: int = 500,
                        conforming=False, 
                        UserLabels=None,
                        plotting=False):
    """! @brief Creates a segmentation from this MorseComplex with 
    the given double edge threshold and the merging threshold.
    
    @details Creates a copy of the Morse cells at this persistence 
    level and than segments based on the given parameters. Segemntation 
    stops when either no more cells can be merged due to no more adjacent 
    cells having a weight below the merge threshold, or reaching the 
    optional minimum number of labels (which is defaulted to 3).
    
    @param salient_edge_points The salient edge points that have been 
            calcualted from the double threshold
    @param thresh_large The larger threshold of the double threshold 
            that was used to get the edge points.
    @param thresh_small The smaller threshold of the double threshold 
            that was used to get the edge points.
    @param merge_threshold The threshold that determines when to stop 
            merging cells. Weights in the neighborhood graph of the 
            Morse cells will be above this threshold.
    @param minimum_labels The minimum number of labels we want to keep. 
            Default is set to 3
    """
    if morse_complex._flag_MorseCells == False:
        raise AssertionError("No Morse Cells calculated yet...")
    SegmentationCells = deepcopy(morse_complex.MorseCells)
    
    SegmentationCells.add_salient_edge_points(salient_edge_points, 
                                                (thresh_large, thresh_small))
    
    segment(SegmentationCells,
            merge_threshold, 
            minimum_labels=minimum_labels, 
            size_threshold=size_threshold, 
            conforming=conforming, 
            UserLabels=UserLabels,
            plotting=plotting)
    
    if (thresh_large, thresh_small) not in morse_complex.Segmentations.keys():
        morse_complex.Segmentations[(thresh_large, thresh_small)] = {}
    if merge_threshold in morse_complex.Segmentations[(thresh_large, thresh_small)].keys():
        raise AssertionError("This parameter combination "
                                "has already been calculated...")
    else:
        morse_complex.Segmentations[(thresh_large, thresh_small)][merge_threshold] = SegmentationCells

    

def segment(morse_cells: MorseCells, 
            merge_threshold: float, 
            minimum_labels: int, 
            size_threshold: int = 500, 
            conforming = False, 
            UserLabels=None,
            plotting=False):
    """! @brief Makes this MorseCells object a Segmentation, based 
    on the salient edge points stored in this MorseCells object 
    and a given merge_threshold and minim_labels number.
    
    @details Requires this MorseCells object to contain salient edge 
    points. Based on those, the weights between neighboring cells 
    are calculated and then cells are merged using a Priority Queue 
    to make sure to merge cells first if they have a low weight. 
    Merging stops if either no more cell adjacencies have a weight 
    below the threshold or the minimum number of labels is 
    reached. This MorseCell object then becomes the segmentation.
    
    @param merge_threshold The threshold for weights between 
            adjacent cells to stop merging.
    @param minimum_labels A minimum number of labels that will 
            stop the merging process if it is reached. (Otherwise 
            the merge threshold is the stopping criterium)
    """
    if morse_cells.salient_edge_points == None or morse_cells.threshold == None:
        raise AssertionError("Cannot segment if no salient edge "
                                "points are loaded to these Morse cells!")
    if morse_cells.merge_threshold != None:
        raise AssertionError("Already has a merge threshold assigned... "
                                "Shouldnt be so, probably messed up the "
                                "order of functions somewhere.")
        
    # 1. calculate weights between cells
    morse_cells.calculate_all_weights(conforming=conforming, UserLabels=UserLabels)

    still_changing = True
    # pop from queue until no more elements are below the merge threshold 
    # or we reach the minimum number of labels
    step_counter = 0
    while len(morse_cells.Cells) > minimum_labels and still_changing:
        # 2. create and fill Cancellation Queue
        queue = CancellationQueue()
        before = len(morse_cells.Cells)
        for label, cell in morse_cells.Cells.items():
            for neighbor, weight in cell.neighbors_weights.items():
                if weight < merge_threshold:
                    queue.insert(tuple((weight,label, neighbor)))

        while queue.length() != 0:
            weight, label1, label2 = queue.pop_front()
            
            # need to make sure the popped tuple is still available 
            # for merging and their weight is also the same.
            if label1 in morse_cells.Cells.keys() and label2 in morse_cells.Cells.keys():
                if label2 in morse_cells.Cells[label1].neighbors.keys():
                    if weight == morse_cells.Cells[label1].neighbors_weights[label2]:
                        # can merge cells
                        updated_weights = morse_cells.merge_cells(label1, label2, conforming=conforming, UserLabels=UserLabels)
                        if plotting:
                            if step_counter % 50 == 0:
                                plot_steps(morse_cells.Cells, step_counter)
                        step_counter+=1 # add 1 after check to include step 0
        after = len(morse_cells.Cells)
        if before == after:
            still_changing = False

    if plotting:
        plot_steps(morse_cells.Cells, step_counter)
        step_counter+=1 # add 1  
    # remove small patches
    morse_cells.remove_small_patches(size_threshold=size_threshold)    
    if plotting:
        plot_steps(morse_cells.Cells, step_counter)
        step_counter+=1 # add 1
    # remove small enclosures
    morse_cells.remove_small_enclosures(size_threshold=size_threshold)   
    if plotting:
        plot_steps(morse_cells.Cells, step_counter)
        
def plot_steps(cells, counter):
    labels = Labels()
    labels.load_from_dict(cells)
    labels.write_labels_txt("./test_plot/step_"+str(counter))
