import warnings
from functools import partial
import numpy as np
import xarray as xr
from typing import Literal, Optional, Dict, List
import pandas as pd
from scipy.optimize import minimize
from matplotlib import pyplot as plt
from tqdm import tqdm

from pymob import SimulationBase

class ECxEstimator:
    """Estimates the exposure level that corresponds to a given effect. The algorithm 
    operates by varying a given exposure profile (x_in)
    """
    _name = "EC"

    def __init__(
        self, 
        sim: SimulationBase, 
        effect: str, 
        x: float=0.5,
        id: Optional[str]=None, 
        time: Optional[float]=None, 
        x_in: Optional[xr.Dataset]=None, 
    ):
        self.sim = sim.copy()
        self.time = time
        self.x = x
        self.id = id
        self.effect = effect
        self._mode = None

        if id is None:
            self.sim.coordinates["id"] = [self.sim.coordinates["id"][0]]
        else:
            self.sim.coordinates["id"] = [id]

        self.sim.model_parameters["x_in"] = x_in

        self.sim.config.data_structure.survival.observed = False
        self.sim.observations = self.sim.observations.sel(id=self.sim.coordinates["id"])

        # fix time after observations have been set
        self.sim.coordinates["time"] = [time]

        self.sim.model_parameters["y0"] = self.sim.parse_input("y0", drop_dims="time")
        self.sim.dispatch_constructor()


    
    def _evaluate(self, factor, theta):
        evaluator = self.sim.dispatch(
            theta=theta, 
            x_in=self.sim.validate_model_input(self.sim.model_parameters["x_in"] * factor)
        )
        evaluator()
        return evaluator

    def _loss(self, log_factor, theta):
        # exponentiate the log factor
        factor = np.exp(log_factor)

        e = self._evaluate(factor, theta)
        s = e.results.sel(time=self.time)[self.effect].values

        return (s - (1 - self.x)) ** 2

    def _posterior_mean(self):
        mean = self.sim.inferer.idata.posterior.mean(("chain", "draw"))
        mean = {k: v["data"] for k, v in mean.to_dict()["data_vars"].items()}
        return mean

    def _posterior_sample(self, i):
        posterior_stacked = self.sim.inferer.idata.posterior.stack(
            sample=("chain", "draw")
        )
        sample = posterior_stacked.isel(sample=i)
        sample = {k: v["data"] for k, v in sample.to_dict()["data_vars"].items()}
        return sample

    def plot_loss_curve(self):
        posterior_mean = self._posterior_mean()

        factor = np.linspace(-2,2, 100)
        y = list(map(partial(self._loss, theta=posterior_mean), factor))

        fig, ax = plt.subplots(1,1, sharey=True, figsize=(4, 3))
        ax.plot(
            np.exp(factor), y, 
            color="black",
            label=f"$\ell = S(t={self.time},x_{{in}}=C_{{ext}} \cdot \phi) - {self.x}$"
        )
        ax.set_ylabel("Loss ($\ell$)")
        ax.set_xlabel("Multiplication factor ($\phi$)")
        ax.set_title(f"ID: {self.sim.coordinates['id'][0]}")
        ax.set_ylim(0, np.max(y) * 1.25)
        ax.legend(frameon=False)
        fig.tight_layout()

    def estimate(
        self, 
        mode: Literal["draws", "mean", "manual"] = "draws", 
        draws: Optional[int] = None, 
        parameters: Optional[Dict[str,float|List[float]]] = None,
        log_x0: float = 0.0, 
        accept_tol: float = 1e-5, 
        optimizer_tol: float = 1e-5,
        method: str = "cobyla", 
        **optimizer_kwargs
    ):
        """The minimizer for the EC_x operates on the unbounded linear scale, estimating 
        the log-modification factor. Converted to the linear scale by factor=exp(x), the 
        profile modification factor is obtained.

        Using x0=0.0 means optimization will start on the linear scale at the unmodified 
        exposure profile. Using the log scale for optimization will provide much smoother
        optimization performance because multiplicative steps on the log scale require 
        much less adaptation.

        Parameters
        ----------

        mode : Literal['draws', 'mean', 'manual']
            mode of estimation. mode='mean' takes the mean of the posterior and estimate
            the ECx for this singular value. mode='draws' takes samples from the posterior
            and estimate the ECx for each of the parameter draws. mode='manual' takes
            a parameter set (Dict) in the parameters argument and uses that for estimation. 
            Default: 'draws'
        
        draws : int
            Number of draws to take from the posterior. Only takes effect if mode='draw'.
            Raises an exception if draws < 100, because this is insufficient for a 
            reasonable uncertainty estimate. Default: None (using all samples from the
            posterior)
        
        parameters : Dict[str,float|list[float]]
            a parameter dictionary passed used as model parameters for finding the ECx
            value. Default: None

        log_x0 : float
            the starting value for the multiplication factor of the exposure profile for
            the minimization algorithm. This value is on the log scale. This means, 
            exp(log_x0=0.0) = 1.0, which means that the log_x0=0.0 will start at an
            unmodified exposure profile. Default: 0.0
        
        accept_tol : float
            After optimization is finished, accept_tol is used to assess if the loss
            function for the individual draws exceed a tolerance. These results are
            discarded and a warning is emitted. This is to assert that no faulty optimization
            results enter the estimate. Default: 1e-5
        
        optimizer_tol : float
            Tolerance limit for the minimzer to stop optimization. Default 1e-5

        method : str
            Minization algorithm. See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
            Default: 'cobyla'
        
        optimizer_kwargs :
            Additional arguments to pass to the optimizer

        """
        x0_tries = np.array([0.0, -1.0, 1.0, -2.0, 2.0]) + log_x0

        if mode == "draws":
            if draws is None:
                draws = (
                    self.sim.inferer.idata.posterior.sizes["chain"] * 
                    self.sim.inferer.idata.posterior.sizes["draw"]
                )
            elif draws < 100:
                raise ValueError(
                    "draws must be larger than 100. Preferably > 1000. "
                    f"If you don't want uncertainty assessment of the {self._name} "
                    "estimates, use mode='mean'"
                )
            else:
                pass

        elif mode == "mean":
            draws = 1
        elif mode == "manual":
            draws = 1
            if parameters is None:
                raise ValueError(
                    "parameters need to be provided if mode='manual'"
                )
        else:
            raise NotImplementedError(
                f"Bad mode: {mode}. Mode must be one 'mean' or 'draws'"
            )

        self._mode = mode
        mult_factor = []
        loss = []
        iterations = []
        for i in tqdm(range(draws)):
            if mode == "draws":
                sample = self._posterior_sample(i)
            elif mode == "mean":
                sample = self._posterior_mean()
            elif mode == "manual":
                sample = parameters
            else: 
                raise NotImplementedError(
                    f"Bad mode: {mode}. Mode must be one 'mean' or 'draws'"
                )

            success = False
            iteration = 0
            while not success and iteration < len(x0_tries):
                opt_res = minimize(
                    self._loss, x0=x0_tries[iteration], 
                    method=method,
                    tol=optimizer_tol,
                    args=(sample,),
                    **optimizer_kwargs
                ) 

                success = opt_res.fun < accept_tol

            # convert to linear scale from log scale
            factor = np.exp(opt_res.x)

            mult_factor.extend(factor)
            iterations.append(iteration)
            loss.append(opt_res.fun)

        res_full = pd.DataFrame(dict(factor = mult_factor, loss=loss, retries=iterations))
        if sum(res_full.loss >= accept_tol) > 0:
            warnings.warn(
                f"Not all optimizations converged on the {self._name}_{self.x}. " +
                "Adjust starting values and method")
            print(res_full)
        
        res = res_full.loc[res_full.loss < accept_tol,:]

        summary = {
            "mean": np.round(np.mean(res.factor.values), 4),
            "q05": np.round(np.quantile(res.factor.values, 0.05), 4),
            "q95": np.round(np.quantile(res.factor.values, 0.95), 4),
            "std": np.round(np.std(res.factor.values), 4),
            "cv": np.round(np.std(res.factor.values)/np.mean(res.factor.values), 2),
        }

        self.results = pd.Series(summary)
        self.results_full = res_full

        print("{name}_{x}".format(name=self._name, x=int(self.x * 100),))
        print(self.results)
        print("\n")

    def plot_profile_and_effect(
        self,
        parameters: Optional[Dict[str,float|List[float]]] = None
    ):
        coordinates_backup = self.sim.coordinates["time"].copy()

        self.sim.coordinates["time"] = np.linspace(0, self.time, 100)
        self.sim.dispatch_constructor()

        if self._mode is None:
            raise RuntimeError(
                "Run .estimate() before plot_profile_and_effect()"
            )
        elif self._mode == "mean" or self._mode == "draws":
            e_new = self._evaluate(factor=self.results["mean"], theta=self._posterior_mean())
            e_old = self._evaluate(factor=1.0, theta=self._posterior_mean())
        elif self._mode == "manual":
            if parameters is None:
                raise RuntimeError(
                    f"If {self._name}_x was estimated using manual mode, parameters must "+
                    "also be provided here."
                )
            e_new = self._evaluate(factor=self.results["mean"], theta=parameters)
            e_old = self._evaluate(factor=1.0, theta=parameters)
    
        extra_dim = [k for k in list(e_old.results.coords.keys()) if k not in ["time", "id"]]

        if len(extra_dim) > 0:
            labels_old = [
                f"{l} (original)" for l 
                in e_old.results.coords[extra_dim[0]].values
            ]
            labels_new = [
                f"{l} (modified)" for l 
                in e_new.results.coords[extra_dim[0]].values
            ]
        else:
            labels_old = "original"
            labels_new = "modified"



        fig, (ax1, ax2) = plt.subplots(2,1, height_ratios=[1,3], sharex=True)
        ax1.plot(
            e_old.results.time, e_old.results.exposure.isel(id=0), 
            ls="--", label=labels_old,
        )
        ax1.set_prop_cycle(None)
        ax1.plot(
            e_new.results.time, e_new.results.exposure.isel(id=0), 
            label=labels_new
        )


        ax2.plot(
            e_new.results.time, e_new.results.survival.isel(id=0), 
            color="black", ls="--", label="modified"
        )
        ax1.set_prop_cycle(None)

        ax2.plot(
            e_old.results.time, e_old.results.survival.isel(id=0), 
            color="black", ls="-", label="original"
        )
        ax2.hlines(self.x, e_new.results.time[0], self.time, color="grey")
        ax1.set_ylabel("Exposure")
        ax2.set_ylabel("Survival")
        ax2.set_xlabel("Time")
        ax1.legend()
        ax2.legend()
        ax2.set_xlim(0, None)
        ax1.set_ylim(0, None)
        ax2.set_ylim(0, None)
        fig.tight_layout()

        self.sim.coordinates["time"] = coordinates_backup
        self.sim.dispatch_constructor()

    

class LPxEstimator(ECxEstimator):
    """
    the LPx is computed, using the existing exposure profile for 
    the specified ID and estimating the multiplication factor for the profile that results
    in an effect of X %
    """
    _name = "LP"

    def __init__(
        self, 
        sim: SimulationBase, 
        id: str,
        x: float=0.5
    ):
        x_in = sim.model_parameters["x_in"].sel(id=[id])
        time = sim.coordinates["time"][-1]
        super().__init__(sim=sim, effect="survival", x=x, id=id, time=time, x_in=x_in)