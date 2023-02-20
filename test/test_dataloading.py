import pytest
import random
from copy import deepcopy
from ..src.Algorithms.load_data.datastructures import Simplex
from ..src.morse import Morse

def test_changed_vertex_order():
    original_data = Morse()
    shuffled_data = Morse()
    original_data.load_mesh_ply("test/test_data/cube_noise2_r0.20_n4_v256.volume.ply", quality_index=3, inverted=True)

    # shuffle vertex indices and adapt edges and faces
    new_vert_dict, new_edge_dict, new_face_dict, transformation_dict = alternate_vertex_order(original_data.Vertices, original_data.Edges, original_data.Faces)
    # fill shuffled_data structure with new dictionaries and min,max and range of the function values
    shuffled_data.reset()
    shuffled_data.Vertices = new_vert_dict
    shuffled_data.Edges = new_edge_dict
    shuffled_data.Faces = new_face_dict
    shuffled_data.filename = original_data.filename
    shuffled_data.min = original_data.min
    shuffled_data.max = original_data.max
    shuffled_data.range = original_data.range

    original_data.process_lower_stars()
    shuffled_data.process_lower_stars()

    check_equal_PLS_outcome(original_data, shuffled_data, transformation_dict)

    original_data.extract_morse_complex()
    shuffled_data.extract_morse_complex()

    check_equal_EMC_outcome(original_data, shuffled_data, transformation_dict)

def check_equal_PLS_outcome(orig_data: Morse, shuff_data: Morse, trafo_dict: dict):
    # need to check C, V12 and V23
    for orig_v_ind, orig_e_ind in orig_data.V12.items():
        assert trafo_dict[orig_v_ind] in shuff_data.V12.keys()
        assert shuff_data.V12[trafo_dict[orig_v_ind]] == orig_e_ind
    for orig_e_ind, orig_f_ind in orig_data.V23.items():
        assert orig_e_ind in shuff_data.V23.keys()
        assert shuff_data.V23[orig_e_ind] == orig_f_ind
    for orig_v_ind in orig_data.C[0]:
        assert trafo_dict[orig_v_ind] in shuff_data.C[0]
    assert orig_data.C[1] == shuff_data.C[1]
    assert orig_data.C[2] == shuff_data.C[2]


def check_equal_EMC_outcome(orig_data: Morse, shuff_data: Morse, trafo_dict: dict):
    assert set(orig_data.MorseComplex.CritEdges.keys()) == set(shuff_data.MorseComplex.CritEdges.keys())
    assert set(orig_data.MorseComplex.CritFaces.keys()) == set(shuff_data.MorseComplex.CritFaces.keys())
    for v_ind, vert in orig_data.MorseComplex.CritVertices.items():
        assert vert == shuff_data.MorseComplex.CritVertices[trafo_dict[v_ind]]

def alternate_vertex_order(vert_dict: dict, edge_dict: dict, face_dict: dict):
    new_vert_dict = {}
    new_edge_dict = {}
    new_face_dict = {}

    keys = list(vert_dict.keys())

    # Randomly shuffle the list of keys
    random.shuffle(keys)

    transformation_dict = {original_ind: shuffled_ind for original_ind, shuffled_ind in zip(vert_dict.keys(), keys)}

    for old_ind, vert in vert_dict.items():
        new_vert = deepcopy(vert)
        new_vert.index = transformation_dict[old_ind]
        new_vert_dict[transformation_dict[old_ind]] = new_vert

    for vert in new_vert_dict.values():
        new_neighbors  = set()
        for old_ind in vert.neighbors:
            new_neighbors.add(transformation_dict[old_ind])
        vert.neighbors = new_neighbors

    for e_ind, edge in edge_dict.items():
        new_indices = set()
        for old_ind in edge.indices:
            new_indices.add(transformation_dict[old_ind])
        new_edge_dict[e_ind] = Simplex(indices=new_indices, index=e_ind)
        new_edge_dict[e_ind].set_fun_val(new_vert_dict)

    for f_ind, face in face_dict.items():
        new_indices = set()
        for old_ind in face.indices:
            new_indices.add(transformation_dict[old_ind])
        new_face_dict[f_ind] = Simplex(indices=new_indices, index=f_ind)
        new_face_dict[f_ind].set_fun_val(new_vert_dict)

    return new_vert_dict, new_edge_dict, new_face_dict, transformation_dict

