import numpy as np
import timeit

def potential_cells(data, Cell_key, Cell_value, N):
    pot_alphas = {}
    for i in Cell_key:
        data['star'][i].update({tuple((i,)) : tuple((data['vertex'][i],))})
        for key, value in data['star'][i].items():
            
            # for cubical complexes do:
            if N == 4:
                if (len(key) == (len(Cell_key) - 2) and set(key).issubset(Cell_key)):
                    if len(key) == 1:
                        pot_alphas.update({key[0] : value[0]})
                    else:
                        pot_alphas.update({key : value})
                elif (len(key) == (len(Cell_key) - 1) and set(key).issubset(Cell_key)):
                    if len(key) == 1:
                        pot_alphas.update({key[0] : value[0]})
                        
            # for simplicial complexes do:
            elif N == 3:
                if (len(key) == (len(Cell_key) - 1) and set(key).issubset(Cell_key)):
                    if len(key) == 1:
                        pot_alphas.update({key[0] : value[0]})
                    else:
                        pot_alphas.update({key : value})
                
    return pot_alphas

def ExtractMorseComplex_old(data, C, V, N):
    start_eff = timeit.default_timer()

    Facelist = {}
    max_conn = {}
    saddle_conn = {}
    min_conn = {}
    Paths = {}
    for p in (0,1,2):
        Qbfs = []
        for C_key, C_value in C[p].items():
            if p > 0:
                Facelist[C_key] = []
                Paths[C_key] = []
                pot_alphas = potential_cells(data, C_key, C_value, N)

                for alpha_key, alpha_value in pot_alphas.items():
                    if alpha_key in V.keys():
                        Qbfs.append(tuple((alpha_key , alpha_value)))
                    elif alpha_key in C[p-1].keys():
                        #add to facelist
                        Facelist[C_key].append(tuple((alpha_key, alpha_value)))
                        # add to conn dictionaries
                        if np.array(C_key).shape == (2,):
                            if C_key not in saddle_conn.keys():
                                saddle_conn[C_key] = []
                            saddle_conn[C_key].append(alpha_key)
                            if alpha_key not in min_conn.keys():
                                min_conn[alpha_key] = []
                            min_conn[alpha_key].append(C_key)
                            
                        elif np.array(C_key).shape == (N,):
                            if C_key not in max_conn.keys():
                                max_conn[C_key] = []
                            max_conn[C_key].append(alpha_key)
                            if alpha_key not in saddle_conn.keys():
                                saddle_conn[alpha_key] = []
                            saddle_conn[alpha_key].append(C_key)
                        # add to Paths
                        Paths[C_key].append(alpha_key)
                        
                while len(Qbfs) != 0:
                    alpha_ind, alpha_height = Qbfs.pop(-1)
                    beta_ind, beta_height = V[alpha_ind]
                    Paths[C_key].append(alpha_ind)
                    Paths[C_key].append(beta_ind)
                    
                    pot_deltas = potential_cells(data, beta_ind, beta_height, N)

                    pot_deltas.pop(alpha_ind, None)

                    for delta_key, delta_value in pot_deltas.items():
                        if delta_key in C[p-1].keys():
                            # add to Facelist
                            Facelist[C_key].append(tuple((delta_key , delta_value)))
                            # add to conn dictionaries
                            if np.array(C_key).shape == (2,):
                                if C_key not in saddle_conn.keys():
                                    saddle_conn[C_key] = []
                                saddle_conn[C_key].append(delta_key)
                                if delta_key not in min_conn.keys():
                                    min_conn[delta_key] = []
                                min_conn[delta_key].append(C_key)

                            elif np.array(C_key).shape == (N,):
                                if C_key not in max_conn.keys():
                                    max_conn[C_key] = []
                                max_conn[C_key].append(delta_key)
                                if delta_key not in saddle_conn.keys():
                                    saddle_conn[delta_key] = []
                                saddle_conn[delta_key].append(C_key)
                            # add to Paths
                            Paths[C_key].append(delta_key)
                            
                        elif delta_key in V.keys():
                            Qbfs.append(tuple((delta_key , delta_value)))
                            
        
    time_eff = timeit.default_timer() -start_eff
    print('Time ExtractMorseComplex:', time_eff)  
    return Facelist, max_conn, saddle_conn, min_conn, Paths