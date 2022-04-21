import numpy as np
import matplotlib.pyplot as plt

from PIL import Image

def plot_criticals(C, image, point_size = 4, save_fig = False, save_path = None):
    
    m_,n_ = image.shape
    
    m,n = (m_+1)/2, (n_+1)/2
    
    xx, yy = np.meshgrid(np.arange(m),np.arange(n))
    indices = np.vstack((xx.T.flatten(),yy.T.flatten())).T
    ind_list = [tuple((indices[i])) for i in range(len(indices))]
    ind_dict = dict(enumerate(ind_list))
    
    x0 = []
    y0 = []
    for key in C[0].keys():
        x0.append(ind_dict[key][0]*2)
        y0.append(ind_dict[key][1]*2)
        
    x1 = []
    y1 = []
    for key in C[1].keys():
        x1.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2)/2)
        y1.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2)/2)
        
    x2 = []
    y2 = []
    for key in C[2].keys():
        x2.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2+ind_dict[key[2]][0]*2+ind_dict[key[3]][0]*2)/4)
        y2.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2+ind_dict[key[2]][1]*2+ind_dict[key[3]][1]*2)/4)
    
    plt.imshow(image,cmap='gray')
    plt.scatter(y0,x0,s=point_size, color = 'red')
    plt.scatter(y1,x1,s=point_size, color = 'limegreen')
    plt.scatter(y2,x2,s=point_size, color = 'blue')
    plt.title('Plot image with critical points')
    if save_fig:
        plt.savefig(save_path)
        
        
        
def plot_criticals_with_Paths(C, Paths, image, point_size = 4, line_width = 0.5, save_fig = False, save_path = None):
    
    m_,n_ = image.shape
    
    m,n = (m_+1)/2, (n_+1)/2
    
    xx, yy = np.meshgrid(np.arange(m),np.arange(n))
    indices = np.vstack((xx.T.flatten(),yy.T.flatten())).T
    ind_list = [tuple((indices[i])) for i in range(len(indices))]
    ind_dict = dict(enumerate(ind_list))
    
    x0 = []
    y0 = []
    for key in C[0].keys():
        x0.append(ind_dict[key][0]*2)
        y0.append(ind_dict[key][1]*2)
        
    x1 = []
    y1 = []
    lines = {}
    for key in C[1].keys():
        x1.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2)/2)
        y1.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2)/2)
        lines[key] = {}
        for face in Paths[key].keys():
            lines[key][face] = []
            for elt in Paths[key][face]:
                if np.array(elt).shape == (2,):
                    lines[key][face].append([(ind_dict[elt[0]][0]*2+ind_dict[elt[1]][0]*2)/2 , (ind_dict[elt[0]][1]*2+ind_dict[elt[1]][1]*2)/2])
                else:
                    lines[key][face].append([ind_dict[elt][0]*2, ind_dict[elt][1]*2])
            
    x2 = []
    y2 = []
    for key in C[2].keys():
        x2.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2+ind_dict[key[2]][0]*2+ind_dict[key[3]][0]*2)/4)
        y2.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2+ind_dict[key[2]][1]*2+ind_dict[key[3]][1]*2)/4)
        lines[key] = {}
        for face in Paths[key].keys():
            lines[key][face] = []
            for elt in Paths[key][face]:
                if np.array(elt).shape == (2,):
                    lines[key][face].append([(ind_dict[elt[0]][0]*2+ind_dict[elt[1]][0]*2)/2 , (ind_dict[elt[0]][1]*2+ind_dict[elt[1]][1]*2)/2])
                else:
                    lines[key][face].append([(ind_dict[elt[0]][0]*2+ind_dict[elt[1]][0]*2+ind_dict[elt[2]][0]*2+ind_dict[elt[3]][0]*2)/4, (ind_dict[elt[0]][1]*2+ind_dict[elt[1]][1]*2+ind_dict[elt[2]][1]*2+ind_dict[elt[3]][1]*2)/4])
            
            
    plt.imshow(image,cmap='gray')
    for key in lines.keys():
        for face in lines[key].keys():
            x_vals = []
            y_vals = []
            for i in range(len(lines[key][face])):
                x_vals.append(lines[key][face][i][0])
                y_vals.append(lines[key][face][i][1])
            plt.plot(y_vals,x_vals, color = 'm', linewidth = line_width)
                
    plt.scatter(y0,x0,s=point_size, color = 'red', zorder = 3)
    plt.scatter(y1,x1,s=point_size, color = 'limegreen', zorder = 3)
    plt.scatter(y2,x2,s=point_size, color = 'blue', zorder = 3)
    plt.title('Plot image with critical points and Paths connecting them')
    if save_fig:
        plt.savefig(save_path)
        
        
def plot_criticals_with_gradient_vectors(C, V, image, point_size = 4, line_width = 0.5, save_fig = False, save_path = None):
    
    m_,n_ = image.shape
    
    m,n = (m_+1)/2, (n_+1)/2
    
    xx, yy = np.meshgrid(np.arange(m),np.arange(n))
    indices = np.vstack((xx.T.flatten(),yy.T.flatten())).T
    ind_list = [tuple((indices[i])) for i in range(len(indices))]
    ind_dict = dict(enumerate(ind_list))
    
    x0 = []
    y0 = []
    for key in C[0].keys():
        x0.append(ind_dict[key][0]*2)
        y0.append(ind_dict[key][1]*2)
        
    x1 = []
    y1 = []
    for key in C[1].keys():
        x1.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2)/2)
        y1.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2)/2)
        
            
    x2 = []
    y2 = []
    for key in C[2].keys():
        x2.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2+ind_dict[key[2]][0]*2+ind_dict[key[3]][0]*2)/4)
        y2.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2+ind_dict[key[2]][1]*2+ind_dict[key[3]][1]*2)/4)
        
    lines = []
    for key, value in V.items():
        if np.array(key).shape == ():
            x_key = ind_dict[key][0]*2
            y_key = ind_dict[key][1]*2
            x_value = (ind_dict[value[0]][0]*2+ind_dict[value[1]][0]*2)/2
            y_value = (ind_dict[value[0]][1]*2+ind_dict[value[1]][1]*2)/2
            lines.append(((x_key,y_key),(x_value,y_value),'r'))
            
        elif np.array(key).shape == (2,) and np.array(value).shape == (4,):
            x_key = (ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2)/2
            y_key = (ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2)/2
            x_value = (ind_dict[value[0]][0]*2+ind_dict[value[1]][0]*2+ind_dict[value[2]][0]*2+ind_dict[value[3]][0]*2)/4
            y_value = (ind_dict[value[0]][1]*2+ind_dict[value[1]][1]*2+ind_dict[value[2]][1]*2+ind_dict[value[3]][1]*2)/4
            lines.append(((x_key,y_key),(x_value,y_value),'b'))
            
        elif np.array(key).shape == (2,) and np.array(value).shape == ():
            x_key = (ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2)/2
            y_key = (ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2)/2
            x_value = ind_dict[value][0]*2
            y_value = ind_dict[value][1]*2
            lines.append(((x_key,y_key),(x_value,y_value),'m'))
            
        elif np.array(key).shape == (4,):
            x_value = (ind_dict[value[0]][0]*2+ind_dict[value[1]][0]*2)/2
            y_value = (ind_dict[value[0]][1]*2+ind_dict[value[1]][1]*2)/2
            x_key = (ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2+ind_dict[key[2]][0]*2+ind_dict[key[3]][0]*2)/4
            y_key = (ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2+ind_dict[key[2]][1]*2+ind_dict[key[3]][1]*2)/4
            lines.append(((x_key,y_key),(x_value,y_value),'g'))
            
    
    plt.imshow(image,cmap='gray')
    
    for xy, xxyy, c in lines:
        x_vals = [xy[0], xxyy[0]]
        y_vals = [xy[1], xxyy[1]]
        plt.arrow(xy[1],xy[0],xxyy[1]-xy[1], xxyy[0]-xy[0], color = c, width = line_width, head_width= 3*line_width, head_length= 1.5*3*line_width)
                
    plt.scatter(y0,x0,s=point_size, color = 'red', zorder = 3)
    plt.scatter(y1,x1,s=point_size, color = 'limegreen', zorder = 3)
    plt.scatter(y2,x2,s=point_size, color = 'blue', zorder = 3)
    plt.title('Plot image with critical points and gradient vector arrows')
    if save_fig:
        plt.savefig(save_path)
        
        
        
def plot_criticals_with_gradient_vectors_MonoG(C, edges, image, point_size = 4, line_width = 0.5, save_fig = False, save_path = None):
    
    m_,n_ = image.shape
    
    m,n = (m_+1)/2, (n_+1)/2
    
    xx, yy = np.meshgrid(np.arange(m),np.arange(n))
    indices = np.vstack((xx.T.flatten(),yy.T.flatten())).T
    ind_list = [tuple((indices[i])) for i in range(len(indices))]
    ind_dict = dict(enumerate(ind_list))
    
    x0 = []
    y0 = []
    for key in C[0].keys():
        x0.append(ind_dict[key][0]*2)
        y0.append(ind_dict[key][1]*2)
        
    x1 = []
    y1 = []
    for key in C[1].keys():
        x1.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2)/2)
        y1.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2)/2)
        
            
    x2 = []
    y2 = []
    for key in C[2].keys():
        x2.append((ind_dict[key[0]][0]*2+ind_dict[key[1]][0]*2+ind_dict[key[2]][0]*2+ind_dict[key[3]][0]*2)/4)
        y2.append((ind_dict[key[0]][1]*2+ind_dict[key[1]][1]*2+ind_dict[key[2]][1]*2+ind_dict[key[3]][1]*2)/4)
        
    lines = []
    for pair in edges:
        end, start = pair
        
        lines.append((flatindex_to_2D_indices(start, image), flatindex_to_2D_indices(end, image), 'm'))
            
    
    plt.imshow(image,cmap='gray')
    
    for xy, xxyy, c in lines:
        x_vals = [xy[0], xxyy[0]]
        y_vals = [xy[1], xxyy[1]]
        if xxyy[1]-xy[1] < 0:
            plt.arrow(xy[1],xy[0],xxyy[1]-xy[1]+0.3, xxyy[0]-xy[0], color = c, width = line_width, head_width= 8*line_width, head_length= 1.5*8*line_width)
        elif xxyy[1]-xy[1] > 0:
            plt.arrow(xy[1],xy[0],xxyy[1]-xy[1]-0.3, xxyy[0]-xy[0], color = c, width = line_width, head_width= 8*line_width, head_length= 1.5*8*line_width)
        elif xxyy[0]-xy[0] < 0:
            plt.arrow(xy[1],xy[0],xxyy[1]-xy[1], xxyy[0]-xy[0]+0.3, color = c, width = line_width, head_width= 8*line_width, head_length= 1.5*8*line_width)
        elif xxyy[0]-xy[0] > 0:
            plt.arrow(xy[1],xy[0],xxyy[1]-xy[1], xxyy[0]-xy[0]-0.3, color = c, width = line_width, head_width= 8*line_width, head_length= 1.5*8*line_width)
    plt.scatter(y0,x0,s=point_size, color = 'red', zorder = 3)
    plt.scatter(y1,x1,s=point_size, color = 'limegreen', zorder = 3)
    plt.scatter(y2,x2,s=point_size, color = 'blue', zorder = 3)
    plt.title('Plot image with critical points and Monotonicity Graph visualization')
    if save_fig:
        plt.savefig(save_path)
        
        
def flatindex_to_2D_indices(flat, image):
    m,n = image.shape
    y = flat%m
    x = int((flat - y)/m)
    
    return (x,y)