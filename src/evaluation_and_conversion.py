# Collection of evaluation functions
from .Evaluation.evaluate_metrics import compute_IoU, compute_F1_Score, get_correct_points
from .Evaluation.read_labels_txt import read_labels_txt
from .Evaluation.read_labels_from_color_ply import read_labels_from_color_ply
from .Evaluation.write_correctness_mask_txt import write_correctness_mask_txt
from .PlotData.write_labels_txt import write_Cell_labels_txt_file
from .Evaluation.clean_and_read_labels_from_color_ply import clean_and_read_labels_from_color_ply
from .Evaluation.artifact3D_conversions import artifact3D_to_labels, artifact3D_get_trafo

import os

def compare_result_txt_to_groundtruth_ply(result_filename, groundtruth_filename, metric = "IoU", plot_correctness_mask = False):
    
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
    
    return correctness
    
def compare_result_txt_to_groundtruth_txt(result_filename, groundtruth_filename, metric = "IoU", plot_correctness_mask = False):
    
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
    
    return correctness
    
def painted_ply_to_label_txt(filename, outfilename, clean_thresh = 0):
    labels = clean_and_read_labels_from_color_ply(filename, outfilename, threshold=clean_thresh)
    return labels
    
    
def label_txt_to_label_dict(filename, sort_enum = True):
    labels = read_labels_txt(filename, params = False)
    
    if sort_enum:
        sort_enum_labels = {}
        for label_enum, indices in enumerate(sorted(labels.values(), key=lambda kv: len(kv), reverse=True)):
            sort_enum_labels[label_enum] = indices 
        labels = sort_enum_labels
    return labels

def label_dict_to_label_txt(labels, filename):
    write_Cell_labels_txt_file(labels, filename)
    
def label_txt_to_sorted_label_txt(filename, outfilename):
    sorted_labels = label_txt_to_label_dict(filename, sort_enum = True)
    label_dict_to_label_txt(sorted_labels, outfilename)
    return sorted_labels

def artifact3D_to_label_dict(filename, scarfilename, sort_enum = True, get_trafo = False):
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

def artifact3D_get_trafo_dict(filename, scarfilename):
    reorientation_trafo = artifact3D_get_trafo(filename, scarfilename)
    return reorientation_trafo

def artifact3D_to_label_txt(filename, scarfilename, outfilename, sort_enum = True):
    label_dict = artifact3D_to_label_dict(filename, scarfilename, sort_enum=sort_enum, get_trafo=False)
    label_dict_to_label_txt(label_dict, outfilename)

    

