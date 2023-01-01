import pytest
import random

def test_changed_vertex_order():
    do=0

def alternate_vertex_order(vert_dict, edge_dict, face_dict):
    new_vert_dict = {}
    new_edge_dict = {}
    new_face_dict = {}

    keys = list(vert_dict.keys())

    # Randomly shuffle the list of keys
    random.shuffle(keys)

    transformation_dict = {original_key: shuffled_key for original_key, shuffled_key in zip(vert_dict.keys(), keys)}

    for old_key, vert in vert_dict.items():
        vert.index = transformation_dict[old_key]
        new_vert_dict[transformation_dict[old_key]] = vert

