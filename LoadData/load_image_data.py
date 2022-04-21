import numpy as np
import timeit
from collections import Counter, deque 
import copy
import matplotlib.pyplot as plt

from PIL import Image

def get_height(cell, vertex_list):
    # gives height array of cell. 
    # if vertex is ordered, than the height will be ordered as well
    height = []
    for ind in cell:
        height.append(vertex_list[ind])
    return tuple(sorted(height,reverse=True))

def load_data(path):
    start_eff = timeit.default_timer()
    
    image = Image.open(path).convert('L')
    #since gray: all 3 channels equal
    image = np.array(image)
    
    data = {}
    data['vertex'] = {}
    data['star'] = {}

    m_,n_ = image.shape
    
    # need uneven dimensions
    if m_%2 == 0:
        image = image[:m_-1,:]
    if n_%2 == 0:
        image = image[:,:n_-1]


    m,n = image.shape
    
    count = 0
    for i in range(m):
        for j in range(n):
            if i%2 == 0  and j%2 == 0:
                data['vertex'][int(count)] = image[i,j]
                data['star'][int(count)] = {}
                count +=  1
                #data['star'][int(count)]['edges'] = []
                #data['star'][int(count)]['faces'] = []
                
                
                
    
    # make heights unique
    uni = timeit.default_timer()
    counts = Counter(data['vertex'].values())
    for key, value in data['vertex'].items():
        if counts[value] > 1:
            data['vertex'][key] = value + (counts[value] - 1) * 0.0000001
            counts[value] = counts[value] - 1
    time_uni = timeit.default_timer() - uni
    print('Time for unique heights:', time_uni)
    
    
    # need to reduce to only vertex dimension
    m,n = (m+1)/2,(n+1)/2

    xx, yy = np.meshgrid(np.arange(m),np.arange(n))
    indices = np.vstack((xx.T.flatten(),yy.T.flatten())).T
    ind_list = [tuple((indices[i])) for i in range(len(indices))]
    ind_dict = dict(enumerate(ind_list))
    
    xy_dict = {value:key for key, value in ind_dict.items()}
    
    edfa_ti = timeit.default_timer()
    # add faces and edges
    for ind in data['vertex'].keys():
        
        x,y = ind_dict[ind]

        if y < n-1:
            x1 = xy_dict[tuple((x,y+1))]
            data['star'][ind].update({tuple((ind,x1)): tuple((get_height(tuple((ind,x1)),data['vertex'])))})
            data['star'][x1].update({tuple((ind,x1)): tuple((get_height(tuple((ind,x1)),data['vertex'])))})
            
        if x < m-1:
            y1 = xy_dict[tuple((x+1,y))]
            data['star'][ind].update({tuple((ind,y1)): tuple((get_height(tuple((ind,y1)),data['vertex'])))})
            data['star'][y1].update({tuple((ind,y1)): tuple((get_height(tuple((ind,y1)),data['vertex'])))})
            
        if y < n-1 and x < m-1:
            x1y1 = xy_dict[tuple((x+1,y+1))]
            data['star'][ind].update({tuple((ind,x1,y1,x1y1)): tuple((get_height(tuple((ind,x1,y1,x1y1)),data['vertex'])))})
            data['star'][x1].update({tuple((ind,x1,y1,x1y1)): tuple((get_height(tuple((ind,x1,y1,x1y1)),data['vertex'])))})
            data['star'][y1].update({tuple((ind,x1,y1,x1y1)): tuple((get_height(tuple((ind,x1,y1,x1y1)),data['vertex'])))})
            data['star'][x1y1].update({tuple((ind,x1,y1,x1y1)): tuple((get_height(tuple((ind,x1,y1,x1y1)),data['vertex'])))})
    
    time_edfa = timeit.default_timer() - edfa_ti
    print('Time loading edges and faces with heights:',time_edfa)
        
    time_eff = timeit.default_timer() - start_eff
    print('Time load data eff total:', time_eff)
    
    return image, data