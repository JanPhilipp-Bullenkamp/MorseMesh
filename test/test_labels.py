import pytest
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from src.evaluation_and_labels.labels_read_write import Labels

LABELS_DICT = {1 : {1,2,4},
               2 : {3,5,6,7,8},
               3 : {23,24},
               5 : {12,14},
               6 : {},
               982 : {13}}

def test_load_from_dict():
    labels = Labels()
    labels.load_from_dict(LABELS_DICT)
    assert labels.get_vertex_number() == 13
    assert len(labels.labels) == 6
    assert labels.labels[1] == {1,2,4}
    assert labels.labels[6] == {}
    assert labels.labels[982] == {13}
    
def test_load_from_txt():
    labels = Labels()
    labels.load_from_txt("./test_data/labels_test.txt")
    assert labels.get_vertex_number() == 6146
    
def test_load_from_ply():
    labels = Labels()
    labels.load_from_ply("./test_data/cube_colored.ply")
    todo=0
    
def test_load_from_cells():
    todo=0
    
def test_sorting():
    todo=0

def test_enumerate():
    todo=0
    