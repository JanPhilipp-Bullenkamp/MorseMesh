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
# @file evaluation_and_conversion.py
#
# @brief Collection of evaluation functions and conversion functions for different types of results.
#
# @details Contains: \todo
#
# @section libraries_evaluation_and_conversion Libraries/Modules
# - os standard library
# - various local imports....

# imports
from .evaluation_and_labels.evaluate_metrics import compute_IoU, compute_F1_Score, get_correct_points
from .evaluation_and_labels.labels_read_write import Labels
from .evaluation_and_labels.artifact3D_conversions import artifact3D_to_labels, artifact3D_get_trafo

from .timer import timed

@timed()
def compare_result_txt_to_groundtruth_ply(result_filename, groundtruth_filename, metric = "IoU"):
    """! @brief Takes a result .txt labels file and compares to a groundtruth given as a colored .ply file.
    @param result_filename The result .txt filename and location.
    @param groundtruth_filename The colored .ply groundtruth filename and location.
    @param metric (Optional) Which metric to use for evaluation: Intersection of Union ("IoU") 
    or F1-Score ("F1). Default is "IoU".
    @param plot_correctness_mask (Optional) Boolean whether to plot a mask (labels txt file) 
    with correct points or not. Default is False. 

    @return correctness The percentage of correctly labelled vertices in the result file 
    compared to the groundtruth file.
    """    
    comp_label_class = Labels(parameters_stored=True)
    comp_label_class.load_from_txt(result_filename)
    pers, high_thr, low_thr, merge_thr = comp_label_class.get_parameters()
    comp_label = comp_label_class.labels
    
    gt_labels_class = Labels()
    gt_labels_class.load_from_ply(groundtruth_filename)
    gt_label = gt_labels_class.labels
    total_points = gt_labels_class.get_vertex_number()
    
    if metric == "IoU":
        IoU = compute_IoU(gt_label, comp_label)
        correct_points = get_correct_points(gt_label, comp_label, IoU)
    elif metric == "F1":
        F1 = compute_F1_Score(gt_label, comp_label)
        correct_points = get_correct_points(gt_label, comp_label, F1)
    else:
        raise ValueError("Currently only IoU and F1 metrics are implemented..")
        
    total_points = 0
    for pts in gt_label.values():
        total_points += len(pts)
    
    correctness = len(correct_points)/total_points*100
    
    return correctness, pers, high_thr, low_thr, merge_thr

@timed()
def compare_result_txt_to_groundtruth_txt(result_filename, groundtruth_filename, metric = "IoU"):
    """! @brief Takes a result .txt labels file and compares to a groundtruth given as a labels .txt file.
    @param result_filename The result .txt filename and location.
    @param groundtruth_filename The labels .txt groundtruth filename and location.
    @param metric (Optional) Which metric to use for evaluation: Intersection of Union ("IoU") 
    or F1-Score ("F1). Default is "IoU".
    @param plot_correctness_mask (Optional) Boolean whether to plot a mask (labels txt file) 
    with correct points or not. Default is False. 

    @return correctness The percentage of correctly labelled vertices in the result file 
    compared to the groundtruth file.
    """    
    comp_label_class = Labels(parameters_stored=True)
    comp_label_class.load_from_txt(result_filename)
    pers, high_thr, low_thr, merge_thr = comp_label_class.get_parameters()
    comp_label = comp_label_class.labels
    
    gt_labels_class = Labels()
    gt_labels_class.load_from_txt(groundtruth_filename)
    gt_label = gt_labels_class.labels
    total_points = gt_labels_class.get_vertex_number()
    
    if metric == "IoU":
        IoU = compute_IoU(gt_label, comp_label)
        correct_points = get_correct_points(gt_label, comp_label, IoU)
    elif metric == "F1":
        F1 = compute_F1_Score(gt_label, comp_label)
        correct_points = get_correct_points(gt_label, comp_label, F1)
    else:
        raise ValueError("Currently only IoU and F1 metrics are implemented...")
    
    correctness = len(correct_points)/total_points*100
    
    return correctness, pers, high_thr, low_thr, merge_thr

@timed()
def compare_result_txt_to_groundtruth_label_dict(result_filename: str, gt_label_dict: dict, metric: str = "IoU"):
    """! @brief Takes a result .txt labels file and compares to a groundtruth given as a labels .txt file.
    @param result_filename The result .txt filename and location.
    @param groundtruth_filename The labels .txt groundtruth filename and location.
    @param metric (Optional) Which metric to use for evaluation: Intersection of Union ("IoU") 
    or F1-Score ("F1). Default is "IoU".
    @param plot_correctness_mask (Optional) Boolean whether to plot a mask (labels txt file) 
    with correct points or not. Default is False. 

    @return correctness The percentage of correctly labelled vertices in the result file 
    compared to the groundtruth file.
    """    
    
    comp_labels_class = Labels()
    comp_labels_class.load_from_txt(result_filename)
    comp_label = comp_labels_class.labels
    total_points = comp_labels_class.get_vertex_number()

    high = str(result_filename.split("/")[-1].split("_")[-3][:-1])
    low = str(result_filename.split("/")[-1].split("_")[-2][:-1])
    merge = str(result_filename.split("/")[-1].split("_")[-1][:-4])
    
    if metric == "IoU":
        IoU = compute_IoU(gt_label_dict, comp_label)
        correct_points = get_correct_points(gt_label_dict, comp_label, IoU)
    elif metric == "F1":
        F1 = compute_F1_Score(gt_label_dict, comp_label)
        correct_points = get_correct_points(gt_label_dict, comp_label, F1)
    else:
        raise ValueError("Currently only IoU and F1 metrics are implemented...")
    
    correctness = len(correct_points)/total_points*100
    
    return correctness, high, low, merge

@timed(False)
def compare_result_dict_to_groundtruth_label_dict(result_dict: str, gt_label_dict: dict, metric: str = "IoU"):
    """! @brief Takes a result .txt labels file and compares to a groundtruth given as a labels .txt file.
    @param result_dict The result segmentation as label dictionary.
    @param groundtruth_filename The labels .txt groundtruth filename and location.
    @param metric (Optional) Which metric to use for evaluation: Intersection of Union ("IoU") 
    or F1-Score ("F1). Default is "IoU".

    @return correctness The percentage of correctly labelled vertices in the result file 
    compared to the groundtruth file.
    """   
    if metric == "IoU":
        IoU = compute_IoU(gt_label_dict, result_dict)
        correct_points = get_correct_points(gt_label_dict, result_dict, IoU)
    elif metric == "F1":
        F1 = compute_F1_Score(gt_label_dict, result_dict)
        correct_points = get_correct_points(gt_label_dict, result_dict, F1)
    else:
        raise ValueError("Currently only IoU and F1 metrics are implemented...")
    
    total_points = 0
    for pts in gt_label_dict.values():
        total_points += len(pts)
    
    correctness = len(correct_points)/total_points*100
    
    return correctness

@timed()
def painted_ply_to_label_txt(filename, 
                             outfilename = None, 
                             clean_thresh = 10, 
                             connected_components = False,
                             sorted = False,
                             enumerated = False,
                             enum_start = 1):
    """! @brief Takes a colored .ply file and returns a labels .txt file based on those colors.
    @param filename The colored .ply filename and location.
    @param outfilename The .txt labels filename that will be created.
    @param clean_thresh (Optional) Threshold that gives the minimum number of vertices each label should have.
    If one color has fewer than this vertices, they are merged into the surrounding larger labels. Default
    is 10 (so no very little removal of too small labels). 

    @return labels Returns a label dictionary of the labels that were written to the output file.
    """
    # initiate and pass settings
    labels = Labels(sorted=sorted, enumerated=enumerated, enumerated_start= enum_start)
    labels.plyread.connected_components = connected_components
    labels.plyread.size_threshold = clean_thresh
    # read labels from ply
    labels.load_from_ply(filename)
    # write label txt
    if outfilename != None:
        labels.write_labels_txt(outfilename)
    return labels.labels
    
@timed()
def label_txt_to_label_txt(filename, 
                           outfilename = None, 
                           sorted = False,
                           enumerated = False,
                           enum_start = 1):
    """! @brief Takes a labels .txt file and returns a label dictionary.
    @param filename The labels .txt file to be read.
    @param sort_enum (Optional) Boolean whether to sort and enumerate the labels, so that the largest label 
    is label 1, the second largest label is label 2, etc. Default is True.

    @return labels Returns a label dictionary of the labels with key=label_id and value=set of vertex indices.
    """
    labels = Labels(sorted=sorted, enumerated=enumerated, enumerated_start=enum_start)
    labels.load_from_txt(filename)
    if outfilename != None:
        labels.write_labels_txt(outfilename)
    return labels.labels

@timed()
def label_dict_to_label_txt(labels,
                            outfilename, 
                            sorted = False,
                            enumerated = False,
                            enum_start = 1):
    """! @brief Takes a label dictionary and writes a corresponding labels .txt file.
    @param labels A label dictionary with key=label_id and value=set of vertex indices.
    @filename The filename of the labels .txt file to be written. (.txt will be added automatically)
    """
    labels = Labels(sorted=sorted, enumerated=enumerated, enumerated_start=enum_start)
    labels.load_from_dict(labels)
    labels.write_labels_txt(outfilename)

@timed()
def artifact3D_to_label_dict(filename, scarfilename, sort_enum = True, get_trafo = False):
    """! @brief Takes the output of the Artifact3D Software and returns their resulting labelling as a 
    label dictionary with key=label_id and value=set of vertex indices.
    @param filename An Artifact3D .mat file. Should be called "Qins-(object_name).mat" or so.
    @param scarfilename An Artifact3D .mat file containing the scar information. Should be called 
    "ScarsQins-(object_name).mat" or so.
    @param sort_enum (Optional) Boolean, whether to sort and enumerate the labels. Default is True.
    @param get_trafo (Optional) Boolean, whether to return the transformation as well or not. Default is False.

    return label_dict, (reorientation_trafo) The label dictionary of the Artifact3D Software result and optionally the 
    reorientation trafo used in Artifact3D.
    """
    label_dict, reorientation_trafo = artifact3D_to_labels(filename, scarfilename)
    if sort_enum:
        sort_enum_labels = {}
        for label_enum, indices in enumerate(sorted(label_dict.values(), key=lambda kv: len(kv), reverse=True)):
            sort_enum_labels[label_enum] = indices 
        label_dict = sort_enum_labels

    if get_trafo:
        return label_dict, reorientation_trafo
    else:
        return label_dict

@timed()
def artifact3D_get_trafo_dict(filename, scarfilename):
    """! @brief Reads the Artifact3D Softwares results and returns the reorientation they got to align the artefacts.
    @details The reorientation returned can be used to recreate the alignment done by the Artifact3D Software as follows:
    Flipvector f = (f1,f2,f3); Trafomat A (3x3 Matrix); Translationvector t = (delta_x, delta_y, delta_z)
    A point (x,y,z) in the Artifact3D coordinate system is translated back to the original mesh coordinate system,
    by performing the foloowing calculations:
    (x_orig,y_orig,z_orig) = (f1,f2,f3) * ((x,y,z).dot(A)) - (delta_x, delta_y, delta_z) 
    or
    x_orig = f * (x.dot(A)) - t
    So to get the Artifact3D coordinates from the original points, we have to reverse this operation:
    (x_art, y_art, z_art) = [(f1,f2,f3) * ((x_orig,y_orig,z_orig) + (delta_x, delta_y, delta_z))}.dot(A_inverse)
    or
    x_artifact3d = (f * (x_orig + t)).dot(A-1)  (A-1 = A inverted)

    @param filename An Artifact3D .mat file. Should be called "Qins-(object_name).mat" or so.
    @param scarfilename An Artifact3D .mat file containing the scar information. Should be called 
    "ScarsQins-(object_name).mat" or so.

    @return reorientation_trafo A dictionary containing 'Flipvector', 'Trafomatrix' and 'Translationvector' that 
    make up the reorientation.
    """
    reorientation_trafo = artifact3D_get_trafo(filename, scarfilename)
    return reorientation_trafo

@timed()
def artifact3D_to_label_txt(filename, scarfilename, outfilename, sort_enum = True):
    """! @brief Takes the output of the Artifact3D Software and writes their resulting labelling as a 
    label .txt file.
    @param filename An Artifact3D .mat file. Should be called "Qins-(object_name).mat" or so.
    @param scarfilename An Artifact3D .mat file containing the scar information. Should be called 
    "ScarsQins-(object_name).mat" or so.
    @param outfilename The name of the labels .txt file to be written.
    @param sort_enum (Optional) Boolean, whether to sort and enumerate the labels. Default is True.
    """
    label_dict = artifact3D_to_label_dict(filename, scarfilename, sort_enum=sort_enum, get_trafo=False)
    label_dict_to_label_txt(label_dict, outfilename)

    

