import numpy as np
import timeit
from collections import Counter


def BettiViaPairCells(MorseComplex):
    start_eff = timeit.default_timer()
    
    partner0, partner1, partner2 = pair_cells(MorseComplex)

    betti = np.zeros(3)
    for cell in MorseComplex.CritVertices.keys():
        if np.array(partner0[cell]).size == 0:
            betti[0] += 1
    for cell in MorseComplex.CritEdges.keys():
        if np.array(partner1[cell]).size == 0:
            betti[1] += 1
    for cell in MorseComplex.CritFaces.keys():
        if np.array(partner2[cell]).size == 0:
            betti[2] += 1
    
    time_eff = timeit.default_timer() -start_eff
    print('Time Betti numbers:', time_eff)  
    return betti, partner0, partner1, partner2


def pair_cells(MorseComplex):
    
    partner0 = {}
    cascade0 = {}
    
    partner1 = {}
    cascade1 = {}
    dell_cascade1 = {}
    
    partner2 = {}
    cascade2 = {}
    dell_cascade2 = {}
    
    M = {}
    M[0] = {k: v for k, v in sorted(MorseComplex.CritVertices.items(), key=lambda item: item[1].fun_val)}
    M[1] = {k: v for k, v in sorted(MorseComplex.CritEdges.items(), key=lambda item: item[1].fun_val)}
    M[2] = {k: v for k, v in sorted(MorseComplex.CritFaces.items(), key=lambda item: item[1].fun_val)}
    
    for sigma in M[0].keys():
        partner0[sigma] = []
        cascade0[sigma] = [sigma]
        
    for sigma in M[1].keys():
        partner1[sigma] = []
        cascade1[sigma] = [sigma]
        dell_cascade1[sigma] = Dell()
        dell_cascade1[sigma].add(M[1][sigma], 1)
        
        eliminate_boundaries(sigma, cascade1, partner1, partner0, dell_cascade1, MorseComplex, 1)
            
        if dell_cascade1[sigma].nonzero():
            tau = dell_cascade1[sigma].youngest(MorseComplex, 1)

            partner0[tau] = sigma
            partner1[sigma] = tau
            
    for sigma in M[2].keys():
        partner2[sigma] = []
        cascade2[sigma] = [sigma]
        dell_cascade2[sigma] = Dell()
        dell_cascade2[sigma].add(M[2][sigma], 2)
        
        eliminate_boundaries(sigma, cascade2, partner2, partner1, dell_cascade2, MorseComplex, 2)
            
        if dell_cascade2[sigma].nonzero():
            tau = dell_cascade2[sigma].youngest(MorseComplex, 2)

            partner1[tau] = sigma
            partner2[sigma] = tau

    return partner0, partner1, partner2


class Dell:
    def __init__(self): 
        self.dell = set()
  
    # for checking if the dell is empty 
    def nonzero(self): 
        return len(self.dell) != 0
  
    # for adding an element to dell 
    def add(self, critElt, p):
        if p==1:
            for elt in critElt.connected_minima:
                if elt in self.dell:
                    self.dell.remove(elt)
                else:
                    self.dell.add(elt)
        elif p==2:
            for elt in critElt.connected_saddles:
                if elt in self.dell:
                    self.dell.remove(elt)
                else:
                    self.dell.add(elt)
        
    def copy(self, dell_set):
        for elt in dell_set:
            if elt in self.dell:
                self.dell.remove(elt)
            else:
                self.dell.add(elt)
        return self.dell
    
    def youngest(self, MorseComplex, p):
        if p==1:
            return sorted(self.dell, key=lambda item: MorseComplex.CritVertices[item].fun_val)[-1]
        elif p==2:
            return sorted(self.dell, key=lambda item: MorseComplex.CritEdges[item].fun_val)[-1]


def eliminate_boundaries(sigma, cascade, partner, partner_below, dell_cascade, MorseComplex, p):
    while dell_cascade[sigma].nonzero():
        tau = dell_cascade[sigma].youngest(MorseComplex, p)
        
        if not partner_below[tau]:
            return
        else:
            cascade[sigma] += cascade[partner_below[tau]]
            
            dell_cascade[sigma].copy(dell_cascade[partner_below[tau]].dell)


