import numpy as np
import timeit
from collections import Counter, deque

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def GetSeparatrices(Paths, Facelist, N):
    start_eff2 = timeit.default_timer()
    
    times = []
    times_2=[]
    times_3=[]
    for key in Paths.keys():
        st = timeit.default_timer()
        if np.array(key).shape == (N,):
            st3 = timeit.default_timer()
            G = {}
            G[key] = []
            for pos, elt in enumerate(Paths[key]):
                G[elt] = []

                if np.array(elt).shape == (N,):
                    
                    # treat cubical complexes here: 
                    # they have 4 boundaries to be checked
                    if N == 4:
                        # first boundary
                        if tuple((elt[0],elt[1])) in Paths[key]:
                            if Paths[key].index(tuple((elt[0],elt[1]))) > pos:
                                G[elt].append(tuple((elt[0],elt[1])))
                            elif Paths[key].index(tuple((elt[0],elt[1]))) < pos:
                                G[tuple((elt[0],elt[1]))].append(elt)

                        elif tuple((elt[1],elt[0])) in Paths[key]:
                            if Paths[key].index(tuple((elt[1],elt[0]))) > pos:
                                G[elt].append(tuple((elt[1],elt[0])))
                            elif Paths[key].index(tuple((elt[1],elt[0]))) < pos:
                                G[tuple((elt[1],elt[0]))].append(elt)

                        # second boundary
                        if tuple((elt[0],elt[2])) in Paths[key]:
                            if Paths[key].index(tuple((elt[0],elt[2]))) > pos:
                                G[elt].append(tuple((elt[0],elt[2])))
                            elif Paths[key].index(tuple((elt[0],elt[2]))) < pos:
                                G[tuple((elt[0],elt[2]))].append(elt)

                        elif tuple((elt[2],elt[0])) in Paths[key]:
                            if Paths[key].index(tuple((elt[2],elt[0]))) > pos:
                                G[elt].append(tuple((elt[2],elt[0])))
                            elif Paths[key].index(tuple((elt[2],elt[0]))) < pos:
                                G[tuple((elt[2],elt[0]))].append(elt)

                        # third boundary
                        if tuple((elt[2],elt[3])) in Paths[key]:
                            if Paths[key].index(tuple((elt[2],elt[3]))) > pos:
                                G[elt].append(tuple((elt[2],elt[3])))
                            elif Paths[key].index(tuple((elt[2],elt[3]))) < pos:
                                G[tuple((elt[2],elt[3]))].append(elt)

                        elif tuple((elt[3],elt[2])) in Paths[key]:
                            if Paths[key].index(tuple((elt[3],elt[2]))) > pos:
                                G[elt].append(tuple((elt[3],elt[2])))
                            elif Paths[key].index(tuple((elt[3],elt[2]))) < pos:
                                G[tuple((elt[3],elt[2]))].append(elt)

                        # forth boundary
                        if tuple((elt[1],elt[3])) in Paths[key]:
                            if Paths[key].index(tuple((elt[1],elt[3]))) > pos:
                                G[elt].append(tuple((elt[1],elt[3])))
                            elif Paths[key].index(tuple((elt[1],elt[3]))) < pos:
                                G[tuple((elt[1],elt[3]))].append(elt)

                        elif tuple((elt[3],elt[1])) in Paths[key]:
                            if Paths[key].index(tuple((elt[3],elt[1]))) > pos:
                                G[elt].append(tuple((elt[3],elt[1])))
                            elif Paths[key].index(tuple((elt[3],elt[1]))) < pos:
                                G[tuple((elt[3],elt[1]))].append(elt)
                    
                    # treat simplicial complexes now
                    # need to check only 3 boundaries now
                    if N == 3:
                        # first boundary
                        if tuple((elt[0],elt[1])) in Paths[key]:
                            if Paths[key].index(tuple((elt[0],elt[1]))) > pos:
                                G[elt].append(tuple((elt[0],elt[1])))
                            elif Paths[key].index(tuple((elt[0],elt[1]))) < pos:
                                G[tuple((elt[0],elt[1]))].append(elt)

                        elif tuple((elt[1],elt[0])) in Paths[key]:
                            if Paths[key].index(tuple((elt[1],elt[0]))) > pos:
                                G[elt].append(tuple((elt[1],elt[0])))
                            elif Paths[key].index(tuple((elt[1],elt[0]))) < pos:
                                G[tuple((elt[1],elt[0]))].append(elt)

                        # second boundary
                        if tuple((elt[0],elt[2])) in Paths[key]:
                            if Paths[key].index(tuple((elt[0],elt[2]))) > pos:
                                G[elt].append(tuple((elt[0],elt[2])))
                            elif Paths[key].index(tuple((elt[0],elt[2]))) < pos:
                                G[tuple((elt[0],elt[2]))].append(elt)

                        elif tuple((elt[2],elt[0])) in Paths[key]:
                            if Paths[key].index(tuple((elt[2],elt[0]))) > pos:
                                G[elt].append(tuple((elt[2],elt[0])))
                            elif Paths[key].index(tuple((elt[2],elt[0]))) < pos:
                                G[tuple((elt[2],elt[0]))].append(elt)

                        # third boundary
                        if tuple((elt[2],elt[1])) in Paths[key]:
                            if Paths[key].index(tuple((elt[2],elt[1]))) > pos:
                                G[elt].append(tuple((elt[2],elt[1])))
                            elif Paths[key].index(tuple((elt[2],elt[1]))) < pos:
                                G[tuple((elt[2],elt[1]))].append(elt)

                        elif tuple((elt[1],elt[2])) in Paths[key]:
                            if Paths[key].index(tuple((elt[1],elt[2]))) > pos:
                                G[elt].append(tuple((elt[1],elt[2])))
                            elif Paths[key].index(tuple((elt[1],elt[2]))) < pos:
                                G[tuple((elt[1],elt[2]))].append(elt)

                        

                if np.array(elt).shape == (2,) and set(elt).issubset(key):
                    G[key].append(elt)
                    
                    
            Paths[key] = {}
            for face,value in Counter(Facelist[key]).keys():
                Paths[key][face] = find_all_paths(G,key,face)[0]
            end3 = timeit.default_timer() -st3
            times_3.append(end3)
        
        if np.array(key).shape == (2,):
            st2 = timeit.default_timer()
            pathlist = Paths[key]
            Paths[key] = {}
            for faceval, nb in Counter(Facelist[key]).items():
                face, value = faceval
                
                if nb == 1:
                    
                    # not sure why distinction btw cubical and simplicial is needed, but doesnt work otherwise: error is:
                    # always where pathlist.index(..) this code works fine for cubical, but with simplicial we get error 
                    # unless we put it as a tuple (face,) into .. so .index((face,)) (face is only an integer)
                    if N == 4:
                        if pathlist.index(face) == len(pathlist)-1:
                            if pathlist.index(key[0]) < pathlist.index(key[1]):
                                Paths[key][face] = [key] + pathlist[pathlist.index(key[1]):]
                            elif pathlist.index(key[1]) < pathlist.index(key[0]):
                                Paths[key][face] = [key] + pathlist[pathlist.index(key[0]):]
                        else:
                            Paths[key][face] = [key] + pathlist[:pathlist.index(face)+1]
                            
                    if N == 3:
                        if pathlist.index((face,)) == len(pathlist)-1:
                            if pathlist.index((key[0],)) < pathlist.index((key[1],)):
                                Paths[key][face] = [key] + pathlist[pathlist.index((key[1],)):]
                            elif pathlist.index((key[1],)) < pathlist.index((key[0],)):
                                Paths[key][face] = [key] + pathlist[pathlist.index((key[0],)):]
                        else:
                            Paths[key][face] = [key] + pathlist[:pathlist.index((face,))+1]
                        
                elif nb == 2:
                    Paths[key][face] = [key] + pathlist
                    
                end2 = timeit.default_timer() -st2
                times_2.append(end2)
                    
        end = timeit.default_timer() -st
        times.append(end)
    
    print("Loop statistics")
    print("Nb of iterations: ", len(times))
    print("Average: ", sum(times)/len(times))
    print("Max: ", max(times))
    print("Total time: ", sum(times))
    
    print("2-1 paths")
    print("Nb of iterations: ", len(times_2))
    print("Average: ", sum(times_2)/len(times_2))
    print("Max: ", max(times_2))
    print("Total time: ", sum(times_2))
    
    print("3-2 paths")
    print("Nb of iterations: ", len(times_3))
    print("Average: ", sum(times_3)/len(times_3))
    print("Max: ", max(times_3))
    print("Total time: ", sum(times_3))
            
    time_eff2 = timeit.default_timer() -start_eff2
    print('Time getting separatrices:', time_eff2)  