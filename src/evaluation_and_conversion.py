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
from .Evaluation.evaluate_metrics import compute_IoU, compute_F1_Score, get_correct_points
from .Evaluation.read_labels_txt import read_labels_txt
from .Evaluation.read_labels_from_color_ply import read_labels_from_color_ply
from .Evaluation.write_correctness_mask_txt import write_correctness_mask_txt
from .plot_data.write_labels_txt import write_Cell_labels_txt_file
from .Evaluation.clean_and_read_labels_from_color_ply import clean_and_read_labels_from_color_ply
from .Evaluation.artifact3D_conversions import artifact3D_to_labels, artifact3D_get_trafo

from .timer import timed

import os

@timed
def compare_result_txt_to_groundtruth_ply(result_filename, groundtruth_filename, metric = "IoU", plot_correctness_mask = False):
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
    comp_label, pers, high_thr, low_thr, merge_thr = read_labels_txt(result_filename, params=True)
    
    gt_label, total_points = read_labels_from_color_ply(groundtruth_filename)
    
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
    
    if plot_correctness_mask:
        write_correctness_mask_txt(total_points, correct_points, groundtruth_filename, os.path.splitext(result_filename)[0]+"_correct")
    
    correctness = len(correct_points)/total_points*100
    
    return correctness, pers, high_thr, low_thr, merge_thr

@timed   
def compare_result_txt_to_groundtruth_txt(result_filename, groundtruth_filename, metric = "IoU", plot_correctness_mask = False):
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
    comp_label, pers, high_thr, low_thr, merge_thr = read_labels_txt(result_filename, params=True)
    
    gt_label = read_labels_txt(groundtruth_filename, params = False)
    
    if metric == "IoU":
        IoU = compute_IoU(gt_label, comp_label)
        correct_points = get_correct_points(gt_label, comp_label, IoU)
    elif metric == "F1":
        F1 = compute_F1_Score(gt_label, comp_label)
        correct_points = get_correct_points(gt_label, comp_label, F1)
    else:
        raise ValueError("Currently only IoU and F1 metrics are implemented...")
    
    total_points = 0
    for pts in gt_label.values():
        total_points += len(pts)
    
    if plot_correctness_mask:
        write_correctness_mask_txt(total_points, correct_points, groundtruth_filename, os.path.splitext(result_filename)[0]+"_correct")
    
    correctness = len(correct_points)/total_points*100
    
    return correctness, pers, high_thr, low_thr, merge_thr

@timed
def compare_result_txt_to_groundtruth_label_dict(result_filename, gt_label_dict, metric = "IoU", plot_correctness_mask = False):
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
    comp_label, pers, high_thr, low_thr, merge_thr = read_labels_txt(result_filename, params=True)
    
    if metric == "IoU":
        IoU = compute_IoU(gt_label_dict, comp_label)
        correct_points = get_correct_points(gt_label_dict, comp_label, IoU)
    elif metric == "F1":
        F1 = compute_F1_Score(gt_label_dict, comp_label)
        correct_points = get_correct_points(gt_label_dict, comp_label, F1)
    else:
        raise ValueError("Currently only IoU and F1 metrics are implemented...")
    
    total_points = 0
    for pts in gt_label_dict.values():
        total_points += len(pts)
    
    if plot_correctness_mask:
        write_correctness_mask_txt(total_points, correct_points, "groundtruth_label_dict", os.path.splitext(result_filename)[0]+"_correct")
    
    correctness = len(correct_points)/total_points*100
    
    return correctness, pers, high_thr, low_thr, merge_thr

@timed    
def painted_ply_to_label_txt(filename, outfilename, clean_thresh = 0):
    """! @brief Takes a colored .ply file and returns a labels .txt file based on those colors.
    @param filename The colored .ply filename and location.
    @param outfilename The .txt labels filename that will be created.
    @param clean_thresh (Optional) Threshold that gives the minimum number of vertices each label should have.
    If one color has fewer than this vertices, they are merged into the surrounding larger labels. Default
    is 0 (so no removal of any small labels). 

    @return labels Returns a label dictionary of the labels that were written to the output file.
    """
    labels = clean_and_read_labels_from_color_ply(filename, outfilename, threshold=clean_thresh)
    return labels

@timed
def painted_ply_to_label_dict(filename, clean_thresh = 0):
    """! @brief Takes a colored .ply file and returns a labels dict based on those colors.
    @param filename The colored .ply filename and location.
    @param clean_thresh (Optional) Threshold that gives the minimum number of vertices each label should have.
    If one color has fewer than this vertices, they are merged into the surrounding larger labels. Default
    is 0 (so no removal of any small labels). 

    @return labels Returns a label dictionary.
    """
    labels = clean_and_read_labels_from_color_ply(filename, threshold=clean_thresh)
    return labels
    
@timed    
def label_txt_to_label_dict(filename, sort_enum = True):
    """! @brief Takes a labels .txt file and returns a label dictionary.
    @param filename The labels .txt file to be read.
    @param sort_enum (Optional) Boolean whether to sort and enumerate the labels, so that the largest label 
    is label 1, the second largest label is label 2, etc. Default is True.

    @return labels Returns a label dictionary of the labels with key=label_id and value=set of vertex indices.
    """
    labels = read_labels_txt(filename, params = False)
    
    if sort_enum:
        sort_enum_labels = {}
        for label_enum, indices in enumerate(sorted(labels.values(), key=lambda kv: len(kv), reverse=True)):
            sort_enum_labels[label_enum] = indices 
        labels = sort_enum_labels
    return labels

@timed
def label_dict_to_label_txt(labels, filename):
    """! @brief Takes a label dictionary and writes a corresponding labels .txt file.
    @param labels A label dictionary with key=label_id and value=set of vertex indices.
    @filename The filename of the labels .txt file to be written. (.txt will be added automatically)
    """
    write_Cell_labels_txt_file(labels, filename)

@timed    
def label_txt_to_sorted_label_txt(filename, outfilename):
    """! @brief Takes a labels .txt file and writes another labels .txt file with the labels being sorted and enumerated.
    @param filename The labels .txt file to be read.
    @param outfilename The labels .txt file to be written (sorted and enumerated).
    """
    sorted_labels = label_txt_to_label_dict(filename, sort_enum = True)
    label_dict_to_label_txt(sorted_labels, outfilename)
    return sorted_labels

@timed
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

@timed
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

@timed
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

    

