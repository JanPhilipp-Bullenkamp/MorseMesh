from plyfile import PlyData, PlyElement
import numpy as np
import timeit

##### Plot with paths
def write_crit_and_base_filesWITHPATH_reducedComplex(C, Paths, data, rawdata, target_base):
    
    start_eff2 = timeit.default_timer()

    vertex_raw = []
    faces_raw = []
    
    # translates the vertex index from data structure to the list index in the plotting file. Relevant 
    #for plotting the faces, since we need the list indices for the given vertex indices
     
    vertex_to_index_translator = {}
    counter = 0
    for index, position in data['position'].items():
        vertex_raw.append(tuple((position[0], 
                             position[1], 
                             position[2],
                             0,
                             0, 
                             0,
                             0,
                             index)))
        
        vertex_to_index_translator[index] = counter
        counter +=1
    
    
    vertex_data_raw = np.array(vertex_raw, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
    
    used_faces = set()
    for vertex, link in data['link'].items():
        for neighbor in link:
            if len(link.intersection(data['link'][neighbor])) != 0:
                for inter in link.intersection(data['link'][neighbor]):
                    
                    if tuple((sorted((vertex,inter,neighbor)))) not in used_faces:            
                        
                        used_faces.add(tuple((sorted((vertex,neighbor,inter)))) )
                        faces_raw.append(tuple((tuple((sorted((vertex_to_index_translator[vertex],
                                                 vertex_to_index_translator[neighbor],
                                                 vertex_to_index_translator[inter])))),
                                                255,
                                                255,
                                                255,
                                                0)))

                            
    faces_data_raw = np.array(faces_raw, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face_raw = PlyElement.describe(faces_data_raw, 'face')
    el_vertex_raw = PlyElement.describe(vertex_data_raw, 'vertex')
    PlyData([el_vertex_raw, el_face_raw], text=True).write(target_base)  # , text=False, byte_order='<'
    
    time_eff2 = timeit.default_timer() -start_eff2
    print('Time writing base file:', time_eff2)  
    return 1
