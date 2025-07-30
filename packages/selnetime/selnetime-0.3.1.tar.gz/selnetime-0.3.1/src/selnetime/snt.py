import sys
import argparse
import csv
from collections import defaultdict
from collections.abc import Iterable
import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm
from scipy.stats import chi2
from .utils import Timer
from . import moments, hmm
from . import TransModel, TransParam


class GeneticTimeSeries:
    ## input data
    epochs: NDArray[int]  # 1D array size T
    deltat: NDArray[int]  # 1D array size T-1
    counts: NDArray[int]  # 2D array size L x T
    depths: NDArray[int]  # 2D array size L x T

    def __init__(self, epochs, counts, depths):
        assert len(counts) == len(depths)
        self.epochs = np.array(epochs, dtype=int)
        assert len(self.epochs.shape) == 1
        self.deltat = self.epochs[1:] - self.epochs[:-1]
        self.counts = np.array(counts, dtype=int)
        self.depths = np.array(depths, dtype=int)
        assert len(self.counts.shape) == 2 and len(self.depths.shape) == 2
        self.L = self.counts.shape[0]
        self.T = self.counts.shape[1]

    @classmethod
    def from_baypass(cls, prefix):
        """Create a GeneticTimeSeries instance from data in baypass format

        The <prefix>.genobaypass file:
        - has one line per locus
        - on each line, successive *pairs* of counts are given (Allele A, Allele B)
          all values are separated by whitespaces

        The <prefix>.time file:
        - has a single line of epochs (dates in generations, usually
          but not necessarily starting at 0), separated by commas

        """
        with open(prefix + ".genobaypass") as f:
            counts = []
            depths = []
            for ligne in f:
                buf = ligne.split()
                counts_A = [int(x) for x in buf[::2]]
                counts_B = [int(x) for x in buf[1::2]]
                counts.append(counts_A)
                depths.append([x[0] + x[1] for x in zip(counts_A, counts_B)])

        with open(prefix + ".times") as f:
            epochs = [int(x) for x in f.readline().rstrip().split(",")]

        return cls(epochs, counts, depths)

    @classmethod
    def from_compareHMM(cls, prefix):

        file_path = prefix + ".csv"
        counts = []
        depths = []
        # Open the CSV file using 'with open'
        with open(file_path, mode="r") as csv_file:
            csv_reader = csv.reader(csv_file)

            # Skip the first row
            colnames = next(csv_reader)
            idx_traj_times = colnames.index("traj_times")
            idx_traj_emis = colnames.index("traj_emis")
            idx_traj_ssize = colnames.index("traj_ssize")

            for row in csv_reader:
                # Assuming each row contains two strings representing lists
                traj_times = row[idx_traj_times]
                traj_emis = row[idx_traj_emis]
                traj_ssize = row[idx_traj_ssize]

                # Convert the strings to lists of integers
                epochs = [int(x) for x in traj_times.strip("[ ]").split()]
                count = [int(x) for x in traj_emis.strip("[ ]").split()]
                depth = [int(x) for x in traj_ssize.strip("[ ]").split()]

                counts.append(count)
                depths.append(depth)

        return cls(epochs, counts, depths)

    def __str__(self):
        result = (
            f"Genetic Time Series Data on {len(self.epochs)} times and {self.L} loci\n"
            + f"epochs: {self.epochs}\n"
        )
        return result


class GTS_Parameters:
    ## Evolutionary model Parameters
    T: int  # number of epochs
    L: int  # number of loci
    demography: NDArray[int] = None  # 1D array size T-1
    S: NDArray[np.float64] = None  # 2D array size (T-1) x L
    h: NDArray[np.float64] = None  # 2D array size (T-1) x L

    def __init__(self, T: int, L: int) -> None:
        self.T = T
        self.L = L
        ## set default values for parameters
        self.demography = -1 * np.ones(self.T - 1, dtype=int)
        self.S = np.zeros((self.T - 1, self.L), dtype=np.float64)
        self.h = 0.5 * np.ones((self.T - 1, self.S), dtype=np.float64)

    def set_constant_demography(self, Ne: int) -> None:
        """Set a constant populations size demography"""
        self.demography = int(Ne) * np.ones_like(self.demography, dtype=int)

    def set_demography(self, Ne_vect: Iterable[int]) -> None:
        """Set a demography as a vector of population sizes"""
        demo = np.array(Ne_vect, dtype=int)
        assert demo.shape == self.demography.shape
        self.demography = demo

    def get_unique_parameters(self, deltat: Iterable[int] = None) -> set[tuple]:
        """Return the set of unique transition parameters (TransParam) across
        loci and time intervals.

        By default, assumes one generation intervals. This can be adjusted by
        providing a list of time intervals (deltat) between successive
        epochs.

        """
        if deltat:
            assert len(deltat) == self.demography.shape[0]
        else:
            deltat = [1] * self.demography.shape[0]
        params = defaultdict(int)
        for interval in range(self.T - 1):
            N = self.demography[interval]
            dt = deltat[interval]
            for loc in self.L:
                params[
                    TransParam(dt, N, self.S[interval, loc], self.h[interval, loc])
                ] += 1
        return set(params.keys())


class GTS_Analyser:
    """A class to analyse a GeneticTimeSeries instance and estimate GTS_Parameters

    needs to be initialized by at least one value for the effective population size
    Assumes additive fitness (h=0.5)
    """

    # Analyser parameters
    N_grid_size: int = 100  # size of the grid for effective population size
    S_grid_size: int = 101  # size of the grid for selection parameter
    X_grid_size: int = 102  # size of the grid for allele frequencies
    transition_model: TransModel = TransModel(
        "BwS"
    )  # Model to use for transitions (default: Beta with Spikes)

    def __init__(
        self,
        model=None,
        verbosity=3,
        N_grid_size: int = None,
        S_grid_size: int = None,
        X_grid_size: int = None,
    ):
        self.verbosity = verbosity
        if model:
            self.transition_model = TransModel(model)
        if N_grid_size != None:
            self.N_grid_size = N_grid_size
        # S grid
        if S_grid_size:
            ## make sure 0 is in the grid
            if S_grid_size % 2 == 0:
                S_grid_size += 1
            self.S_grid_size = S_grid_size
        ## set prior on S s.t. log2(1+s) ~ N(0,0.5)
        q = np.linspace(0.0005, 0.9995, self.S_grid_size)
        w = norm.ppf(q, scale=0.5)
        self._S_grid = 2 ** w - 1
        self._S_logprior = norm.logpdf(w, scale=0.5)
        #
        dw = 0.5 * (w[1:] - w[:-1])
        imoins = np.zeros_like(w)
        iplus = np.zeros_like(w)
        imoins[1:] = w[1:] - dw
        imoins[0] = w[0] - dw[0]
        iplus[:-1] = w[:-1] + dw
        iplus[-1] = w[-1] + dw[-1]
        dk = 2 ** iplus - 2 ** imoins
        self._S_logprior += np.log(dk)
        ## X grid
        if X_grid_size:
            self.X_grid_size = X_grid_size + 2  ## add 0 and 1
        _ib = np.linspace(0, 1, self.X_grid_size - 1)
        _mids = 0.5 * (_ib[1:] + _ib[:-1])
        self._X_grid = np.zeros(self.X_grid_size, dtype=float)
        self._X_grid[-1] = 1
        self._X_grid[1:-1] = _mids
        if self.transition_model != TransModel.WF:
            self.mf = moments.Moments_factory(self._X_grid)

    def __str__(self):
        result = f"Genetic Time Series Analyser\n"
        if self.N_grid_size != 0:
            result += f"N_grid_size: {self.N_grid_size}\n"
        result += (
            f"S_grid_size: {self.S_grid_size}\n" + f"Model: {self.transition_model}\n"
        )
        if self.verbosity >= 3:
            result += f"S_grid: {self._S_grid}\n"
        if self.transition_model != TransModel.WF and self.verbosity >= 3:
            result += f"X_grid: {self._X_grid}\n"
        return result

    def analyze(self, gts, Ne=None, Sesti=True, sel=0):
        """Perform an analysis of the genetic time series gts"""
        if sel != 0:
            assert Sesti != True
        results = defaultdict(dict)

        if self.transition_model == TransModel.WF:
            assert Ne != None
            self.X_grid_size = Ne + 1
            self._X_grid = np.arange(Ne + 1) / Ne

        with Timer("Build Emissions", verbosity=self.verbosity):
            emissions = np.zeros((gts.L, gts.T, self.X_grid_size))
            for l in range(gts.L):
                for i, dat in enumerate(zip(gts.counts[l], gts.depths[l])):
                    emissions[l, i, :] = hmm.emissions_binom(
                        self._X_grid, dat[0], dat[1]
                    )
        if Ne is None:
            assert self.transition_model != TransModel.WF
            ## Estimate effective population size
            # results["Ne"] = {}
            with Timer("1. Estimate Ne", verbosity=self.verbosity):
                Ne_lik = self.estimate_Ne(emissions, gts.deltat, sel)
            results["Ne"]["lik"] = Ne_lik
            L = sorted(Ne_lik.items(), key=lambda x: -x[1])
            results["Ne"]["bestN"] = L[0][0]
            results["Ne"]["bestL"] = L[0][1]
            nei = [k for k, v in Ne_lik.items() if v > (L[0][1] - 2)]
            results["Ne"]["loN"] = min(nei)
            results["Ne"]["hiN"] = max(nei)
            if self.verbosity >= 1:
                print(
                    f"Estimate of the effective population size: {results['Ne']['bestN']}"
                    + f" ({results['Ne']['loN']} -- {results['Ne']['hiN']})"
                )
        else:
            results["Ne"]["bestN"] = Ne
            if self.verbosity >= 1:
                print(f"Known effective population size: {Ne}")
        if Sesti:
            ## Estimate selection coefficients
            with Timer(
                f"2. Estimate s for N= {results['Ne']['bestN']}",
                verbosity=self.verbosity,
            ):
                S_lik = self.estimate_s_given_N(
                    results["Ne"]["bestN"], emissions, gts.deltat
                )
            ## Maximum Likelihood
            idx_max = np.argmax(S_lik, axis=0)
            lmax = np.max(S_lik, axis=0)
            S_mle = self._S_grid[idx_max]
            ## Confidence interval
            idx_sei = np.vstack([self._S_grid] * S_lik.shape[1]).T
            idx_sei = np.where(S_lik > lmax - 2, idx_sei, np.nan)
            seimin = np.nanmin(idx_sei, axis=0)
            seimax = np.nanmax(idx_sei, axis=0)
            seimin[np.isnan(seimin)] = min(self._S_grid)
            seimax[np.isnan(seimax)] = max(self._S_grid)
            ## Likelihood-ratio test
            idx_zero = int(self.S_grid_size / 2)
            lrt = 2 * (
                S_lik[idx_max, range(S_lik.shape[1])]
                - S_lik[idx_zero, range(S_lik.shape[1])]
            )
            lrt_p_value = chi2.sf(lrt, 1)
            ## Bayesian Inference
            if self.S_grid_size > 1:
                S_logpost = S_lik + self._S_logprior[:, None]
                normC = np.mean(S_logpost, axis=0)
                S_logpost = S_logpost - normC[None, :]
                S_post = np.exp(S_logpost)
                S_post /= np.sum(S_post, axis=0)[None, :]
                S_post_mean = np.dot(self._S_grid, S_post)
                S_post_sd = np.sqrt(
                    np.dot(np.power(self._S_grid, 2), S_post) - np.power(S_post_mean, 2)
                )
                S_cdf = np.cumsum(S_post, axis=0)
                S_lo = self._S_grid[np.argmin(np.abs(S_cdf - 0.025), axis=0)]
                S_hi = self._S_grid[np.argmin(np.abs(S_cdf - 0.975), axis=0)]
                i_S_0 = np.argmin(abs(self._S_grid))
                S_lfsr = np.where(S_mle > 0, S_cdf[i_S_0], 1 - S_cdf[i_S_0])
                results["s"]["pmean"] = S_post_mean
                results["s"]["psd"] = S_post_sd
                results["s"]["loS"] = S_lo
                results["s"]["hiS"] = S_hi
                results["s"]["lfsr"] = S_lfsr
            ## compute lfsr
            ## find S grid point closest to zero
            results["s"]["lik"] = S_lik
            results["s"]["grid"] = self._S_grid
            results["s"]["mle"] = S_mle
            results["s"]["95_ci_left"] = seimin
            results["s"]["95_ci_right"] = seimax
            results["s"]["lrt"] = lrt
            results["s"]["pvalue"] = lrt_p_value
            results["s"]["mle"] = S_mle
        return results

    def get_transitions(self, N, deltat):
        trajectories = []
        if self.transition_model == TransModel.BwS:
            for s in self._S_grid:
                traj = []
                for dt in deltat:
                    mom = self.mf.get_moments(N=N, s=s, h=0.5, dt=dt)
                    Q = hmm.transition_bws(self._X_grid, mom)
                    traj.append(Q)
                trajectories.append(traj)
        elif self.transition_model == TransModel.WF:
            for s in self._S_grid:
                traj = []
                for dt in deltat:
                    Q = hmm.transition_wf(N=N, s=s, h=0.5, dt=dt)
                    traj.append(Q)
                trajectories.append(traj)
        trajectories = np.array(trajectories)
        return trajectories

    def estimate_s_given_N(self, N, emissions, deltat):
        with Timer("\tBuild Transitions", verbosity=self.verbosity):
            trajectories = self.get_transitions(N, deltat)
        with Timer("\tCompute likelihoods", verbosity=self.verbosity):
            S_lik = hmm.hmm_fwd_loglik(trajectories, emissions)
        return S_lik

    def estimate_Ne(self, emissions, deltat, sel=0):
        Ne_lik = {}
        ## coarse estimation on a log scale
        if self.verbosity >= 2:
            print("Coarse Grid estimation")
        N_coarse = np.logspace(1, 6, 20, dtype=int)
        with Timer("\tBuild Transitions", verbosity=self.verbosity):
            trajectories = []
            for N in N_coarse:
                traj = []
                for dt in deltat:
                    mom = self.mf.get_moments(N=N, s=sel, h=0.5, dt=dt)
                    Q = hmm.transition_bws(self._X_grid, mom)
                    traj.append(Q)
                trajectories.append(traj)
            trajectories = np.array(trajectories)
        with Timer("\tCompute likelihoods", verbosity=self.verbosity):
            lik = hmm.hmm_fwd_loglik(trajectories, emissions)
            lik_N = np.sum(lik, axis=1)
        ibest = np.argmax(lik_N)
        imin = max(ibest - 1, 0)
        imax = min(ibest + 1, N_coarse.shape[0] - 1)
        for i, N in enumerate(N_coarse):
            Ne_lik[N] = lik_N[i]
        if self.verbosity >= 2:
            print(f"Fine Grid estimation in {N_coarse[imin]} , {N_coarse[imax]}")
        N_fine = np.unique(
            np.logspace(
                np.log10(N_coarse[imin]),
                np.log10(N_coarse[imax]),
                self.N_grid_size,
                dtype=int,
            )
        )
        if self.verbosity >= 3:
            print(N_fine)
        with Timer("\tBuild Transitions", verbosity=self.verbosity):
            trajectories = []
            for N in N_fine:
                traj = []
                for dt in deltat:
                    mom = self.mf.get_moments(N=N, s=sel, h=0.5, dt=dt)
                    Q = hmm.transition_bws(self._X_grid, mom)
                    traj.append(Q)
                trajectories.append(traj)
            trajectories = np.array(trajectories)
        with Timer("\tCompute likelihoods", verbosity=self.verbosity):
            lik = hmm.hmm_fwd_loglik(trajectories, emissions)
            lik_N = np.sum(lik, axis=1)
        for i, N in enumerate(N_fine):
            Ne_lik[N] = lik_N[i]
        return Ne_lik


def main_wf():
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", type=str)
    parser.add_argument("--min", type=int, default=10, help="Lower bound for Ne")
    parser.add_argument("--max", type=int, default=500, help="Upper bound for Ne")
    parser.add_argument(
        "--tol", type=int, default=10, help="Tolerance for Ne estimation"
    )
    parser.add_argument(
        "-ft",
        "--file_type",
        type=str,
        default="baypass",
        help=argparse.SUPPRESS,
        choices=["compareHMM", "baypass"],
    )
    parser.add_argument("-v", action="count", default=0)
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Disable every log in stdout ",
    )
    parser.add_argument(
        "--output",
        type=str,
        nargs="?",
        const="",
        default=None,
        help="Specify a different output, default is prefix. If OUTPUT is set "
        "empty, no file will be created and some data will be lost. If "
        'OUTPUT is set to "/dev/stdout" or just "stdout", the '
        "information in the files will be printed on terminal",
    )
    args = parser.parse_args()
    verbosity = 3 if args.v == 0 else args.v
    if args.quiet:
        if args.v > 0:
            print(
                f"Warning: you specified a verbosity of {verbosity}, which is"
                " incompatible with the --quiet option. The quiet option will "
                "therefore be ignored."
            )
        else:
            verbosity = 0
    if args.output is None:
        output = f"{args.prefix}"
    elif args.output == "None" or args.output == "":
        output = None
    else:
        output = args.output

    ## Read data in
    if args.file_type == "compareHMM":
        my_gts = GeneticTimeSeries.from_compareHMM(args.prefix)
    elif args.file_type == "baypass":
        my_gts = GeneticTimeSeries.from_baypass(args.prefix)
    if verbosity >= 2:
        print(my_gts)

    ## Analyse
    my_analyzer = GTS_Analyser(model=TransModel.WF, verbosity=verbosity)
    my_analyzer.S_grid_size = 1
    my_analyzer._S_grid = np.zeros(1)

    ## Find maximum using Golden-section search
    ## https://en.wikipedia.org/wiki/Golden-section_search

    Nl = args.min
    Nr = args.max
    gr = (np.sqrt(5) + 1) / 2
    search_results = {}

    ## f(Nl)
    res_l = my_analyzer.analyze(my_gts, Ne=Nl)
    lik_l = np.sum(res_l["s"]["lik"])
    search_results[Nl] = lik_l
    ## f(Nr)
    res_r = my_analyzer.analyze(my_gts, Ne=Nr)
    lik_r = np.sum(res_r["s"]["lik"])
    search_results[Nr] = lik_r

    while (Nr - Nl) > args.tol:
        new_Nl = int(Nr - (Nr - Nl) / gr)
        new_Nr = int(Nl + (Nr - Nl) / gr)
        ## f(new_Nl)
        res_l = my_analyzer.analyze(my_gts, Ne=new_Nl)
        lik_l = np.sum(res_l["s"]["lik"])
        search_results[new_Nl] = lik_l
        ## f(new_Nr)
        res_r = my_analyzer.analyze(my_gts, Ne=new_Nr)
        lik_r = np.sum(res_r["s"]["lik"])
        search_results[new_Nr] = lik_r
        if verbosity >= 2:
            print(new_Nl, lik_l)
            print(new_Nr, lik_r)
        if lik_l > lik_r:
            Nr = new_Nr
        else:
            Nl = new_Nl
        if verbosity >= 1:
            print(f"*** Search: {Nl} -- {Nr} {search_results[Nl]},{search_results[Nr]}")

    if output != None:
        if output == "/dev/stdout" or output == "stdout":
            filename_N = output
        else:
            filename_N = f"{output}.snt.wf.N"

        with open(filename_N, "w") as f:
            mle = max(search_results, key=search_results.get)
            mle_lik = max(search_results.values())
            nei = [k for k, v in search_results.items() if v > mle_lik - 2]
            it_left = min(nei)
            it_right = max(nei)
            print(f"# N MLE : {mle}", file=f)
            print(f"# MLE log-likelihood : {mle_lik}", file=f)
            print(f"# N 95% interval : {it_left} -- {it_right}", file=f)

            print("Ne llik", file=f)
            for k, v in sorted(search_results.items(), key=lambda x: x[0]):
                print(k, v, file=f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", type=str)
    parser.add_argument(
        "-N",
        "--Ne",
        type=int,
        default=None,
        help="Set effective population size to NE (turns off Ne estimation)",
    )
    parser.add_argument(
        "-S",
        "--Sesti",
        action="store_true",
        default=False,
        help="Enable estimation of selection coefficients",
    )
    parser.add_argument(
        "-ft",
        "--file_type",
        type=str,
        default="baypass",
        help=argparse.SUPPRESS,
        choices=["compareHMM", "baypass"],
    )
    parser.add_argument(
        "-M", "--model", type=str, choices=[m.value for m in TransModel]
    )
    parser.add_argument("-v", action="count", default=0)
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Disable every log in stdout ",
    )
    parser.add_argument(
        "--output",
        type=str,
        nargs="?",
        const="",
        default=None,
        help="Specify a different output, default is prefix. If OUTPUT is set "
        "empty, no file will be created and some data will be lost. If "
        'OUTPUT is set to "/dev/stdout" or just "stdout", the '
        "information in the files will be printed on terminal",
    )
    parser.add_argument(
        "-sl",
        "--s_lik",
        action="store_true",
        default=False,
        help="If set, print the content of S_lik (a Matrix of size l x "
        "S_grid_size, with l the number of loci) in 'OUTPUT.snt.S.loglik'."
        "Warning: this option may produce very large files.",
    )
    args = parser.parse_args()
    prefix = args.prefix
    file_type = args.file_type

    verbosity = 3 if args.v == 0 else args.v
    if args.quiet:
        if args.v > 0:
            print(
                f"Warning: you specified a verbosity of {verbosity}, which is"
                " incompatible with the --quiet option. The quiet option will "
                "therefore be ignored."
            )
        else:
            verbosity = 0

    if args.output is None:
        output = f"{prefix}"
    elif args.output == "None" or args.output == "":
        output = None
    else:
        output = args.output

    if args.Ne is not None and not args.Sesti:
        print(
            "Ne already known and no estimation of s requested, no computation to be done"
        )
        sys.exit(0)

    if args.model == "WF" and args.Ne is None:
        print("Ne is required for the Wright Fisher transition model")
        sys.exit(1)

    ## Read data in
    if file_type == "compareHMM":
        my_gts = GeneticTimeSeries.from_compareHMM(prefix)
    elif file_type == "baypass":
        my_gts = GeneticTimeSeries.from_baypass(prefix)
    if verbosity >= 2:
        print(my_gts)

    ## Analyse
    if args.Ne is None:
        my_analyzer = GTS_Analyser(model=args.model, verbosity=verbosity)
    else:
        my_analyzer = GTS_Analyser(model=args.model, N_grid_size=0, verbosity=verbosity)
    if verbosity >= 2:
        print(my_analyzer)
    results = my_analyzer.analyze(my_gts, Ne=args.Ne, Sesti=args.Sesti)

    ## write results
    if output != None:
        if output == "/dev/stdout" or output == "stdout":
            filename_N = output
            filename_S = output
        else:
            filename_N = f"{output}.snt.N"
            filename_S = (
                f"{output}.snt.wf.S" if (args.model == "WF") else f"{output}.snt.S"
            )

        if args.Ne is None:
            with open(filename_N, "w") as f:
                print(f"# N MLE : {results['Ne']['bestN']}", file=f)
                print(f"# MLE log-likelihood : {results['Ne']['bestL']}", file=f)
                print(
                    f"# N 95% interval : "
                    f"{results['Ne']['loN']} -- {results['Ne']['hiN']}",
                    file=f,
                )
                print("Ne loglik", file=f)
                for k, v in sorted(results["Ne"]["lik"].items(), key=lambda x: x[0]):
                    print(k, v, file=f)
        if args.Sesti:
            with open(filename_S, "w") as f:
                print(
                    "loc mle ci_95_left ci_95_right lrt pvalue pmean psd lo hi lfsr",
                    file=f,
                )
                res = results["s"]
                for l in range(my_gts.L):
                    print(
                        l,
                        res["mle"][l],
                        res["95_ci_left"][l],
                        res["95_ci_right"][l],
                        res["lrt"][l],
                        res["pvalue"][l],
                        res["pmean"][l],
                        res["psd"][l],
                        res["loS"][l],
                        res["hiS"][l],
                        res["lfsr"][l],
                        file=f,
                    )
            if args.s_lik:
                np.savetxt(
                    f"{filename_S}.loglik",
                    results["s"]["lik"].T,
                    header=" ".join(map(str, results["s"]["grid"])),
                    fmt="%.5f",
                )
    else:
        if args.Sesti and verbosity >= 2:
            print(
                "Estimation of S was computed, but the no output option is on."
                " Please specify an output file or keep the default output if you"
                " want to retrieve the results."
            )

    print("All done")
    return
