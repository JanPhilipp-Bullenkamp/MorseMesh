

def Segmentation_dual_thresh_edges():
    if persistence not in self.reducedMorseComplexes.keys():
        raise ValueError('No MorseComplex reduced to this persistence!')
    if not self.reducedMorseComplexes[persistence]._flag_MorseCells:
        raise ValueError('No MorseCell calculated for this persistence!')
    elif not self._flag_SalientEdge:
        print("Need maximally reduced complex for salient edges!")
        print("Computing maximally reduced complex ...")
        self.ReduceMorseComplex(self.range)

    if persistence not in self.SegmentationDual.keys():
        self.SegmentationDual[persistence] = {}

    if thresh_high not in self.SegmentationDual[persistence].keys():
        self.SegmentationDual[persistence][thresh_high] = {}

    if thresh_low not in self.SegmentationDual[persistence][thresh_high].keys():
        self.SegmentationDual[persistence][thresh_high][thresh_low] = {}

    if edge_percent in self.SegmentationDual[persistence][thresh_high][thresh_low].keys():
        print("Segmentation for these parameters has been calculated already: Persistence", persistence, ", SalientEdge Threshold",thresh_high, thresh_low, ", Edge Percentage", edge_percent)
    else:
        salient_edge_points = self.dual_thresh_edges(thresh_high, thresh_low)

        Cells = deepcopy(self.MorseCells[persistence])

        self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent] = {}
        self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"] = create_SalientEdgeCellConnectivityGraph(Cells, 
                                                                                                                salient_edge_points,
                                                                                                                self.Vertices,
                                                                                                                self.Edges)
        start_time = timeit.default_timer()
        # merge cells 40 iterations:
        for i in range(40):
            Cells = self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].simplify_cells(Cells, edge_percent, salient_edge_points, self.Vertices)
        # remove small components:
        Cells = self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].remove_small_components(Cells, size_thresh=300)

        # remove enclosures
        Cells = self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].remove_small_enclosures(Cells)


        self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Cells"] = Cells

        end_time = timeit.default_timer() - start_time
        print('Time merging and simplifying Cells:', end_time)

        print("Segmented for",persistence, "persistence Complex with", thresh_high, thresh_low, "salient edge threshold and", edge_percent*100, "% edge percentage merging threshold")
        print("Got ",len(self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]["Graph"].conncomps),"differnt cell labels")

    return self.SegmentationDual[persistence][thresh_high][thresh_low][edge_percent]