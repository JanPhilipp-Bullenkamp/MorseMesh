from collections import Counter
import numpy as np
import timeit


def get_closest_extremum(crit_edge, vert_dict, face_dict):
    distances = []
    
    # first add distances to all maxima
    face_counter = Counter(crit_edge.connected_maxima)
    for face_ind, nb in face_counter.items():
        # cannot cancel loops, so only if there is a single path we can add the extremum
        if nb==1:
            # take absolute value btw the two highest vertices of edge and face respectively
            dist.append(tuple((conn, 2, abs(face_dict[conn].fun_val[0]-crit_edge.fun_val[0]))))
                               
    # now add distances to all minima
    vert_counter = Counter(crit_edge.connected_minima)
    for vert_ind, nb in vert_counter.items():
        # cannot cancel loops, so only if there is a single path we can add the extremum
        if nb==1:
            # take absolute value btw the highest vertex of edge and the value of the vertex
            dist.append(tuple((conn, 0, abs(crit_edge.fun_val[0]-vert_dict[conn].fun_val))))
    
    if sorted(dist, key=lambda item: item[2]):
        closest, dim, dist = sorted(dist, key=lambda item: item[2])[0] 
        return closest, dim, dist
    else: 
        return None

def CancelCriticalPairs(MorseComplex, threshold):
    start_eff = timeit.default_timer()

    CancelPairs = CancellationQueue()
    
    # fill queue
    for crit_edge in MorseComplex.CritEdges.values():
        closest_extremum = get_closest_extremum(crit_edge, MorseComplex.CritVertices, MorseComplex.CritFaces)
        if closest_extremum != None:
            index, dim, dist = closest_extremum
            if dist < threshold:
                CancelPairs.insert(tuple((dist, crit_edge)))
    
    # work down queue
    while CancelPairs.notEmpty():
        prio, saddle = CancelPairs.pop_front()
        check = get_closest_extremum(MorseComplex.CritEdges[saddle], MorseComplex.CritVertices, MorseComplex.CritFaces)
        if check != None:
            closest, dim, dist = check
            if dist <= CancelPairs.check_distance():
                cancel_one_critical_pair(saddle, closest, dim)
            else:
                CancelPairs.insert(tuple((dist,saddle)))

    time_eff = timeit.default_timer() - start_eff
    print('Time cancel critical points:', time_eff)

def _cancel_one_critical_pair(saddle, extremum, dim, MorseComplex):
    
    # Case: saddle to minimum path should be cancelled:
    #     1. remove saddle from all maxima connections and delete paths
    #     2. invert path btw old min and saddle
    #     3. reconnnect saddles from old min to min from old saddle by path adding
    if dim == 0:
        minimum = MorseComplex.CritVertices[extremum]
        # 1. remove saddle from all maxima connections and delete paths
        for max_conn in saddle.connected_maxima:
            MorseComplex.CritFaces[max_conn].connected_saddles.remove(saddle.index)
            MorseComplex.CritFaces[max_conn].paths.pop(saddle.index)
        

    if np.array(extremum).shape == ():

        new_saddles = []
        for elt in self.min_conn[extremum]:
            if elt != saddle:
                new_saddles.append(elt)
            '''
            ERROR JUST FOR 3D DATASET!!!!!!!!!!!!!!!!!
            not sure where the error is, but 

            self.saddle_conn[elt].remove(extremum)

            produces the any all error although extremum is a tuple, the following implementation is quite bad compared 
            to just the remove 

            Same happens for the (N,) case 
            '''
            for index, sad_list_tup in enumerate(self.saddle_conn[elt]):
                if np.array(sad_list_tup).shape == ():
                    if sad_list_tup == extremum:
                        self.saddle_conn[elt].pop(index)     
            for index, sad_tuple in enumerate(self.Facelist[elt]):
                if np.array(sad_tuple[0]).shape == ():
                    if sad_tuple[0] == extremum:
                        self.Facelist[elt].pop(index)            

        new_min = []
        for elt in self.saddle_conn[saddle]:
            if np.array(elt).shape == ():
                if elt != extremum:
                    new_min.append(elt)
                self.min_conn[elt].remove(saddle)
                for index, min_tuple in enumerate(self.Facelist[saddle]):
                    if np.array(min_tuple[0]).shape == ():
                        if min_tuple[0] == elt:
                            self.Facelist[saddle].pop(index)     
            # delete connections from saddle to 2-cells
            elif np.array(elt).shape == (self.N,):
                self.max_conn[elt].remove(saddle)
                self.Paths[elt].pop(saddle,None)
                for index, sad_tuple in enumerate(self.Facelist[elt]):
                    if np.array(sad_tuple[0]).shape == (2,):
                        if sad_tuple[0][0] == saddle[0] and sad_tuple[0][1] == saddle[1]:
                            self.Facelist[elt].pop(index)

        # change the V field new V (needs to be done before the paths are changed
        self._change_V_field(extremum, saddle)

        # reconnect saddles and minima via cancelled path
        for sad in new_saddles:
            for mini in new_min:
                self.min_conn[mini].append(sad)
                self.saddle_conn[sad].append(mini)
                self._update_paths(extremum, saddle, mini, sad)
                self.Facelist[sad].append(tuple((mini,self.C[0][mini])))


        for sad in new_saddles:
            self.Paths[sad].pop(extremum,None)

        # delete saddle and extremum from the conn lists
        self.min_conn.pop(extremum)
        self.saddle_conn.pop(saddle)
        self.C[0].pop(extremum)
        self.C[1].pop(saddle)
        self.Paths.pop(saddle)
        self.Facelist.pop(saddle)



    elif np.array(extremum).shape == (self.N,):

        new_saddles = []
        for elt in self.max_conn[extremum]:
            if elt != saddle:
                new_saddles.append(elt)
            '''
            ERROR JUST FOR 3D DATASET!!!!!!!!!!!!!!!!!
            not sure where the error is, but 

            self.saddle_conn[elt].remove(extremum)

            produces the any all error although extremum is a tuple, the following implementation is quite bad compared 
            to just the remove 
            '''
            for index, sad_list_tup in enumerate(self.saddle_conn[elt]):
                if np.array(sad_list_tup).shape == (self.N,):
                    if sad_list_tup[0] == extremum[0] and sad_list_tup[1] == extremum[1] and sad_list_tup[2] == extremum[2]:
                        self.saddle_conn[elt].pop(index)

        new_max = []
        for elt in self.saddle_conn[saddle]:
            if np.array(elt).shape == (self.N,):
                if elt != extremum:
                    new_max.append(elt)
                self.max_conn[elt].remove(saddle)
                '''
                !!! same problem as above!!!!!
                '''
                for index, sad_tuple in enumerate(self.Facelist[elt]):
                    if np.array(sad_tuple[0]).shape == (2,):
                        if sad_tuple[0][0] == saddle[0] and sad_tuple[0][1] == saddle[1]:
                            self.Facelist[elt].pop(index)
            # delete connections from saddle to 0-cells
            elif np.array(elt).shape == ():
                self.min_conn[elt].remove(saddle)

        # change the V field new V (needs to be done before the paths are changed
        self._change_V_field(extremum, saddle)

        # reconnect saddles and minima via cancelled path
        for sad in new_saddles:
            for maxi in new_max:
                self.max_conn[maxi].append(sad)
                self.saddle_conn[sad].append(maxi)
                self._update_paths(extremum, saddle, maxi, sad)
                self.Facelist[maxi].append(tuple((sad,self.C[1][sad])))

        for maxi in new_max:
            self.Paths[maxi].pop(saddle)


        # delete saddle and extremum from the conn lists
        self.max_conn.pop(extremum)
        self.saddle_conn.pop(saddle)
        self.C[2].pop(extremum)
        self.C[1].pop(saddle)
        self.Paths.pop(extremum)
        self.Paths.pop(saddle)
        self.Facelist.pop(extremum)
        self.Facelist.pop(saddle)


def _update_paths(self, extremum, saddle, new_extr, new_sad):
    if np.array(extremum).shape == (self.N,):
        path_to_saddle = self.Paths[new_extr][saddle]
        path_to_reverse = self.Paths[extremum][saddle]
        path_to_extremum = self.Paths[extremum][new_sad]

        combined_path = path_to_saddle + path_to_reverse[::-1][1:-1] + path_to_extremum

        self.Paths[new_extr][new_sad] = combined_path



    elif np.array(extremum).shape == ():
        path_to_extremum = self.Paths[new_sad][extremum]
        path_to_reverse = self.Paths[saddle][extremum]
        path_to_saddle = self.Paths[saddle][new_extr]

        combined_path = path_to_extremum + path_to_reverse[::-1][1:-1] + path_to_saddle

        self.Paths[new_sad][new_extr] = combined_path


def _change_V_field(self, extremum, saddle):
    if np.array(extremum).shape == (self.N,):
        path = self.Paths[extremum][saddle][::-1]
        for position, cell in enumerate(self.Paths[extremum][saddle][::-1]):
            if np.array(cell).shape == (2,):
                self.newV[cell] = path[position+1]

                '''
                maybe needs to be changed: issue if path splits  might occur, 
                as the order is not necessarily right in that case
                '''

    elif np.array(extremum).shape == ():
        path = self.Paths[saddle][extremum][::-1]
        for position, cell in enumerate(self.Paths[saddle][extremum][::-1]):
            if np.array(cell).shape == ():
                self.newV[cell] = path[position+1]



def _get_highest_value(self,cell):
    if np.array(cell).shape == (self.N,) or np.array(cell).shape == (2,):
        return max(self.data['star'][cell[0]][cell])
    else:
        return self.data['vertex'][cell]


