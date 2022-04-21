from plyfile import PlyData, PlyElement
import numpy as np
import timeit

##### Plot with paths
def write_crit_and_base_filesWITHPATH(C, Paths, rawdata, target_base, target_crit, target_crit_pts):
    start_eff1 = timeit.default_timer()
    
    vertex = []
    faces = []
    split_faces = []
    counter = 0
    for ind in range(len(rawdata.elements[0].data)):
        if ind in C[0].keys():
            for i in range(3):
                vertex.append(tuple((rawdata.elements[0].data[ind][0], 
                                     rawdata.elements[0].data[ind][1], 
                                     rawdata.elements[0].data[ind][2],
                                     255,
                                     0,
                                     0,
                                     255,
                                     counter)))
                counter += 1
            
            faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                 255, 
                                 0, 
                                 0, 
                                 255)))
        '''
    for edge in C[1].keys():
        vertex.append(tuple((rawdata.elements[0].data[edge[0]][0], 
                             rawdata.elements[0].data[edge[0]][1], 
                             rawdata.elements[0].data[edge[0]][2],
                             0,
                             255,
                             0,
                             255,
                             counter)))
        counter += 1
        
        for i in range(2):
            vertex.append(tuple((rawdata.elements[0].data[edge[1]][0], 
                                 rawdata.elements[0].data[edge[1]][1], 
                                 rawdata.elements[0].data[edge[1]][2],
                                 0,
                                 255,
                                 0,
                                 255,
                                 counter)))
            counter += 1
        
        faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                            0,
                            255,
                            0,
                            255)))
                '''
                
    vertex_data = np.array(vertex, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
            
    faces_data = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face = PlyElement.describe(faces_data, 'face')
    el_vertex = PlyElement.describe(vertex_data, 'vertex')
    PlyData([el_vertex, el_face], text=True).write(target_crit_pts) 
    
    
    vertex = []
    faces = []
    split_faces = []
    counter = 0
    for ind in range(len(rawdata.elements[0].data)):
        if ind in C[0].keys():
            for i in range(3):
                vertex.append(tuple((rawdata.elements[0].data[ind][0], 
                                     rawdata.elements[0].data[ind][1], 
                                     rawdata.elements[0].data[ind][2],
                                     255,
                                     0,
                                     0,
                                     255,
                                     counter)))
                counter += 1
            
            faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                 255, 
                                 0, 
                                 0, 
                                 255)))
            
    for edge in C[1].keys():
        vertex.append(tuple((rawdata.elements[0].data[edge[0]][0], 
                             rawdata.elements[0].data[edge[0]][1], 
                             rawdata.elements[0].data[edge[0]][2],
                             0,
                             255,
                             0,
                             0,
                             counter)))
        counter += 1
        
        for i in range(2):
            vertex.append(tuple((rawdata.elements[0].data[edge[1]][0], 
                                 rawdata.elements[0].data[edge[1]][1], 
                                 rawdata.elements[0].data[edge[1]][2],
                                 0,
                                 255,
                                 0,
                                 0,
                                 counter)))
            counter += 1
        
        faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                            0,
                            255,
                            0,
                            255)))
        
        for face_loc in Paths[edge].keys():
            for elt in Paths[edge][face_loc]:
                if np.array(elt).shape == (2,):
                    vertex.append(tuple((rawdata.elements[0].data[elt[0]][0], 
                                         rawdata.elements[0].data[elt[0]][1], 
                                         rawdata.elements[0].data[elt[0]][2],
                                         255,
                                         0,
                                         255,
                                         0,
                                         counter)))
                    counter += 1

                    for i in range(2):
                        vertex.append(tuple((rawdata.elements[0].data[elt[1]][0], 
                                             rawdata.elements[0].data[elt[1]][1], 
                                             rawdata.elements[0].data[elt[1]][2],
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                    faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                        255,
                                        0,
                                        255,
                                        255)))
                
    for face in C[2].keys():
        #add first midpoint twice!!!
        for i in range(2):
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[1]][0]+rawdata.elements[0].data[face[2]][0])/3, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[1]][1]+rawdata.elements[0].data[face[2]][1])/3, 
                                 (rawdata.elements[0].data[face[0]][2]+rawdata.elements[0].data[face[1]][2]+rawdata.elements[0].data[face[2]][2])/3,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
        
        help_counter = 0
        if tuple((face[0],face[1])) in Paths[face] or tuple((face[1],face[0])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[1]][0])/2, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[1]][1])/2, 
                                 (rawdata.elements[0].data[face[0]][2]+rawdata.elements[0].data[face[1]][2])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
        
        if tuple((face[1],face[2])) in Paths[face] or tuple((face[2],face[1])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[1]][0]+rawdata.elements[0].data[face[2]][0])/2, 
                                 (rawdata.elements[0].data[face[1]][1]+rawdata.elements[0].data[face[2]][1])/2, 
                                 (rawdata.elements[0].data[face[1]][2]+rawdata.elements[0].data[face[2]][2])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
            
        if tuple((face[0],face[2])) in Paths[face] or tuple((face[2],face[0])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[2]][0])/2, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[2]][1])/2, 
                                 (rawdata.elements[0].data[face[0]][2]+rawdata.elements[0].data[face[2]][2])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
            
            
            
        
        
        for face_loc in Paths[face].keys():
            for elt in Paths[face][face_loc]:
                #add midpoint twice
                if np.array(elt).shape == (3,):
                    for i in range(2):
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[1]][0]+rawdata.elements[0].data[elt[2]][0])/3, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[1]][1]+rawdata.elements[0].data[elt[2]][1])/3, 
                                             (rawdata.elements[0].data[elt[0]][2]+rawdata.elements[0].data[elt[1]][2]+rawdata.elements[0].data[elt[2]][2])/3,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                    help_counter = 0
                    if tuple((elt[0],elt[1])) in Paths[face][face_loc] or tuple((elt[1],elt[0])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[1]][0])/2, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[1]][1])/2, 
                                             (rawdata.elements[0].data[elt[0]][2]+rawdata.elements[0].data[elt[1]][2])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 
                    if tuple((elt[1],elt[2])) in Paths[face][face_loc] or tuple((elt[2],elt[1])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[1]][0]+rawdata.elements[0].data[elt[2]][0])/2, 
                                             (rawdata.elements[0].data[elt[1]][1]+rawdata.elements[0].data[elt[2]][1])/2, 
                                             (rawdata.elements[0].data[elt[1]][2]+rawdata.elements[0].data[elt[2]][2])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 

                    if tuple((elt[0],elt[2])) in Paths[face][face_loc] or tuple((elt[2],elt[0])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[2]][0])/2, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[2]][1])/2, 
                                             (rawdata.elements[0].data[elt[0]][2]+rawdata.elements[0].data[elt[2]][2])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 
                
                
    vertex_data = np.array(vertex, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
            
    faces_data = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face = PlyElement.describe(faces_data, 'face')
    el_vertex = PlyElement.describe(vertex_data, 'vertex')
    PlyData([el_vertex, el_face], text=True).write(target_crit)  # , text=False, byte_order='<'
    
    time_eff1 = timeit.default_timer() -start_eff1
    print('Time writing critical cells in file:', time_eff1)  

    start_eff2 = timeit.default_timer()

    vertex_raw = []
    faces_raw = []
    
    for ind in range(len(rawdata.elements[0].data)):
        vertex_raw.append(tuple((rawdata.elements[0].data[ind][0], 
                             rawdata.elements[0].data[ind][1], 
                             rawdata.elements[0].data[ind][2],
                             0,
                             0, 
                             0,
                             0,
                             rawdata.elements[0].data[ind][2])))
    
    vertex_data_raw = np.array(vertex_raw, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
    
    for ind in range(len(rawdata.elements[1].data)):
        if tuple((rawdata.elements[1].data[ind][0])) in C[2].keys():
            faces_raw.append(tuple((rawdata.elements[1].data[ind][0],
                                0,
                                0,
                                255,
                                255)))
        else:
            faces_raw.append(tuple((rawdata.elements[1].data[ind][0],
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





#### write file with interpolated z values



def write_crit_and_base_filesWITHPATH_and_new_interpolated(C, Paths, data, rawdata, new_vertices, new_faces, replaced_faces, target_base, target_crit):
    start_eff1 = timeit.default_timer()

    vertex = []
    faces = []
    split_faces = []
    counter = 0
    for ind in range(len(rawdata.elements[0].data)):
        if ind in C[0].keys():
            for i in range(3):
                vertex.append(tuple((rawdata.elements[0].data[ind][0], 
                                     rawdata.elements[0].data[ind][1], 
                                     data['vertex'][ind],
                                     255,
                                     0,
                                     0,
                                     255,
                                     counter)))
                counter += 1
            
            faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                 255, 
                                 0, 
                                 0, 
                                 255)))
            
            
    for edge in C[1].keys():
        vertex.append(tuple((rawdata.elements[0].data[edge[0]][0], 
                             rawdata.elements[0].data[edge[0]][1], 
                             data['vertex'][edge[0]],
                             0,
                             255,
                             0,
                             0,
                             counter)))
        counter += 1
        
        for i in range(2):
            vertex.append(tuple((rawdata.elements[0].data[edge[1]][0], 
                                 rawdata.elements[0].data[edge[1]][1], 
                                 data['vertex'][edge[1]],
                                 0,
                                 255,
                                 0,
                                 0,
                                 counter)))
            counter += 1
        
        faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                            0,
                            255,
                            0,
                            255)))
        
        for face_loc in Paths[edge].keys():
            for elt in Paths[edge][face_loc]:
                if np.array(elt).shape == (2,):
                    vertex.append(tuple((rawdata.elements[0].data[elt[0]][0], 
                                         rawdata.elements[0].data[elt[0]][1], 
                                         data['vertex'][elt[0]],
                                         255,
                                         0,
                                         255,
                                         0,
                                         counter)))
                    counter += 1

                    for i in range(2):
                        vertex.append(tuple((rawdata.elements[0].data[elt[1]][0], 
                                             rawdata.elements[0].data[elt[1]][1], 
                                             data['vertex'][elt[1]],
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                    faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                        255,
                                        0,
                                        255,
                                        255)))
                
    for face in C[2].keys():
        #add first midpoint twice!!!
        for i in range(2):
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[1]][0]+rawdata.elements[0].data[face[2]][0])/3, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[1]][1]+rawdata.elements[0].data[face[2]][1])/3, 
                                 (data['vertex'][face[0]]+data['vertex'][face[1]]+data['vertex'][face[2]])/3,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
        
        help_counter = 0
        if tuple((face[0],face[1])) in Paths[face] or tuple((face[1],face[0])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[1]][0])/2, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[1]][1])/2, 
                                 (data['vertex'][face[0]]+data['vertex'][face[1]])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
        
        if tuple((face[1],face[2])) in Paths[face] or tuple((face[2],face[1])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[1]][0]+rawdata.elements[0].data[face[2]][0])/2, 
                                 (rawdata.elements[0].data[face[1]][1]+rawdata.elements[0].data[face[2]][1])/2, 
                                 (data['vertex'][face[1]]+data['vertex'][face[2]])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
            
        if tuple((face[0],face[2])) in Paths[face] or tuple((face[2],face[0])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[2]][0])/2, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[2]][1])/2, 
                                 (data['vertex'][face[0]]+data['vertex'][face[2]])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
            
            
            
        
        
        for face_loc in Paths[face].keys():
            for elt in Paths[face][face_loc]:
                #add midpoint twice
                if np.array(elt).shape == (3,):
                    for i in range(2):
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[1]][0]+rawdata.elements[0].data[elt[2]][0])/3, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[1]][1]+rawdata.elements[0].data[elt[2]][1])/3, 
                                             (data['vertex'][elt[0]]+data['vertex'][elt[1]]+data['vertex'][elt[2]])/3,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                    help_counter = 0
                    if tuple((elt[0],elt[1])) in Paths[face][face_loc] or tuple((elt[1],elt[0])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[1]][0])/2, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[1]][1])/2, 
                                             (data['vertex'][elt[0]]+data['vertex'][elt[1]])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 
                    if tuple((elt[1],elt[2])) in Paths[face][face_loc] or tuple((elt[2],elt[1])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[1]][0]+rawdata.elements[0].data[elt[2]][0])/2, 
                                             (rawdata.elements[0].data[elt[1]][1]+rawdata.elements[0].data[elt[2]][1])/2, 
                                             (data['vertex'][elt[1]]+data['vertex'][elt[2]])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 

                    if tuple((elt[0],elt[2])) in Paths[face][face_loc] or tuple((elt[2],elt[0])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[2]][0])/2, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[2]][1])/2, 
                                             (data['vertex'][elt[0]]+data['vertex'][elt[2]])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 
                
                
    vertex_data = np.array(vertex, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
            
    faces_data = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face = PlyElement.describe(faces_data, 'face')
    el_vertex = PlyElement.describe(vertex_data, 'vertex')
    PlyData([el_vertex, el_face], text=True).write(target_crit)  # , text=False, byte_order='<'
    
    time_eff1 = timeit.default_timer() -start_eff1
    print('Time writing critical cells in file:', time_eff1)  

    start_eff2 = timeit.default_timer()

    vertex_raw = []
    faces_raw = []
    
    for ind in range(len(rawdata.elements[0].data)):
        vertex_raw.append(tuple((rawdata.elements[0].data[ind][0], 
                             rawdata.elements[0].data[ind][1], 
                             data['vertex'][ind],
                             0,
                             0, 
                             0,
                             0,
                             rawdata.elements[0].data[ind][2])))
        
    for key, value in new_vertices.items():
        if key not in C[2].keys() and key not in C[1].keys():
            vertex_raw.append(tuple((value[1][0],
                                     value[1][1],
                                     data['vertex'][value[0]],
                                     0,
                                     0,
                                     0,
                                     255,
                                     0.0)))
        elif key in C[2].keys():
            vertex_raw.append(tuple((value[1][0],
                                     value[1][1],
                                     data['vertex'][value[0]],
                                     0,
                                     0,
                                     255,
                                     255,
                                     0.0)))
        elif key in C[1].keys():
            vertex_raw.append(tuple((value[1][0],
                                     value[1][1],
                                     data['vertex'][value[0]],
                                     0,
                                     255,
                                     0,
                                     255,
                                     0.0)))
    
    vertex_data_raw = np.array(vertex_raw, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
    
    for ind in range(len(rawdata.elements[1].data)):
        if tuple((rawdata.elements[1].data[ind][0])) in replaced_faces:
            continue
        else:
            faces_raw.append(tuple((rawdata.elements[1].data[ind][0],
                                255,
                                255,
                                255,
                                0)))
    for face in new_faces:
        faces_raw.append(tuple((face,
                                255,
                                255,
                                255,
                                255)))
            
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





##### write file with paths and newly created cells on 1-2-1-2-.. paths

def write_crit_and_base_filesWITHPATH_and_new(C, Paths, rawdata, new_vertices, new_faces, replaced_faces, target_base, target_crit):
    start_eff1 = timeit.default_timer()

    vertex = []
    faces = []
    split_faces = []
    counter = 0
    for ind in range(len(rawdata.elements[0].data)):
        if ind in C[0].keys():
            for i in range(3):
                vertex.append(tuple((rawdata.elements[0].data[ind][0], 
                                     rawdata.elements[0].data[ind][1], 
                                     rawdata.elements[0].data[ind][2],
                                     255,
                                     0,
                                     0,
                                     255,
                                     counter)))
                counter += 1
            
            faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                 255, 
                                 0, 
                                 0, 
                                 255)))
            
            
    for edge in C[1].keys():
        vertex.append(tuple((rawdata.elements[0].data[edge[0]][0], 
                             rawdata.elements[0].data[edge[0]][1], 
                             rawdata.elements[0].data[edge[0]][2],
                             0,
                             255,
                             0,
                             0,
                             counter)))
        counter += 1
        
        for i in range(2):
            vertex.append(tuple((rawdata.elements[0].data[edge[1]][0], 
                                 rawdata.elements[0].data[edge[1]][1], 
                                 rawdata.elements[0].data[edge[1]][2],
                                 0,
                                 255,
                                 0,
                                 0,
                                 counter)))
            counter += 1
        
        faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                            0,
                            255,
                            0,
                            255)))
        
        for face_loc in Paths[edge].keys():
            for elt in Paths[edge][face_loc]:
                if np.array(elt).shape == (2,):
                    vertex.append(tuple((rawdata.elements[0].data[elt[0]][0], 
                                         rawdata.elements[0].data[elt[0]][1], 
                                         rawdata.elements[0].data[elt[0]][2],
                                         255,
                                         0,
                                         255,
                                         0,
                                         counter)))
                    counter += 1

                    for i in range(2):
                        vertex.append(tuple((rawdata.elements[0].data[elt[1]][0], 
                                             rawdata.elements[0].data[elt[1]][1], 
                                             rawdata.elements[0].data[elt[1]][2],
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                    faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                        255,
                                        0,
                                        255,
                                        255)))
                
    for face in C[2].keys():
        #add first midpoint twice!!!
        for i in range(2):
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[1]][0]+rawdata.elements[0].data[face[2]][0])/3, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[1]][1]+rawdata.elements[0].data[face[2]][1])/3, 
                                 (rawdata.elements[0].data[face[0]][2]+rawdata.elements[0].data[face[1]][2]+rawdata.elements[0].data[face[2]][2])/3,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
        
        help_counter = 0
        if tuple((face[0],face[1])) in Paths[face] or tuple((face[1],face[0])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[1]][0])/2, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[1]][1])/2, 
                                 (rawdata.elements[0].data[face[0]][2]+rawdata.elements[0].data[face[1]][2])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
        
        if tuple((face[1],face[2])) in Paths[face] or tuple((face[2],face[1])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[1]][0]+rawdata.elements[0].data[face[2]][0])/2, 
                                 (rawdata.elements[0].data[face[1]][1]+rawdata.elements[0].data[face[2]][1])/2, 
                                 (rawdata.elements[0].data[face[1]][2]+rawdata.elements[0].data[face[2]][2])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
            
        if tuple((face[0],face[2])) in Paths[face] or tuple((face[2],face[0])) in Paths[face]:
            vertex.append(tuple(((rawdata.elements[0].data[face[0]][0]+rawdata.elements[0].data[face[2]][0])/2, 
                                 (rawdata.elements[0].data[face[0]][1]+rawdata.elements[0].data[face[2]][1])/2, 
                                 (rawdata.elements[0].data[face[0]][2]+rawdata.elements[0].data[face[2]][2])/2,
                                 255,
                                 0,
                                 255,
                                 0,
                                 counter)))
            counter += 1
            
            faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                    255,
                                    0,
                                    255,
                                    255)))
            help_counter += 1 
            
            
            
        
        
        for face_loc in Paths[face].keys():
            for elt in Paths[face][face_loc]:
                #add midpoint twice
                if np.array(elt).shape == (3,):
                    for i in range(2):
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[1]][0]+rawdata.elements[0].data[elt[2]][0])/3, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[1]][1]+rawdata.elements[0].data[elt[2]][1])/3, 
                                             (rawdata.elements[0].data[elt[0]][2]+rawdata.elements[0].data[elt[1]][2]+rawdata.elements[0].data[elt[2]][2])/3,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                    help_counter = 0
                    if tuple((elt[0],elt[1])) in Paths[face][face_loc] or tuple((elt[1],elt[0])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[1]][0])/2, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[1]][1])/2, 
                                             (rawdata.elements[0].data[elt[0]][2]+rawdata.elements[0].data[elt[1]][2])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 
                    if tuple((elt[1],elt[2])) in Paths[face][face_loc] or tuple((elt[2],elt[1])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[1]][0]+rawdata.elements[0].data[elt[2]][0])/2, 
                                             (rawdata.elements[0].data[elt[1]][1]+rawdata.elements[0].data[elt[2]][1])/2, 
                                             (rawdata.elements[0].data[elt[1]][2]+rawdata.elements[0].data[elt[2]][2])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 

                    if tuple((elt[0],elt[2])) in Paths[face][face_loc] or tuple((elt[2],elt[0])) in Paths[face][face_loc]:
                        vertex.append(tuple(((rawdata.elements[0].data[elt[0]][0]+rawdata.elements[0].data[elt[2]][0])/2, 
                                             (rawdata.elements[0].data[elt[0]][1]+rawdata.elements[0].data[elt[2]][1])/2, 
                                             (rawdata.elements[0].data[elt[0]][2]+rawdata.elements[0].data[elt[2]][2])/2,
                                             255,
                                             0,
                                             255,
                                             0,
                                             counter)))
                        counter += 1

                        faces.append(tuple((tuple((int(counter -3-help_counter),int(counter -2-help_counter),int(counter -1))),
                                                255,
                                                0,
                                                255,
                                                255)))
                        help_counter += 1 
                
                
    vertex_data = np.array(vertex, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
            
    faces_data = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face = PlyElement.describe(faces_data, 'face')
    el_vertex = PlyElement.describe(vertex_data, 'vertex')
    PlyData([el_vertex, el_face], text=True).write(target_crit)  # , text=False, byte_order='<'
    
    time_eff1 = timeit.default_timer() -start_eff1
    print('Time writing critical cells in file:', time_eff1)  

    start_eff2 = timeit.default_timer()

    vertex_raw = []
    faces_raw = []
    
    for ind in range(len(rawdata.elements[0].data)):
        vertex_raw.append(tuple((rawdata.elements[0].data[ind][0], 
                             rawdata.elements[0].data[ind][1], 
                             rawdata.elements[0].data[ind][2],
                             0,
                             0, 
                             0,
                             0,
                             rawdata.elements[0].data[ind][2])))
        
    for key, value in new_vertices.items():
        if key not in C[2].keys() and key not in C[1].keys():
            vertex_raw.append(tuple((value[1][0],
                                     value[1][1],
                                     value[1][2],
                                     0,
                                     0,
                                     0,
                                     255,
                                     0.0)))
        elif key in C[2].keys():
            vertex_raw.append(tuple((value[1][0],
                                     value[1][1],
                                     value[1][2],
                                     0,
                                     0,
                                     255,
                                     255,
                                     0.0)))
        elif key in C[1].keys():
            vertex_raw.append(tuple((value[1][0],
                                     value[1][1],
                                     value[1][2],
                                     0,
                                     255,
                                     0,
                                     255,
                                     0.0)))
    
    vertex_data_raw = np.array(vertex_raw, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
    
    for ind in range(len(rawdata.elements[1].data)):
        if tuple((rawdata.elements[1].data[ind][0])) in replaced_faces:
            continue
        else:
            faces_raw.append(tuple((rawdata.elements[1].data[ind][0],
                                255,
                                255,
                                255,
                                0)))
    for face in new_faces:
        faces_raw.append(tuple((face,
                                255,
                                255,
                                255,
                                255)))
            
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







####### plot just critical cells


def write_crit_and_base_files(C, rawdata, target_base, target_crit, target_crit_pts):
    start_eff1 = timeit.default_timer()

    vertex = []
    faces = []
    counter = 0
    for ind in range(len(rawdata.elements[0].data)):
        if ind in C[0].keys():
            for i in range(3):
                vertex.append(tuple((rawdata.elements[0].data[ind][0], 
                                     rawdata.elements[0].data[ind][1], 
                                     rawdata.elements[0].data[ind][2],
                                     255,
                                     0,
                                     0,
                                     255,
                                     counter)))
                counter += 1
            
            faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                 255, 
                                 0, 
                                 0, 
                                 255)))
            
    
    vertex_data = np.array(vertex, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
            
    faces_data = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face = PlyElement.describe(faces_data, 'face')
    el_vertex = PlyElement.describe(vertex_data, 'vertex')
    PlyData([el_vertex, el_face], text=True).write(target_crit_pts)  # , text=False, byte_order='<'
    
    
    
    vertex = []
    faces = []
    counter = 0
    for ind in range(len(rawdata.elements[0].data)):
        if ind in C[0].keys():
            for i in range(3):
                vertex.append(tuple((rawdata.elements[0].data[ind][0], 
                                     rawdata.elements[0].data[ind][1], 
                                     rawdata.elements[0].data[ind][2],
                                     255,
                                     0,
                                     0,
                                     255,
                                     counter)))
                counter += 1
            
            faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                                 255, 
                                 0, 
                                 0, 
                                 255)))
            
    for edge in C[1].keys():
        vertex.append(tuple((rawdata.elements[0].data[edge[0]][0], 
                             rawdata.elements[0].data[edge[0]][1], 
                             rawdata.elements[0].data[edge[0]][2],
                             0,
                             255,
                             0,
                             0,
                             counter)))
        counter += 1
        
        for i in range(2):
            vertex.append(tuple((rawdata.elements[0].data[edge[1]][0], 
                                 rawdata.elements[0].data[edge[1]][1], 
                                 rawdata.elements[0].data[edge[1]][2],
                                 0,
                                 255,
                                 0,
                                 0,
                                 counter)))
            counter += 1
        
        faces.append(tuple((tuple((int(counter -3),int(counter -2),int(counter -1))),
                            0,
                            255,
                            0,
                            255)))
    
    vertex_data = np.array(vertex, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
            
    faces_data = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                        ('red', 'u1'),
                                        ('green', 'u1'),
                                        ('blue', 'u1'),
                                        ('alpha', 'u1')])
    
    el_face = PlyElement.describe(faces_data, 'face')
    el_vertex = PlyElement.describe(vertex_data, 'vertex')
    PlyData([el_vertex, el_face], text=True).write(target_crit)  # , text=False, byte_order='<'
    
    time_eff1 = timeit.default_timer() -start_eff1
    print('Time writing critical cells in file:', time_eff1)  

    start_eff2 = timeit.default_timer()

    vertex_raw = []
    faces_raw = []
    
    for ind in range(len(rawdata.elements[0].data)):
        vertex_raw.append(tuple((rawdata.elements[0].data[ind][0], 
                             rawdata.elements[0].data[ind][1], 
                             rawdata.elements[0].data[ind][2],
                             0,
                             0, 
                             0,
                             0,
                             rawdata.elements[0].data[ind][2])))
    
    vertex_data_raw = np.array(vertex_raw, dtype=[('x', 'f4'),
                                      ('y', 'f4'),
                                      ('z', 'f4'),
                                      ('red', 'u1'),
                                      ('green', 'u1'),
                                      ('blue', 'u1'),
                                      ('alpha', 'u1'),
                                      ('quality', 'f4')])
    
    for ind in range(len(rawdata.elements[1].data)):
        if tuple((rawdata.elements[1].data[ind][0])) in C[2].keys():
            faces_raw.append(tuple((rawdata.elements[1].data[ind][0],
                                0,
                                0,
                                255,
                                255)))
        else:
            faces_raw.append(tuple((rawdata.elements[1].data[ind][0],
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
