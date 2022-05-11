import numpy as np
import timeit
from collections import Counter


def BettiViaPairCells(MorseComplex):
    start_eff = timeit.default_timer()
    
    partner = pair_cells(MorseComplex)

    betti = np.zeros(3)
    for p in range(3):
        for key in C[p].keys():
            if np.array(partner[key]).size == 0:
                betti[p] += 1
    
    time_eff = timeit.default_timer() -start_eff
    print('Time Betti numbers:', time_eff)  
    return betti, partner


def pair_cells(MorseComplex):
    
    partner = {}
    cascade = {}
    dell_cascade = {}
    
    M = {}
    M[0] = {k: v for k, v in sorted(MorseComplex.CritVertices.items(), key=lambda item: item[1].fun_val)}
    M[1] = {k: v for k, v in sorted(MorseComplex.CritEdges.items(), key=lambda item: item[1].fun_val)}
    M[2] = {k: v for k, v in sorted(MorseComplex.CritFaces.items(), key=lambda item: item[1].fun_val)}
    
    for sigma in M[0].keys():
        partner[sigma] = []
        cascade[sigma] = [sigma]
        
    for sigma in M[1].keys():
        partner[sigma] = []
        cascade[sigma] = [sigma]
        dell_cascade[sigma] = Dell()
        dell_cascade[sigma].add(M[1][sigma], MorseComplex, 1)
        
        eliminate_boundaries(sigma, cascade, partner, dell_cascade, MorseComplex, 1)
            
        if dell_cascade[sigma].nonzero():
            tau = dell_cascade[sigma].youngest()

            partner[tau] = sigma
            partner[sigma] = tau

    for p in range(3):
        for sigma in M[p].keys():
            
            partner[sigma] = []
            cascade[sigma] = [sigma]
            dell_cascade[sigma] = Dell()
            dell_cascade[sigma].add(M[p][sigma], MorseComplex, p)
            
            eliminate_boundaries(sigma, cascade, partner, dell_cascade, MorseComplex)
            
            if dell_cascade[sigma].nonzero():
                tau = dell_cascade[sigma].youngest()

                partner[tau] = sigma
                partner[sigma] = tau
                
    return partner


class Dell:
    def __init__(self): 
        self.dell0 = set()
        self.dell1 = set()
  
    # for checking if the dell is empty 
    def nonzero(self): 
        return (len(self.dell0) + len(self.dell1) + len(self.dell2)) != 0
  
    # for adding an element to dell 
    def add(self, critElt, MorseComplex, p):
        if p==1:
            for elt in critElt.connected_minima:
                if elt in self.dell0:
                    self.dell0.remove(MorseComplex.CritVertices[elt])
                else:
                    self.dell0.add(MorseComplex.CritVertices[elt])
        elif p==2:
            for elt in critElt.connected_saddles:
                if elt in self.dell1:
                    self.dell1.remove(MorseComplex.CritEdges[elt])
                else:
                    self.dell1.add(MorseComplex.CritEdges[elt])
        
    def copy(self, dell_list):
        for elt in dell_list:
            if elt in self.dell:
                self.dell.remove(elt)
            else:
                self.dell.add(tuple((elt)))
        return self.dell
    
    def youngest(self, p):
        if p==1:
            return sorted(self.dell0, key=lambda item: item.fun_val)[-1][0]
        elif p==2:
            return sorted(self.dell1, key=lambda item: item.fun_val)[-1][0]


def eliminate_boundaries(sigma, cascade, partner, dell_cascade, MorseComplex, p):
    while dell_cascade[sigma].nonzero():
        tau = dell_cascade[sigma].youngest(p).index
        
        if not partner[tau]:
            return
        else:
            cascade[sigma] += cascade[partner[tau]]
            
            dell_cascade[sigma].copy(dell_cascade[partner[tau]].dell)


