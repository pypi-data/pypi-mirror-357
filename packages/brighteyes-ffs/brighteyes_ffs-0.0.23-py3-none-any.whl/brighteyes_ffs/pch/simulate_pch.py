import numpy as np

def simulate_pch_1c(psf, n=30, c=1, q=1, T=1):
    """
    Recover the photon counting histogram P(k) from the generating function G(xi)
    Assume 1 component

    Parameters
    ----------
    psf : np.array()
        3D array with the PSF, normalized to sum=1.
    n : int, optional
        Number of histogram bins to simulate. The default is 30.
    c : float, optional
        Emitter concentration. The default is 1.
    q : float, optional
        Brighness of the emitter. The default is 1.
    T : float, optional
        Bin time. The default is 1.

    Returns
    -------
    coeffs
        P(k) for k=0..n-1.

    """
    
    all_xi = np.linspace(-1, 1, int(2*n+1))
    G = np.zeros((len(all_xi)))
    int_B = q * psf * T

    all_exp_xi = np.exp(all_xi - 1)
    for i, xi in enumerate(all_xi):
        G[i] = np.sum(all_exp_xi[i] ** int_B - 1)
    G = np.exp(c * G)

    coeffs = np.polyfit(all_xi, G, n)
    coeffs /= np.sum(coeffs)
    
    return coeffs[::-1]