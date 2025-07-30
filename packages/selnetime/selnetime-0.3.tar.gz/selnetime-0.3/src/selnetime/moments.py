import math
from collections import defaultdict
from collections.abc import Iterable, Callable
import numpy as np
from numpy.typing import NDArray

from scipy.special import beta as beta_f
from numba import njit, jit, vectorize, int32, float64
from sympy import symbols, lambdify, simplify, diff
from . import utils
from . import TransModel, TransParam

### positions of the moments in the moment arrays
p0_i = 0
p1_i = 1
m_i = 2
v_i = 3
a_i = 4
b_i = 5


@njit
def beta_ratio(a: float, b: float, N: int) -> float:
    """
    computes the ratio beta(a+N,b)/beta(a,b)
    """
    res = 1.0
    for i in range(N):
        res *= (a + i) / (a + b + i)
    return res

@njit
def beta_ratio2(a: float, b: float, x: int, y: int) -> float:
    """
    computes the ratio beta(a+x,b+y)/beta(a,b)
    """
    v1=np.sum(np.log(a+np.arange(x)))
    v2=np.sum(np.log(b+np.arange(y)))
    v3=np.sum(np.log(a+b+np.arange(x+y)))
    res=np.exp(v1+v2-v3)
    return res


# @vectorize([float64(float64, float64)])
# def beta_f(a: float, b: float) -> float:
#     y = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
#     return math.exp(y)


class Moments_factory:
    """Class implementing approximate computations of the moments of the
    distribution of a Wright-Fisher process P(X_t|N,s,h,x_0)

    """

    xzero: Iterable[float] = None  # conditioning starting frequencies
    model: TransModel = TransModel.BwS  # distribution of the transitions
    # should the Mathieson and Terhorst (2023) moments approximation be used
    MT2023: bool = False

    def __init__(
        self, x0: Iterable[float], model: TransModel = None, MT2023: bool = False
    ):
        _xz = np.array(x0)
        assert len(_xz.shape) == 1
        self.xzero = _xz
        if model:
            self.model = TransModel(model)
        self.MT2023 = MT2023
        # private variable `_store` keeps calculated values for speed
        # up. The type is dict[tuple,list[NDArray]] where tuple is
        # (N,s,h), list is successive generations so that
        # dict[(N,x,h)][i] gives moments after i+1 generations.
        # Moments are arrays of size (len(xzero,6)) for mean, var, p0, p1, a,b
        self._mshape = (self.xzero.shape[0], 6)  # mean, var, p0, p1, a, b
        self._store_moments = {}
        # private variable `_store_ffunc` keeps track of the fitness
        # functions, their first and second order derivatives as a
        # function of (s,h)
        self._store_ffunc = {}

    def get_moments(self, N: int, s: float, h: float, dt: int):
        try:
            mom = self._store_moments[(N, s, h)][dt - 1, :]
        except:
            ff = self.get_fitness_functions(s, h)
            # wfm = wf_moments(N, s, h, dt, self.xzero, ff[0], ff[1], ff[2])
            mom = bws_moments(N, s, h, dt, self.xzero, ff[0], ff[1], ff[2])
            self._store_moments[(N, s, h)] = mom
            mom = mom[dt - 1, :]
        return mom

    def get_fitness_functions(
        self, s: float, h: float = 1 / 2
    ) -> list[Callable[[float], float]]:
        """Returns the (callable) fitness function and its first and second
        order derivatives in x.

        The three functions are evaluated at specified values for the
        selection parameter mys and dominance parameter (myh, default
        = additive).

        The three functions are evaluated symbolically (using sympy) ,
        lambdified and njit compiled. They can be passed numpy arrays
        as arguments.

        Parameters:
        - s: Selection parameter.
        - h: Dominance parameter (default = additive).

        Returns a list of length 3 with:
        - f: Fitness function.
        - fp: First derivative of the fitness function.
        - fpp: Second derivative of the fitness function.

        """
        try:
            ffunc = self._store_ffunc[(s, h)]
        except KeyError:
            x, _s, _h = symbols("x s h")
            fitness_f = (
                x
                * (1 + _s * _h + _s * (1 - _h) * x)
                / (1 + 2 * _s * _h * x + _s * (1 - 2 * _h) * x ** 2)
            )
            f_symb = simplify(fitness_f.subs({_s: s, _h: h}))
            fp_symb = diff(f_symb, x)
            fpp_symb = diff(fp_symb, x)

            f = njit(lambdify(x, f_symb))
            fp = njit(lambdify(x, fp_symb))
            fpp = njit(lambdify(x, fpp_symb))
            ## force compiling functions here
            _ = f(self.xzero)
            _ = fp(self.xzero)
            _ = fpp(self.xzero)
            ffunc = [f, fp, fpp]
            self._store_ffunc[(s, h)] = ffunc
        return ffunc


# @njit
def wf_moments(
    N: int,
    s: float,
    h: float,
    dt: int,
    xzero: NDArray[np.float64],
    # starting_moments: NDArray[np.float64],
    f: Callable[[float], float],
    fp: Callable[[float], float],
    fpp: Callable[[float], float],
) -> NDArray[np.float64]:

    moments = np.zeros((dt + 1, 2, xzero.shape[0]))  # time, (0: mean, 1: var) , x0
    # moments[0, :, :] = starting_moments
    moments[0, 0, :] = xzero

    # Calculate pfix_lim based on selection parameter s
    if s > 0 and abs(2 * N * s) < 700:
        pfix_lim = (1 - np.exp(-2 * N * s * xzero)) / (
            1 - np.exp(-2 * N * s)
        )  ## Kimura
    elif s < 0 and abs(2 * N * s) < 700:
        s_prim = 1 / (1 + s) - 1
        pfix_lim = (1 - np.exp(-2 * N * s_prim * xzero)) / (1 - np.exp(-2 * N * s_prim))
    else:
        pfix_lim = np.ones_like(xzero)

    for t in range(dt):
        # Calculate next moment using fitness function and second derivative
        val = f(moments[t, 0, :]) + 0.5 * fpp(moments[t, 0, :]) * moments[t, 1, :]
        val[val < 0] = 0
        sub = val > pfix_lim
        val[sub] = pfix_lim[sub]
        moments[t + 1, 0, :] = val

        # Calculate next variance using first derivative and previous variance
        val = (1 - 1.0 / N) * moments[t, 1, :] * fp(moments[t, 0, :]) ** 2
        val[val < 0] = 0
        val += (1.0 / N) * moments[t + 1, 0, :] * (1 - moments[t + 1, 0, :])
        val[val < 0] = 0
        val[val > 1] = 1
        sub = val > (moments[t + 1, 0, :]) * (1 - moments[t + 1, 0, :])  # var_lim
        val[sub] = (moments[t + 1, 0, sub]) * (1 - moments[t + 1, 0, sub])
        moments[t + 1, 1, :] = val

        # Check if variance is close to zero, and stop the process if so
        if np.all(moments[t + 1, 1, :] < 1e-6):
            # no more variance in the process : stop it
            # moments[t + 1 : dt_max] = 0
            for _t in range(t + 1, dt + 1):
                moments[_t, 0, :] = moments[t, 0, :]
                # moments[_t, 1, :] = 0 ## not required as init at 0
            break
    return moments[1:, :, :]


# @njit
def bws_moments(
    N: int,
    s: float,
    h: float,
    dt: int,
    xzero: NDArray[np.float64],  # starting_moments: NDArray[np.float64],
    f: Callable[[float], float],
    fp: Callable[[float], float],
    fpp: Callable[[float], float],
) -> NDArray[np.float64]:
    """Returns an array of approximate moments of a Wrigh-Fisher process,
    characterized by N,s,h for dt generation, with starting allele frequency xzero

    Returns an array of size (dt, 6, len(xzero)), where the 6 moments are:
    - Probability of fixation at 0
    - Probability of fixation at 1
    - mean
    - variance
    - a, b parameters of the beta distribution

    Parameters:
    - N: Effective haploid population size.
    - s: Selection parameter.
    - h: Dominance parameter
    - dt: Maximum value for the time.
    - xzero: starting allele frequencies, assumes xzero[0] == 0 and xzero[-1] == 0
    - f, fp, fpp: fitness function, its first and second derivatives
    """

    moments_wf = wf_moments(N, s, h, dt, xzero, f, fp, fpp)

    # Calculate initial conditions
    moments_bws = np.zeros((dt, 6, xzero.shape[0]), dtype=np.float64)
    nx = xzero.shape[0]
    moments_bws[:, p0_i, 0] = 1  # Pfix (0) when the frequency is 0 is 1
    moments_bws[:, p1_i, -1] = 1  # Pfix (1) when the frequency is 1 is 1
    moments_bws[0, m_i, :] = xzero  # initialize mean at xzero
    # stay on 1 if starting at 1, note
    # that its already the case @0
    moments_bws[:, m_i, -1] = 1
    wf_mean = moments_wf[0, 0, 1 : (nx - 1)]
    wf_var = moments_wf[0, 1, 1 : (nx - 1)]

    const_lim = 0
    cur_mean = moments_bws[0, m_i, 1 : (nx - 1)]
    cur_var = np.zeros_like(cur_mean)
    cur_a = np.zeros_like(cur_mean)
    cur_b = np.zeros_like(cur_mean)

    cur_p_0 = (1 - f(xzero[1 : (nx - 1)])) ** N
    cur_p_1 = f(xzero[1 : (nx - 1)]) ** N
    const = 1 - cur_p_0 - cur_p_1
    fixed = np.nonzero(const <= const_lim)
    varia = np.nonzero(const > const_lim)
    ## fixed at the start
    cur_p_0[fixed] = cur_p_0[fixed] * (1 - const_lim) / (1 - const[fixed])
    cur_p_1[fixed] = cur_p_1[fixed] * (1 - const_lim) / (1 - const[fixed])
    # uniform distribution
    cur_mean[fixed] = 1 / 2
    cur_var[fixed] = 1 / 12
    cur_a[fixed] = 1
    cur_b[fixed] = 1
    #
    cur_mean[varia] = (wf_mean[varia] - cur_p_1[varia]) / const[varia]
    cur_var[varia] = (wf_var[varia] + wf_mean[varia] ** 2 - cur_p_1[varia]) / const[
        varia
    ] - cur_mean[varia] ** 2
    ##
    var_lim = cur_mean * (1 - cur_mean)
    cond_up = cur_var < var_lim
    cond_down = cur_var > 0
    good = cond_up & cond_down
    cur_a[good] = cur_mean[good] * (var_lim[good] / cur_var[good] - 1)
    cur_b[good] = (1 - cur_mean[good]) * (var_lim[good] / cur_var[good] - 1)
    cur_a[~cond_up | ~cond_down] = cur_p_1[~cond_up | ~cond_down]
    cur_b[~cond_up | ~cond_down] = cur_p_0[~cond_up | ~cond_down]
    cur_var[~cond_up] = var_lim[~cond_up]
    cur_var[~cond_down] = 0

    moments_bws[0, p0_i, 1 : (nx - 1)] = cur_p_0
    moments_bws[0, p1_i, 1 : (nx - 1)] = cur_p_1
    moments_bws[0, m_i, 1 : (nx - 1)] = cur_mean
    moments_bws[0, v_i, 1 : (nx - 1)] = cur_var
    moments_bws[0, a_i, 1 : (nx - 1)] = cur_a
    moments_bws[0, b_i, 1 : (nx - 1)] = cur_b

    for t in range(1, dt):
        prev_a = moments_bws[t - 1, a_i, 1 : (nx - 1)]
        prev_b = moments_bws[t - 1, b_i, 1 : (nx - 1)]
        prev_mean = moments_bws[t - 1, m_i, 1 : (nx - 1)]
        prev_var = moments_bws[t - 1, v_i, 1 : (nx - 1)]
        wf_mean = moments_wf[t, 0, 1 : (nx - 1)]
        wf_var = moments_wf[t, 1, 1 : (nx - 1)]
        bottom = beta_f(prev_a, prev_b)
        cur_p_0 = moments_bws[t - 1, p0_i, 1 : (nx - 1)]
        cur_p_1 = moments_bws[t - 1, p1_i, 1 : (nx - 1)]
        cur_mean = np.zeros_like(moments_bws[0, m_i, 1 : (nx - 1)])
        cur_var = np.zeros_like(moments_bws[0, v_i, 1 : (nx - 1)])

        cond = (
            (bottom > 0)
            & (~np.isinf(bottom))
            & (prev_a > 0)
            & (prev_b > 0)
            & (const > const_lim)
        )
        beta_0 = beta_f(prev_a, prev_b + N) -N*s/2*beta_f(prev_a+1, prev_b + N) + N*(N+3)*s**2/8*beta_f(prev_a+2, prev_b + N)
        negative=(beta_0<0)
        beta_0[negative]=0
        beta_1 = beta_f(prev_a + N, prev_b) + N*s/2*beta_f(prev_a + N, prev_b + 1) + N*(N-1)*s**2/8*beta_f(prev_a + N, prev_b + 2) -N*s**2/2*beta_f(prev_a + N +1, prev_b + 1)
        negative=(beta_1<0)
        beta_1[negative]=0
        cur_p_0[cond] = cur_p_0[cond] + const[cond] * beta_0[cond] / bottom[cond]
        cur_p_1[cond] = cur_p_1[cond] + const[cond] * beta_1[cond] / bottom[cond]
        const[cond] = 1 - cur_p_0[cond] - cur_p_1[cond]
        ## treat fixed guys
        fixed = const <= const_lim
        cur_p_0[fixed] = cur_p_0[fixed] * (1 - const_lim) / (1 - const[fixed])
        cur_p_1[fixed] = cur_p_1[fixed] * (1 - const_lim) / (1 - const[fixed])
        cur_mean[fixed] = prev_mean[fixed]
        cur_var[fixed] = prev_var[fixed]
        cur_a[fixed] = prev_a[fixed]
        cur_b[fixed] = prev_b[fixed]
        ## variable cases
        varia = const > const_lim
        val = wf_mean[varia] - cur_p_1[varia]
        val = np.where(val < 0, 0, val)
        val /= const[varia]
        val = np.where(val > 1, 1, val)
        cur_mean[varia] = val
        cur_var[varia] = (wf_var[varia] + wf_mean[varia] ** 2 - cur_p_1[varia]) / const[
            varia
        ] - cur_mean[varia] ** 2
        var_lim[varia] = cur_mean[varia] * (1 - cur_mean[varia])
        ##
        cond_up = cur_var < var_lim
        cond_down = cur_var > 0
        good = cond_up & cond_down & varia
        # good
        cur_a[good] = cur_mean[good] * (var_lim[good] / cur_var[good] - 1)
        cur_b[good] = (1 - cur_mean[good]) * (var_lim[good] / cur_var[good] - 1)
        # bad
        cur_a[varia & (~cond_up | ~cond_down)] = prev_a[varia & (~cond_up | ~cond_down)]
        cur_b[varia & (~cond_up | ~cond_down)] = prev_b[varia & (~cond_up | ~cond_down)]
        cur_var[varia & ~cond_up] = var_lim[varia & ~cond_up]
        cur_var[varia & ~cond_down] = 0

        moments_bws[t, p0_i, 1 : (nx - 1)] = cur_p_0
        moments_bws[t, p1_i, 1 : (nx - 1)] = cur_p_1
        moments_bws[t, m_i, 1 : (nx - 1)] = cur_mean
        moments_bws[t, v_i, 1 : (nx - 1)] = cur_var
        moments_bws[t, a_i, 1 : (nx - 1)] = cur_a
        moments_bws[t, b_i, 1 : (nx - 1)] = cur_b

    return moments_bws
