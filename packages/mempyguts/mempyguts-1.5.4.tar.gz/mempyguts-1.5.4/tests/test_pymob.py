from typing import Tuple
import pytest
import numpy as np
import xarray as xr
from mempy.model import (
    RED_IT, RED_SD, RED_IT_DA, RED_SD_DA, RED_IT_IA, RED_SD_IA, Reduced,
    BufferGUTS_SD, BufferGUTS_IT, BufferGUTS_SD_DA, BufferGUTS_SD_CA, BufferGUTS_IT_DA, 
    BufferGUTS_IT_CA
)
from mempy.input_data import read_exposure_survival
from guts_base import PymobSimulator

# results are from Bürger and Focks 2025 (https://doi.org/10.1093/etojnl/vgae058) 
# supplementary material (Tab. 5.3)
OPENGUTS_ESTIMATES = dict(
    red_sd = xr.Dataset(dict(kd=0.712, m=2.89, b=0.619, hb=0.008)).to_array().sortby("variable"),
    red_it = xr.Dataset(dict(kd=0.789, m=5.36, beta=5.08, hb=0.025)).to_array().sortby("variable"),
    red_sd_da = None,
    red_sd_ia = None,
    red_it_da = None,
    red_it_ia = None,
    bufferguts_it = None,
    bufferguts_sd = None,
    bufferguts_sd_ca = None,
    bufferguts_sd_da = None,
    bufferguts_it_ca = None,
    bufferguts_it_da = None,
    # TODO: Define true parameters for red_sd_da
)

def read_data(file):
    data = read_exposure_survival(
        "data/", file, 
        survival_name="Survival",
        exposure_name="Exposure",
        visualize=False,
        with_raw_exposure_data=True
    )

    exposure_funcs, survival_data, num_expos, exposure_data = data
    info_dict = {}

    return exposure_funcs, survival_data, num_expos, info_dict, exposure_data


def construct_sim(dataset: Tuple, model: type):
    """Helper function to construct simulations for debugging"""
    _, survival_data, num_expos, _, exposure_data = read_data(file=dataset)

    if model in (RED_IT, RED_SD, BufferGUTS_SD, BufferGUTS_IT):
        _model = model()
    else:
        _model = model(num_expos=num_expos)

    sim = PymobSimulator.from_mempy(
        exposure_data=exposure_data,
        survival_data=survival_data,
        model=_model,
        output_directory="output/pymob/testing"
    )

    return sim


@pytest.fixture(scope="module", params=[
    ("ringtest_A_IT.xlsx", RED_IT),
    ("ringtest_A_SD.xlsx", RED_SD),
    ("Fit_Data_Cloeon_final.xlsx", RED_SD_DA,),
    ("Fit_Data_Cloeon_final.xlsx", RED_SD_IA,),
    ("Fit_Data_Cloeon_final.xlsx", RED_IT_DA,),
    ("Fit_Data_Cloeon_final.xlsx", RED_IT_IA,),
    ("osmia_contact_synthetic.xlsx", BufferGUTS_SD,),
    ("osmia_contact_synthetic.xlsx", BufferGUTS_IT,),
    ("osmia_multiexpo_synthetic.xlsx", BufferGUTS_SD_CA,),
    ("osmia_multiexpo_synthetic.xlsx", BufferGUTS_SD_DA,),
    ("osmia_multiexpo_synthetic.xlsx", BufferGUTS_IT_CA,),
    ("osmia_multiexpo_synthetic.xlsx", BufferGUTS_IT_DA,),
])
def dataset_and_model(request) -> Reduced:
    yield request.param


# Derive simulations for testing from fixtures
@pytest.fixture(scope="module")
def sim(dataset_and_model):
    dataset, model = dataset_and_model
    yield construct_sim(dataset=dataset, model=model)


# run tests with the Simulation fixtures
def test_setup(sim):
    """Tests the construction method"""
    assert True


def test_simulation(sim):
    """Tests if a forward simulation pass can be computed"""
    # sim.dispatch_constructor()
    evaluator = sim.dispatch()
    evaluator()
    evaluator.results

    assert True

@pytest.mark.slow
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference(sim: PymobSimulator, backend):
    """Tests if prior predictions can be computed for arbitrary backends"""

    sim.set_inferer(backend)

    sim.prior_predictive_checks()
    sim.config.inference_numpyro.svi_iterations = 100
    sim.config.inference_numpyro.draws = 250
    sim.inferer.run()

    sim.posterior_predictive_checks()

    sim.config.report.debug_report = True
    sim.report()

    # test if inferer converged on the true estmiates
    pymob_estimates = sim.inferer.idata.posterior.mean(("chain", "draw")).to_array().sortby("variable")
    openguts_estimates = OPENGUTS_ESTIMATES[sim.config.simulation.model.lower()]

    if openguts_estimates is None:
        # this explicitly skips testing the results, since they are not available,
        # but does not fail the test.
        pytest.skip()

    np.testing.assert_allclose(pymob_estimates, openguts_estimates, rtol=0.05, atol=0.1)


if __name__ == "__main__":
    # test_simulation(sim=construct_sim(data_ringtest, model=RED_IT))
    test_inference(sim=construct_sim(dataset="Fit_Data_Cloeon_final.xlsx", model=BufferGUTS_SD_DA), backend="numpyro")
    # test_inference(sim=construct_sim(dataset="Fit_Data_Cloeon_final.xlsx", model=RED_IT_IA), backend="numpyro")
    # test_inference(sim=construct_sim(dataset="paula_data/Dimethoate_Clothianidin_Propiconazole_constant_plsed - muegL.xlsx", model=RED_IT_IA), backend="numpyro")