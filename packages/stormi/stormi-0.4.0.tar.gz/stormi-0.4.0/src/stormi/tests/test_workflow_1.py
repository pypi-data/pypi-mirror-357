import anndata as ad
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

###############################################################################
# Fixtures (non‑amortized workflow only)
###############################################################################
# Monkey-patch Gamma distribution to skip validate_args in tests
from numpyro.distributions.continuous import Gamma
from numpyro.infer.autoguide import AutoNormal
from numpyro.infer.initialization import init_to_mean

import stormi.posterior as posterior_module
from stormi.models.RNA_1layer import model, prepare_model_input, sample_prior
from stormi.plotting import plot_elbo_loss, predictions_vs_data
from stormi.train import train_svi

_orig_gamma_init = Gamma.__init__


def _no_validate_gamma_init(self, concentration, rate, validate_args=True):
    # force validate_args to False
    _orig_gamma_init(self, concentration, rate, validate_args=False)


Gamma.__init__ = _no_validate_gamma_init


@pytest.fixture(scope="module")
def adata_rna():
    """Tiny synthetic AnnData with 2 cells × 3 genes."""
    np.random.seed(0)
    genes = [f"gene{i}" for i in range(1, 3)]  # 2 genes
    cells = [f"cell{i}" for i in range(1, 3)]  # 2 cells

    spliced = np.random.randint(0, 100, size=(len(cells), len(genes)))
    unspliced = np.random.randint(0, 100, size=(len(cells), len(genes)))

    obs = pd.DataFrame(
        {
            "n_cells": np.random.randint(1, 11, size=len(cells)),
            "day_float": np.random.rand(len(cells)) * 100,
            "experiment": ["expA", "expB"][: len(cells)],
        },
        index=cells,
    )
    var = pd.DataFrame(index=genes)

    adata = ad.AnnData(X=spliced, obs=obs, var=var)
    adata.layers["spliced"] = spliced
    adata.layers["unspliced"] = unspliced
    adata.raw = adata
    return adata


@pytest.fixture(scope="module")
def tf_list():
    return ["gene1", "gene2"]


@pytest.fixture
def model_input(adata_rna, tf_list):
    return prepare_model_input(
        adata_rna,
        tf_list,
        n_cells_col="n_cells",
        prior_time_col="day_float",
        batch_annotation="experiment",
    )


@pytest.fixture(scope="module")
def guide():
    """Non‑amortized AutoNormal guide."""
    return AutoNormal(model, init_loc_fn=init_to_mean)


@pytest.fixture
def prior_samples(model_input):
    return sample_prior(model, model_input, num_samples=1)


@pytest.fixture
def svi_results(guide, model_input):
    """Run a single SVI step and return artefacts."""
    guide, svi, svi_state, losses, updated_mi = train_svi(
        model,
        guide,
        model_input=model_input,
        max_iterations=2,
        min_lr=1e-3,
        max_lr=1e-2,
        ramp_up_fraction=0.5,
        log_interval=50,
        cell_batch_size=0,
        region_batch_size=0,
    )
    return guide, svi, svi_state, losses, updated_mi


###############################################################################
# Utility
###############################################################################


def _collapse_to_matrix(arr):
    """Return (cells, genes) matrix by averaging over extra axes."""
    while arr.ndim > 2:
        arr = arr.mean(axis=0)
    return arr


###############################################################################
# Tests
###############################################################################


def test_prior_shape(prior_samples, adata_rna):
    mu = prior_samples["mu"]
    assert sorted(mu.shape[-2:]) == sorted((adata_rna.n_obs, adata_rna.n_vars))


def test_predictions_vs_data_prior(prior_samples, model_input):
    observed = model_input["data"]
    preds = prior_samples["mu"]
    fig = predictions_vs_data(
        observed, preds, ylabel="Prior", title="Prior vs Data", min_value=0.0
    )
    assert isinstance(fig, Figure)


def test_svi_losses(svi_results):
    _, _, _, losses, _ = svi_results
    assert isinstance(losses, list) and losses


def test_posterior_shapes_and_plot(svi_results, adata_rna):
    guide, svi, svi_state, _, mi = svi_results
    posterior = posterior_module.extract_posterior_estimates(
        model,
        guide,
        svi,
        svi_state,
        quantiles=[0.05, 0.5, 0.95],
        num_samples=2,
        modes=[],
        model_input=mi,
        deterministic_sites=["predictions_rearranged", "T_c", "mu"],
    )
    mu_post = posterior["deterministic"]["mu"]
    assert sorted(mu_post.shape[-2:]) == sorted((adata_rna.n_obs, adata_rna.n_vars))

    obs = mi["data"]
    fig = predictions_vs_data(
        obs,
        mu_post,
        ylabel="Posterior",
        title="Post vs Data",
        min_value=0.0,
        log_norm=False,
    )
    assert isinstance(fig, Figure)
