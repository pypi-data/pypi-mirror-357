import pytest
import arviz as az

from guts_base import LPxEstimator, GutsBase
from mempy.model import RED_SD_DA, RED_IT

def construct_sim(scenario, simulation_class):
    """Helper function to construct simulations for debugging"""
    sim = simulation_class(f"scenarios/{scenario}/settings.cfg")

    # this sets a different output directory
    sim.config.case_study.scenario = "testing"
    sim.setup()
    return sim


# List test scenarios and simulations
@pytest.fixture(scope="session", params=[
    # (GutsBase, "red_sd"),
])
def sim_and_scenario(request):
    return request.param


# Derive simulations for testing from fixtures
@pytest.fixture(scope="session")
def sim(sim_and_scenario):
    simulation_class, scenario = sim_and_scenario
    yield construct_sim(scenario, simulation_class)


# run tests with the Simulation fixtures
def test_setup(sim):
    """Tests the construction method"""
    assert True


def test_simulation(sim):
    """Tests if a forward simulation pass can be computed"""
    sim.dispatch_constructor()
    evaluator = sim.dispatch()
    evaluator()
    evaluator.results

    assert True
            

@pytest.mark.slow
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference(sim: GutsBase, backend):
    """Tests if prior predictions can be computed for arbitrary backends"""
    sim.dispatch_constructor()
    sim.set_inferer(backend)

    sim.config.inference.n_predictions = 2
    sim.prior_predictive_checks()
    
    sim.config.inference_numpyro.kernel = "svi"
    sim.config.inference_numpyro.svi_iterations = 10
    sim.config.inference_numpyro.svi_learning_rate = 0.05
    sim.config.inference_numpyro.draws = 10
    sim.config.inference.n_predictions = 10

    sim.inferer.run()

    sim.inferer.idata
    sim.inferer.store_results()

    sim.posterior_predictive_checks()

    sim.inferer.load_results()
    sim.config.report.debug_report = True
    sim.report()

@pytest.mark.slow
@pytest.mark.parametrize("model,dataset,idata,id", [
    (RED_SD_DA, "Fit_Data_Cloeon_final.xlsx", "idata_red_sd_da.nc", "FLUA.5"),
    (RED_IT, "ringtest_A_IT.xlsx", "idata_red_it.nc", "T 1")
])
def test_lp50(model, dataset, idata, id):
    pytest.skip()
    sim=construct_sim(dataset=dataset, model=model)
    sim.set_inferer("numpyro")
    sim.inferer.idata = az.from_netcdf(f"data/testing/{idata}")

    lpx_estimator = LPxEstimator(sim=sim, id=id)

    theta_mean = lpx_estimator.sim.inferer.idata.posterior.mean(("chain", "draw"))
    theta_mean = {k: v["data"] for k, v in theta_mean.to_dict()["data_vars"].items()}

    lpx_estimator._loss(log_factor=0.0, theta=theta_mean)

    lpx_estimator.plot_loss_curve()

    lpx_estimator.estimate(mode="mean")
    lpx_estimator.plot_profile_and_effect()
    lpx_estimator.estimate(mode="manual", parameters=lpx_estimator._posterior_mean())
    lpx_estimator.plot_profile_and_effect(parameters=lpx_estimator._posterior_mean())

    lpx_estimator.estimate(mode="draws")
    lpx_estimator.plot_profile_and_effect()

    lpx_estimator.results
    lpx_estimator.results_full


if __name__ == "__main__":
    # test_inference(sim=construct_sim("test_scenario_v2", Simulation_v2), backend="numpyro")
    test_inference(sim=construct_sim("red_it", GutsBase), backend="numpyro",)
