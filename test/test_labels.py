import pytest

from ..src.plot_data.labels_read_write import Labels

LABELS_DICT = {1 : {1,2,4},
               2 : {3,5,6,7,8},
               3 : {23,24},
               5 : {12,14},
               6 : {},
               982 : {13}}

def test_load_from_dict():
    labels = Labels()
    labels.load_from_dict(LABELS_DICT)
    assert labels.get_vertex_number == 13
    assert len(labels.labels) == 6
    assert labels.labels[1] == {1,2,4}
    assert labels.labels[6] == {}
    assert labels.labels[982] == {13}
    
def test_load_from_txt():
    labels = Labels()
    labels.load_from_txt("./test_data/labels_test.txt")
    
def test_load_from_ply():
    labels = Labels()
    labels.load_from_txt("./test_data/cube_colored.ply")
    todo=0
    
def test_load_from_cells():
    todo=0
    
def test_sorting():
    todo=0

def test_enumerate():
    todo=0
    
    
labels = Labels(sorted=True, enumerated=True, enumerated_start=3)
labels.load_from_ply("./cube_colored.ply")
labels.write_labels_txt("./cube_colored_labels_test.txt")

labels2 = Labels()
labels2.load_from_txt("./cube_colored_labels_test.txt.txt")
labels2.write_labels_txt("./test2.txt")