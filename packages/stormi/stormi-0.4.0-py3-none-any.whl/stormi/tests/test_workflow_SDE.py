import anndata as ad
import numpy as np
import pandas as pd
import pytest
import scanpy as sc
from matplotlib.figure import Figure

###############################################################################
# Monkey-patch Gamma distribution to skip validate_args in tests
from numpyro.distributions.continuous import Gamma

_orig_gamma_init = Gamma.__init__


def _no_validate_gamma_init(self, concentration, rate, validate_args=True):
    _orig_gamma_init(self, concentration, rate, validate_args=False)


Gamma.__init__ = _no_validate_gamma_init
###############################################################################

from numpyro.infer.initialization import init_to_mean

import stormi.posterior as posterior_module
from stormi.guides.AmortizedNormal import AmortizedNormal, warm_up_guide
from stormi.models.RNA_2layers_MultiplePaths_SDE import (
    model,
    prepare_model_input,
)
from stormi.plotting import plot_elbo_loss, posterior_data_geneset_multipath
from stormi.train import train_svi_jit

###############################################################################
# Fixtures
###############################################################################


@pytest.fixture(scope="module")
def adata_rna():
    """
    Synthetic AnnData with a flexible number of cells × genes,
    including all obs columns needed for prepare_model_input.
    """
    np.random.seed(0)
    n_cells = 5
    n_genes = 5

    genes = [f"gene{i}" for i in range(1, n_genes + 1)]
    cells = [f"cell{i}" for i in range(1, n_cells + 1)]

    # Simulate expression counts (we'll treat both spliced/unspliced the same here)
    X = np.random.randint(0, 100, size=(n_cells, n_genes))

    # Construct obs with required columns:
    n_cells_col = np.random.randint(1, 11, size=n_cells)
    day_float = np.random.rand(n_cells) * 100

    # Ensure at least one “Mesoderm” and one “CM”
    available_batches = ["expA", "expB", "expC"]
    exper = ["expA", "expB"] if n_cells >= 2 else ["expA"]
    if len(exper) < n_cells:
        exper += list(np.random.choice(available_batches, size=n_cells - len(exper)))
    exper = exper[:n_cells]

    cluster_labels = ["Mesoderm", "CM"] if n_cells >= 2 else ["Mesoderm"]
    all_states = ["Mesoderm", "CM", "EC", "Fib"]
    if len(cluster_labels) < n_cells:
        cluster_labels += list(
            np.random.choice(all_states, size=n_cells - len(cluster_labels))
        )
    cluster_labels = cluster_labels[:n_cells]

    obs = pd.DataFrame(
        {
            "n_cells": n_cells_col,
            "day_float": day_float,
            "experiment": exper,
            "RNA_cell_type": cluster_labels,
        },
        index=cells,
    )

    var = pd.DataFrame(index=genes)
    adata = ad.AnnData(X=X, obs=obs, var=var)
    # Duplicate X into “spliced” and “unspliced” layers so that prepare_model_input sees a 3D structure
    adata.layers["spliced"] = X.copy()
    adata.layers["unspliced"] = X.copy()
    adata.raw = adata
    return adata


@pytest.fixture(scope="module")
def tf_list():
    return ["gene1", "gene2"]


@pytest.fixture(scope="module")
def model_input(adata_rna, tf_list):
    return prepare_model_input(
        adata_rna,
        tf_list,
        n_cells_col="n_cells",
        prior_time_col="day_float",
        batch_annotation="experiment",
        terminal_states=["CM", "EC", "Fib"],
        initial_states=["Mesoderm"],
        cluster_key="RNA_cell_type",
    )


@pytest.fixture(scope="module")
def guide(model_input):
    """
    Build AmortizedNormal guide via warm-up.
    """
    warm_params = warm_up_guide(model, model_input)
    return AmortizedNormal(model, init_net_params=warm_params, init_loc_fn=init_to_mean)


@pytest.fixture(scope="module")
def svi_results(guide, model_input):
    """
    Run a couple of SVI iterations and return:
    (guide, svi, svi_state, losses, updated_model_input)
    """
    num_cells = model_input["data"].shape[0]
    guide_out, svi, svi_state, losses, updated_mi = train_svi_jit(
        model,
        guide,
        model_input,
        max_iterations=2,
        cell_batch_size=4,
        log_interval=1,
        min_lr=1e-3,
        max_lr=1e-2,
        ramp_up_fraction=0.5,
    )
    return guide_out, svi, svi_state, losses, updated_mi


###############################################################################
# Tests
###############################################################################


def test_svi_losses(svi_results):
    """
    Ensure losses is a non-empty list.
    """
    _, _, _, losses, _ = svi_results
    assert isinstance(losses, list)
    assert len(losses) > 0


def test_plot_elbo_loss(svi_results):
    """
    Test that plot_elbo_loss returns either None or a Figure.
    """
    _, _, _, losses, _ = svi_results
    fig = plot_elbo_loss(losses)
    assert fig is None or isinstance(fig, Figure)


def test_posterior_extraction(svi_results, adata_rna, tf_list):
    """
    Extract posterior
    """
    guide_out, svi, svi_state, _, mi = svi_results
    posterior = posterior_module.extract_posterior_estimates(
        model,
        guide_out,
        svi,
        svi_state,
        quantiles=[],
        num_samples=0,
        modes=[1],
        model_input=mi,
        deterministic_sites=[
            "T_c",
            "mu",
            "normalizing_term",
            "additive_term",
            "sol_at_cells",
            "path_weights",
        ],
    )
