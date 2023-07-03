from src.morse import Morse

class Parameters:
    def __init__(self):
        self.reset()

    def reset(self):
        self.feature_vector_function = "maxabs"
        self.high_thresh = None
        self.low_thresh = None
        self.mode = "ridge" # options: "ridge", "valley" or "both" 
        self.separatrix_type = "reverse" # options: "all", "reverse" or "cutoff"
        self.min_length = 1
        self.max_length = float('inf')

        self.high_percent = 75
        self.low_percent = 70

        self.persistence = 0.04
        self.merge_threshold = 0.3
        self.cluster_seed_number = 150
        self.merge_threshold_cluster = 0.3

        self.size_threshold = 500

    def update(self, value, attr: str):
        if hasattr(self, attr):
            setattr(self, attr, value)
        else:
            raise AttributeError("No such parameter found in Parameters class!")

class Flags:
    def __init__(self):
        self.reset()

    def reset(self):
        self.flag_loaded_data = False
        self.flag_morse_computations = False
        self.flag_current_segmentation = False
        self.flag_sliders_shown = False
        self.flag_conforming_input = False
        self.flag_conforming_morse = False

class Data:
    def __init__(self):
        self.reset()

    def reset(self):
        self.morse = Morse()

        self.color_points = set()
        self.current_segmentation = {}
        self.current_segmentation_params = None