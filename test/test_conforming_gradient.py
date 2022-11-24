import pytest

from src.morse import Morse

def trivial_labels(morse):
    labels = {}
    for ind in morse.Vertices.keys():
        labels[ind] = 1
    morse.InitialLabels = labels

def test_trivial_labels():
    p = False

    # Initialize test data
    file = "Data/vase_reduced_cleaned_painted.ply"

    data1 = Morse()
    data2 = Morse()

    data1.load_mesh_ply(file, quality_index=2)
    data2.load_mesh_ply(file, quality_index=2)

    data1.ProcessLowerStars()

    #data2.load_labels("Data/vase_reduced_cleaned_painted_labels.txt") #need trivial label file
    trivial_labels(data2)
    data2.ConformingGradient()

    if p:
        print("Critical Simplices")
        print(data1.C)
        print(data2.C)
        print("Point-Edge Pairings")
        print(data1.V12)
        print(data2.V12)
        print("Edge-Face Pairings")
        print(data1.V23)
        print(data2.V23)

    assert(data1.C == data2.C and data1.V12 == data2.V12 and data1.V23 == data2.V23)