import numpy as np

def compute_gradient(vert_dict: dict, face_dict: dict) -> dict:
    gradient = {}
    for ind, vert in vert_dict.items():
        gradient[ind] = vert.average_gradient_on_star(vert_dict, face_dict)
    return gradient

def smooth_gradient(gradient: dict, vert_dict: dict, lamb: float):
    smoothed_gradient = {}
    for ind in gradient.keys():
        neis = vert_dict[ind].get_n_neighborhood(vert_dict, 3)
        nei_grad = np.mean([gradient[nei_ind] for nei_ind in neis])
        smoothed_gradient[ind] = nei_grad #grad + lamb * (nei_grad - grad)
    return smoothed_gradient

def smooth_function_values(vert_dict: dict, n_neighborhood: int = 1):
    smoothed_fun_vals = {}
    for ind, vert in vert_dict.items():
        if n_neighborhood > 1:
            neis = vert.get_n_neighborhood(vert_dict, n_neighborhood)
        elif n_neighborhood == 1:
            neis = vert.neighbors
        else:
            raise ValueError('n_neighborhood should be positive integer (1 or larger)')
        mean_val = np.mean([vert_dict[nei].fun_val for nei in neis])
        smoothed_fun_vals[ind] = mean_val
    # update fun_vals
    for ind, vert in vert_dict.items():
        vert.fun_val = smoothed_fun_vals[ind]


def diffusivity_coeff(grad, k, option="fraction"):
    if option == "fraction":
        c = 1/(1+(np.abs(grad)/k)**2)
    elif option == "exp":
        c = np.exp(-(np.abs(grad)/k)**2)
    return c

def compute_anisotropic_diffusion(vert_dict: dict, face_dict: dict, iterations: int, lamb: float, k: float):
    """! @brief Calculates Perona-Malik anisostropic diffusion on the vertices given.
    @details Explain ....

    @param vert_dict The vertices dictionary to be smoothed. (Needs Vertex objects with compute_gradient method)
    @param iterations Number of "time steps" to be performed. Higher -> more smoothing.
    @param lamb Scaling factor: small -> slower smoothing, high -> faster smothing. Typical values between 0.1-0.25
    @param k Controls the sensitivity of the diffusivity coefficient to the gradient .... Typical values between 0.1-0.25
    
    @return vert_dict The smoothed vertices dictionary.
    """
    for i in range(iterations):
        gradient = compute_gradient(vert_dict, face_dict)

        #smoothed_gradient = smooth_gradient(gradient, vert_dict, 0.5)

        print("Iteration: ",i, " Funval: ",vert_dict[10].fun_val)
        if len(gradient) != len(vert_dict):
            raise AssertionError("Gradient and Vertices dictionaries should have same length!")
        
        for v_ind, vert in vert_dict.items():
            vert.fun_val += lamb * np.linalg.norm(diffusivity_coeff(gradient[v_ind], k, option="exp"))

    return vert_dict