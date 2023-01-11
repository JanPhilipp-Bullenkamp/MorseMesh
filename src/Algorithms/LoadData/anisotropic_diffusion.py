import numpy as np

def compute_gradient(vert_dict: dict) -> dict:
    gradient = {}
    for ind, vert in vert_dict.items():
        gradient[ind] = vert.compute_gradient(vert_dict)
    return gradient

def diffusivity_coeff(grad, k, option="fraction"):
    if option == "fraction":
        c = 1/(1+(np.abs(grad)/k)**2)
    elif option == "exp":
        c = np.exp(-np.abs(grad)**2 / (2*k**2))
    return c

def compute_anisotropic_diffusion(vert_dict: dict, iterations: int, lamb: float, k: float):
    """! @brief Calculates Perona-Malik anisostropic diffusion on the vertices given.
    @details Explain ....

    @param vert_dict The vertices dictionary to be smoothed. (Needs Vertex objects with compute_gradient method)
    @param iterations Number of "time steps" to be performed. Higher -> more smoothing.
    @param lamb Scaling factor: small -> slower smoothing, high -> faster smothing. Typical values between 0.1-0.25
    @param k Controls the sensitivity of the diffusivity coefficient to the gradient .... Typical values between 0.1-0.25
    
    @return vert_dict The smoothed vertices dictionary.
    """
    for i in range(iterations):
        gradient = compute_gradient(vert_dict)
        print("Iteration: ",i, " Funval: ",vert_dict[10].fun_val)
        if len(gradient) != len(vert_dict):
            raise AssertionError("Gradient and Vertices dictionaries should have same length!")
        
        for v_ind, vert in vert_dict.items():
            dt = lamb * (diffusivity_coeff(gradient[v_ind], k, option="fraction") * gradient[v_ind])

            vert.fun_val += dt

    return vert_dict