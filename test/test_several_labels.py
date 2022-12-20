import pytest
from src.morse import Morse

def cells(file):
    p = False

    # Initialize test data
    data = Morse()

    data.load_mesh_ply(file, quality_index=2)

    data.load_labels("Data/vase_reduced_cleaned_painted_labels.txt") 
    data.ConformingGradient()

    if p:
        print("Critical Simplices")
        print(data.C)
        print("Point-Edge Pairings")
        print(data.V12)
        print("Edge-Face Pairings")
        print(data.V23)

    cells = data.ExtractMorseCells(0)

    counter = 0
    for cell in cells.Cells.values():
        labels = set()
        for v in cell.vertices:
            if v not in cell.boundary:
                labels.add(data.UserLabels['vertices'][v])
        if p:
            print(labels)
        if len(labels) > 1:
            counter += 1
    assert(counter < 0.1*len(cells.Cells))



def test_conforming_gradient():
    for file in ["Data/torus_distorted_painted.ply"]:#, "Data/torus_distorted_painted.ply", "Data/vase_reduced_cleaned_painted.ply"]:
        cells(file)