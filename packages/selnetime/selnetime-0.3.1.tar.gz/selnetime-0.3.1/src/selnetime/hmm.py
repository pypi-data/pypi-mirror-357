from math import comb
import numpy as np
import numba
from numba import njit, prange, jit
from scipy.special import betainc
from .moments import p0_i, p1_i, m_i, v_i, a_i, b_i

def transition_wf(N,s,h,dt):
    """Compute the transition matrix Q(x(t+dt)|x(t)) from the WF distribution
    """
    # single generation WF matrix
    Q=np.zeros(shape=(N+1, N+1))
    x=np.arange(N+1)/N
    _num=(1+s)*x**2+(1+s*h)*x*(1-x)
    _den=(1+s)*x**2+2*(1+s*h)*x*(1-x)+(1-x)**2
    fit=_num/_den
    for j in range(N+1):
        Q[:,j]=fit**j*(1-fit)**(N-j)*comb(N, j)

    # Calculate Q for each dt
    if dt>1:
        Q=np.linalg.matrix_power(Q,dt)
        
    return Q
    
def transition_bws(xt, mom):
    """Compute the transition matrix Q(x(t+k)|x(t)) from the Beta with
    Spikes moments (p0,p1,a,b)

    xt is the conditioning starting allele frequency, supposed to include 0 and 1.
    For example xt = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    """
    p0 = mom[p0_i, :]
    p1 = mom[p1_i, :]
    a = mom[a_i, :]
    b = mom[b_i, :]

    nx = xt.shape[0]
    Q = np.zeros((nx, nx), dtype=np.float64)
    # Treat intermediate allele frequencies
    # _dx : integration intervals bounds
    # e.g. [0,0.2,0.4,0.6,0.8,1]
    _dx = np.linspace(0,1,nx-1)
    # build beta distribution parameters
    # (a,b)[0] and (a,b)[nx-1] are degenerate
    _a = a[1 : (nx - 1)] # shape == nx - 2
    _b = b[1 : (nx - 1)] ## shape == nx - 2
    ndist = _a.shape[0]
    cdf_x = np.transpose(betainc(_a, _b, np.repeat(_dx, ndist).reshape(nx - 1, ndist)))
    F_x = (
        cdf_x[:, 1:] - cdf_x[:, :-1]
    )
    Q[1 : (nx - 1), 1 : (nx - 1)] = F_x
    ## Include fixation probabilities
    Q[:, 0] = p0  # fixing at 0 : P(Xt+1 = 0|Xt)
    Q[:, nx - 1] = p1  # fixing at 1 : P(Xt+1 =1 |Xt)
    p_nonfix = np.repeat(1 - p0 - p1, nx - 2).reshape(nx, nx - 2)
    Q[:, 1 : (nx - 1)] *= p_nonfix
    return Q


def emissions_binom(x, count, depth):
    """Compute emission probabilities of `count` among `depth` conditioning
    on allele frequency `x`"""
    e = comb(depth, count) * x ** count * (1 - x) ** (depth - count)
    return e


def hmm_fwd_loglik(trajectories, emissions):
    """Compute the HMM log-likelihood with the forward algorithm

    Input:
    ------

    - trajectories : numpy array of shape (shp_p,ndt,nx,nx) of transition matrices
    - emissions : numpy array of shape (shp_l,ndt+1,nx) of emission probabilities

    The prefix shape (shp_p) of `trajectories` can be None (e.g. only one set of parameters)
    The prefix shape (shp_l) of `emissions` can be None  (e.g. only one locus)

    Returns : an array of size (shp_p, shp_l) of log-likelihoods for e.g.
    each parameter set and at each locus
    """

    nx = trajectories.shape[-2]
    ndt = trajectories.shape[-3]

    ## Flatten transition arrays for parallel computations
    if len(trajectories.shape) > 3:
        params_shape = trajectories.shape[:-3]
        _traj = trajectories
    else:
        params_shape = np.ones((1,)).shape
        _traj = np.reshape(trajectories, (1, *trajectories.shape))

    ## Flatten / Broadcast emission arrays
    if len(emissions.shape) > 2:
        locus_shape = emissions.shape[:-2]
        _em = emissions
    else:
        locus_shape = np.ones((1,)).shape
        _em = np.reshape(emissions, (1, *emissions.shape))

    loglik = np.zeros((*params_shape, *locus_shape), dtype=np.float64)

    for _ip in np.ndindex(params_shape):
        _q = _traj[_ip]  # dt x nx x nx
        fwd = np.ones(locus_shape + (ndt + 1, nx), dtype=np.float64)
        sca = np.zeros(locus_shape, dtype=np.float64)
        lik = np.zeros(locus_shape, dtype=np.float64)
        ## 1. Initialization
        fwd[..., 0, :] = (1.0 / nx) * _em[..., 0, :]
        sca = 1.0 / np.sum(fwd[..., 0, :], axis=-1)
        fwd[..., 0, :] = fwd[..., 0, :] * sca[..., :, None]
        lik += -np.log(sca)
        ## 2. Induction
        for t in range(ndt):
            # for _x in range(nx):
            #     fwd[..., t + 1, _x] = (
            #         np.sum(fwd[..., t, :] * _q[t, :, _x], axis=-1) * _em[..., t + 1, _x]
            #     )
            ### Same as above, using einsum
            fwd[..., t + 1, :] = np.einsum(
                "...i,ij,...j->...j",
                fwd[..., t, :],
                _q[t, :, :],
                _em[..., t + 1, :],
            )
            sca = 1.0 / np.sum(fwd[..., t + 1, :], axis=-1)
            fwd[..., t + 1, :] = fwd[..., t + 1, :] * sca[..., :, None]
            lik += -np.log(sca)
        loglik[_ip, ...] = lik
    return loglik
