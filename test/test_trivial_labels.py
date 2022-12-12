import pytest
import filecmp

from src.morse import Morse

def trivial_labels(morse):
    vertexLabels = {}
    for ind in morse.Vertices.keys():
        vertexLabels[ind] = 1
    edgeLabels = {}
    faceLabels = {}

    for key in morse.Edges.keys():
        edgeLabels[key] = set()
        for i in morse.Edges[key].indices:
            edgeLabels[key].add(vertexLabels[i])

    for key in morse.Faces.keys():
        faceLabels[key] = set()
        for i in morse.Faces[key].indices:
            faceLabels[key].add(vertexLabels[i])

    morse.UserLabels = {'vertices': vertexLabels, 'edges': edgeLabels, 'faces': faceLabels}

def pairings(file):
    p = False

    # Initialize test data
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

def reduction(file):
    p = False

    # Initialize test data
    data1 = Morse()
    data2 = Morse()

    data1.load_mesh_ply(file, quality_index=2)
    data2.load_mesh_ply(file, quality_index=2)
    trivial_labels(data2)

    data1.ProcessLowerStars()
    data2.ProcessLowerStars()

    data1.ExtractMorseComplex()
    data2.ExtractMorseComplex()

    data1.ReduceMorseComplex(3)
    data2.ReduceMorseComplex(3, conforming = True)        

    if p:
        print(data1.reducedMorseComplexes[3])
        print(data2.reducedMorseComplexes[3])

    data1.plot_MorseComplex_ply(3, "test/data1", path_color=[255,0,255], detailed=True, separate_points_file=True)
    data2.plot_MorseComplex_ply(3, "test/data2", path_color=[255,0,255], detailed=True, separate_points_file=True)

    assert(filecmp.cmp("test/data1_3P_DetailedOverlayMorseComplex.ply", "test\data2_3P_DetailedOverlayMorseComplex.ply") and filecmp.cmp("test/data1_3P_DetailedOverlayMorseComplex_CritPoints.ply", "test\data2_3P_DetailedOverlayMorseComplex_CritPoints.ply"))

def test_conforming_gradient():
    for file in ["Data/small_torus_painted.ply", "Data/torus_distorted.ply", "Data/vase_reduced_cleaned_painted.ply"]:
        pairings(file)

def test_conforming_reduction():
    for file in ["Data/small_torus_painted.ply", "Data/torus_distorted.ply", "Data/vase_reduced_cleaned_painted.ply"]:
        reduction(file)
