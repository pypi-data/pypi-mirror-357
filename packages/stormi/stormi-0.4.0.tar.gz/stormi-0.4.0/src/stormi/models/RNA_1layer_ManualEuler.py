from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
from anndata import AnnData
from beartype import beartype
from numpyro.handlers import scale
from scipy import sparse

from .RNA_utils import sample_prior
from .utils import solve_DE, sort_times_over_all_cells


def _linear_dt_grid(n_points: int, ratio: float) -> jnp.ndarray:
    """Return an array `t[0..n_points-1] ∈ [0,1]` where
    dt(i) grows linearly from dt_min to dt_max and dt_max/dt_min = *ratio*.
    The grid size is *n_points* (so dt array has length n_points-1).
    """
    ratio = float(max(ratio, 1.0))  # ensure ≥ 1
    N = n_points - 1  # number of intervals
    idx = jnp.arange(N, dtype=jnp.float32)
    weights = 1.0 + (ratio - 1.0) * idx / (N - 1)  # linear ramp 1 → ratio
    dt_norm = weights / weights.sum()  # normalise so Σ dt = 1
    times = jnp.concatenate([jnp.array([0.0], dtype=jnp.float32), jnp.cumsum(dt_norm)])
    return times

@beartype
def prepare_model_input(
    adata_rna: AnnData,
    tf_list: List[str],
    n_cells_col: str = "n_cells",
    prior_time_col: Optional[str] = None,
    batch_annotation: Optional[str] = None,
    prior_timespan: Optional[float] = 40,
    N_steps: int = 100,
    grid_type: str = "linear",
    grid_param: float = 1.0,
    custom_grid_fn: Optional[Callable[[int], jnp.ndarray]] = None,
):
    """
    Prepare RNA input data for the model by extracting spliced and unspliced counts,
    computing transcription factor indices, and extracting cell metadata including batch
    information from adata_rna.obs if provided.  In addition, if you supply
    `cluster_key`, `initial_states`, and `terminal_states`, this will automatically
    build a “Prior Paths” (1-based) from those labels.  If you still want to pass
    in a numeric column (`prior_path_col`) you can; that takes priority if given.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object containing RNA expression data with 'spliced' and 'unspliced' layers.
    tf_list : List[str]
        List of transcription factor names.
    n_cells_col : str, optional
        Column name in `adata_rna.obs` representing the number of cells per metacell.
    prior_time_col : Optional[str], optional
        Column name in `adata_rna.obs` containing prior pseudotimes; if provided, used
        to center the prior over t_c (default: None).
    batch_annotation : Optional[str], optional
        Column name in `adata_rna.obs` that contains batch information; if provided,
        cells are assigned batch indices based on this column.
    prior_path_col : Optional[str], optional
        (legacy) Column name in `adata_rna.obs` that contains a hard‐coded 1‐based path index;
        missing/NaN entries become −1 (inference).  Takes priority over the
        automatic cluster‐based labeling described below.
    terminal_states : Optional[List[str]], optional
        If provided (and `cluster_key` is also given), defines a list of cluster names
        that should be mapped to terminal paths.  They will be assigned raw_prior = 1..P
        in the order you list them.
    initial_states : Optional[List[str]], optional
        If provided (and `cluster_key` is also given), defines a list of cluster names
        that should be mapped to raw_prior = 0 (which then becomes prior_path = −2
        internally, i.e. “initial state”).
    cluster_key : Optional[str], optional
        Column in `adata_rna.obs` whose values are compared against `initial_states`
        or `terminal_states` to build a “Prior Path” assignment.  This is only used
        if `prior_path_col` is None.
    prior_timespan : float, optional
        Used if prior_time_col is None (default span).  Otherwise recalculated from data.
    N_steps : int, optional
        Number of grid steps (default: 100).
    grid_type : str, optional
        “linear” or “linear_dt” (default: “linear”).
    grid_param : float, optional
        Parameter for “linear_dt” spacing (ignored if grid_type=“linear”).
    custom_grid_fn : Optional[Callable[[int], jnp.ndarray]], optional
        If you want to supply your own function to build `times_norm`.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing:
          - `data`: JAX array of shape (cells, genes, 2) with stacked unspliced and spliced counts.
          - `M_c`: JAX array of shape (cells, 1, 1) holding the per‐cell metacell size.
          - `obs2sample`: one‐hot encoding of batch indices (shape cells × n_batch).
          - `batch_index`: JAX array of shape (cells,) with batch indices.
          - `tf_indices`: JAX array of TF gene indices.
          - `total_num_cells`: int, number of cells.
          - `n_batch`: int, number of batches.
          - `prior_time`: JAX array of prior times or None.
          - `prior_timespan`: float, span of prior_time or default.
          - `prior_path`: JAX int array of shape (cells,) with −1 or 0‐based path ids;
              prior_path = −2 means “initial state,” prior_path ≥ 0 means fixed to path id.
          - `unknown_idx`: Python list of ints, indices of cells with unknown prior (prior_path < 0).
          - `unknown_count`: int, number of unknown cells.
          - `times_norm`, `dt_norm`, `T_limits`, `hidden_units`, `num_paths`
    """

    def _to_dense_f32(layer):
        if sparse.issparse(layer):
            # cast to float32 and densify in one go
            return layer.astype(np.float32).toarray()
        else:
            # if it’s already an ndarray, just ensure dtype
            return np.asarray(layer, dtype=np.float32)

    # ========== 1) STACK RAW DATA ==========
    spliced = _to_dense_f32(adata_rna.layers["spliced"])
    unspliced = _to_dense_f32(adata_rna.layers["unspliced"])
    data = jnp.array(np.stack([unspliced, spliced], axis=-1))

    # ========== 2) METACELL SIZES ==========
    M_c = jnp.array(
        np.expand_dims(np.expand_dims(adata_rna.obs[n_cells_col].to_numpy(), -1), -1),
        dtype=jnp.float32,
    )
    total_num_cells = int(data.shape[0])

    # ========== 3) PRIOR TIME ==========
    if prior_time_col is not None:
        prior_time = jnp.array(
            adata_rna.obs[prior_time_col].to_numpy(), dtype=jnp.float32
        )
        prior_timespan = float(prior_time.max() - prior_time.min())
    else:
        prior_time = None

    # ========== 4) BATCH INDEX ==========
    if batch_annotation is not None:
        batches = adata_rna.obs[batch_annotation].astype(str)
        uniq = batches.unique()
        mapping = {b: i for i, b in enumerate(uniq)}
        batch_index = jnp.array(batches.map(mapping).to_numpy(), dtype=jnp.int32)
    else:
        batch_index = jnp.zeros(total_num_cells, dtype=jnp.int32)
    n_batch = int(jnp.unique(batch_index).shape[0])
    obs2sample = jax.nn.one_hot(batch_index, num_classes=n_batch, dtype=jnp.float32)

    # ========== 5) TF INDICES ==========
    is_tf = np.isin(adata_rna.var_names, tf_list)
    tf_indices = jnp.array(np.where(is_tf)[0], dtype=jnp.int32)
    hidden_units = int(jnp.sqrt(int(np.sum(is_tf))))

    # ========== 7) BUILD TIMEGRID ==========
    if prior_time_col is None:
        T_min = -prior_timespan / 2.0
        T_max = +prior_timespan / 2.0
    else:
        T_min = prior_time.min() - prior_timespan / 10.0
        T_max = prior_time.max() + prior_timespan / 10.0

    if grid_type == "linear":
        times_norm = jnp.linspace(0.0, 1.0, N_steps + 1)
    elif grid_type in {"linear_dt", "lin_dt"}:
        times_norm = _linear_dt_grid(N_steps + 1, ratio=float(grid_param))
    else:
        raise ValueError(f"Unknown grid_type '{grid_type}'.")

    return OrderedDict(
        [
            ("data", data),
            ("M_c", M_c),
            ("obs2sample", obs2sample),
            ("batch_index", batch_index),
            ("tf_indices", tf_indices),
            ("total_num_cells", total_num_cells),
            ("n_batch", n_batch),
            ("prior_time", prior_time),
            ("prior_timespan", prior_timespan),
            ("times_norm", times_norm),
            ("T_limits", (T_min, T_max)),
            ("hidden_units", hidden_units),
        ],
    )

def soft_clip(y, lower, upper, sharpness=1.0):
    y1 = lower + jax.nn.softplus(sharpness * (y - lower)) / sharpness
    y2 = upper - jax.nn.softplus(sharpness * (upper - y1)) / sharpness
    return y2

@jax.jit
def interpolate_solution(
    sol_grid: jnp.ndarray,
    times_grid: jnp.ndarray,
    T_c: jnp.ndarray,
) -> jnp.ndarray:
    """
    Linearly interpolate a precomputed solution grid at specified cell times.

    Parameters:
    - sol_grid (jnp.ndarray): Solution values on a regular time grid, shape (L, num_paths, num_genes, 3).
    - times_grid (jnp.ndarray): 1D array of time points corresponding to sol_grid, length L.
    - T_c (jnp.ndarray): Array of arbitrary times at which to interpolate, shape (num_cells,).

    Returns:
    - jnp.ndarray: Interpolated solution at each time in T_c, shape (num_cells, num_paths, num_genes, 3).
    """
    idx0 = jnp.searchsorted(times_grid, T_c, side="right") - 1
    idx0 = jnp.clip(idx0, 0, sol_grid.shape[0] - 2)
    t0 = times_grid[idx0]
    t1 = times_grid[idx0 + 1]
    sol0 = sol_grid[idx0]
    sol1 = sol_grid[idx0 + 1]
    w = ((T_c - t0) / (t1 - t0))[..., None, None, None]
    return sol0 * (1 - w) + sol1 * w

@beartype
def mlp(
    params: Dict,
    x: Any,
) -> Any:
    """
    One or Multilayer Perceptron (MLP) with residual connections.

    Args:
        params: Dictionary containing neural network parameters (weights and biases).
        x: Input data array.

    Returns:
        Output array after passing through the MLP.
    """

    # First hidden layer with residual connections
    out = jnp.dot(x, params["W"]) + params["b"]
    out = jax.nn.softplus(out)

    return out

# Define the ODE function using the MLP
@beartype
def dstate_dt(t, state, args):
    """
    Compute the derivative of the state vector for the coupled system using a neural network.

    Args:
        t: Time scalar.
        state: State vector [u_1, ..., u_G, s_1, ..., s_G].
        args: Tuple containing parameters (G, beta_g, gamma_g, nn_params, T_ON).

    Returns:
        Derivative of the state vector
    """

    alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices = args
    u = state[..., 0]  # Unspliced counts for all genes.
    s = state[..., 1]  # Spliced counts for all genes.
    p = state[..., 2]  # Proteins for all genes.

    # Clip state values to increase numerical stability:
    u = jnp.clip(u, 0, 1e3)
    s = jnp.clip(s, 0, 1e3)
    p = jnp.clip(p, 0, 1e3)

    # Compute transcription rates using the neural network
    alpha = alpha_0 * jnp.clip(mlp(nn_params, p[:, tf_indices]), 0, 1e3)  # Shape: (G,)

    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s
    # Compute dp_dt only for TF indices
    dp_dt = jnp.zeros_like(u)
    dp_dt = dp_dt.at[:, tf_indices].set(
        lamda * s[:, tf_indices] - kappa * p[:, tf_indices]
    )

    dstate_dt = jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)  # Shape: (3G,)
    return dstate_dt

def euler_integrator(
    times: jnp.ndarray,    # (L+1,)
    y0: jnp.ndarray,       # state at t0, shape (G, 3)
    drift_fn: Any,         # f(t, y, args) -> dy/dt
    drift_args: Any,
) -> jnp.ndarray:
    """
    Simple Euler integrator for ODE dy/dt = f(t, y, args).
    Returns array of shape (L+1, G, 3).
    """
    dt = jnp.diff(times)
    def step(y_prev, t_dt):
        t_prev, dt_i = t_dt
        f = drift_fn(t_prev, y_prev, drift_args)
        y_new = y_prev + f * dt_i
        return y_new, y_new

    init = y0
    ts = jnp.stack([times[:-1], dt], axis=1)
    _, ys = jax.lax.scan(step, init, ts)
    return jnp.concatenate([y0[None], ys], axis=0)

# Define the complete NumPyro model
def model(
    data: Any,
    M_c: Any,
    obs2sample: Any,
    batch_index: Any,
    tf_indices: Any,
    total_num_cells: int,
    n_batch: int,
    prior_time: Any,
    prior_timespan: Any,
    times_norm: Any,
    T_limits: Any,
    return_alpha: bool = False,
    Tmax_alpha: float = 50.0,
    Tmax_beta: float = 1.0,
    splicing_rate_alpha_hyp_prior_alpha: float = 20.0,
    splicing_rate_alpha_hyp_prior_mean: float = 5.0,
    splicing_rate_mean_hyp_prior_alpha: float = 10.0,
    splicing_rate_mean_hyp_prior_mean: float = 1.0,
    degradation_rate_alpha_hyp_prior_alpha: float = 20.0,
    degradation_rate_alpha_hyp_prior_mean: float = 5.0,
    degradation_rate_mean_hyp_prior_alpha: float = 10.0,
    degradation_rate_mean_hyp_prior_mean: float = 1.0,
    transcription_rate_alpha_hyp_prior_alpha: float = 20.0,
    transcription_rate_alpha_hyp_prior_mean: float = 2.0,
    transcription_rate_mean_hyp_prior_alpha: float = 10.0,
    transcription_rate_mean_hyp_prior_mean: float = 5.0,
    lambda_alpha: float = 1.0,
    lambda_mean: float = 1.0,
    kappa_alpha: float = 1.0,
    kappa_mean: float = 1.0,
    detection_mean_hyp_prior_alpha: float = 1.0,
    detection_mean_hyp_prior_beta: float = 1.0,
    detection_hyp_prior_alpha: float = 10.0,
    detection_i_prior_alpha: float = 100.0,
    detection_gi_prior_alpha: float = 200.0,
    gene_add_alpha_hyp_prior_alpha: float = 9.0,
    gene_add_alpha_hyp_prior_beta: float = 3.0,
    gene_add_mean_hyp_prior_alpha: float = 1.0,
    gene_add_mean_hyp_prior_beta: float = 100.0,
    stochastic_v_ag_hyp_prior_alpha: float = 9.0,
    stochastic_v_ag_hyp_prior_beta: float = 3.0,
    sde_rng_key=0,
    **kwargs,
):
    """
    NumPyro model for coupled transcription and splicing dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        M_c: Number of cells in each metacell.
        batch_index: Array indicating batch assignments for each cell.
        tf_indices: Indices of genes that are TFs.
        total_num_cells: Number of cells in the full dataset.
        n_batch: Number of batches.
        Tmax_alpha: Alpha parameter for Tmax prior.
        Tmax_beta: Beta parameter for Tmax prior.
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """

    num_cells = int(data.shape[0])
    num_genes = int(data.shape[1])
    num_modalities = int(data.shape[2])
    num_tfs = tf_indices.shape[0]
    batch_size = num_cells

    # Splicing Rates for mRNA
    splicing_alpha = numpyro.sample(
        "splicing_alpha",
        dist.Gamma(
            splicing_rate_alpha_hyp_prior_alpha,
            splicing_rate_alpha_hyp_prior_alpha / splicing_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_alpha = jnp.clip(splicing_alpha, a_min=1e-2, a_max=1e3)

    splicing_mean = numpyro.sample(
        "splicing_mean",
        dist.Gamma(
            splicing_rate_mean_hyp_prior_alpha,
            splicing_rate_mean_hyp_prior_alpha / splicing_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_mean = jnp.clip(splicing_mean, a_min=1e-2, a_max=1e3)

    beta_g = numpyro.sample(
        "beta_g",
        dist.Gamma(splicing_alpha, splicing_alpha / splicing_mean, validate_args=True)
        .expand([num_genes])
        .to_event(1),
    )

    # Degradation Rates for mRNA
    degradation_alpha = numpyro.sample(
        "degradation_alpha",
        dist.Gamma(
            degradation_rate_alpha_hyp_prior_alpha,
            degradation_rate_alpha_hyp_prior_alpha
            / degradation_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_alpha = degradation_alpha + 0.001  # Prevent zero

    degradation_mean = numpyro.sample(
        "degradation_mean",
        dist.Gamma(
            degradation_rate_mean_hyp_prior_alpha,
            degradation_rate_mean_hyp_prior_alpha
            / degradation_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_mean = jnp.clip(degradation_mean, a_min=1e-2, a_max=1e3)

    gamma_g = numpyro.sample(
        "gamma_g",
        dist.Gamma(
            degradation_alpha, degradation_alpha / degradation_mean, validate_args=True
        )
        .expand([num_genes])
        .to_event(1),
    )

    # Translation rate for proteins
    lamda = numpyro.sample(
        "lambda",
        dist.Gamma(lambda_alpha, lambda_alpha / lambda_mean, validate_args=True)
        .expand([num_tfs])
        .to_event(1),
    )
    # Degradation rate for proteins
    kappa = numpyro.sample(
        "kappa",
        dist.Gamma(kappa_alpha, kappa_alpha / kappa_mean, validate_args=True)
        .expand([num_tfs])
        .to_event(1),
    )

    # Time Parameters
    # sample a *single* global scaling factor
    T_min, T_max = T_limits
    T_scaling = numpyro.sample("T_scaling", dist.Beta(1.0, 3.0))
    total_span = (T_max - T_min) * T_scaling

    # build *static‐shape* grid (always N_steps long)
    abs_grid   = T_min + times_norm * (T_max - T_min)
    times_grid = T_scaling * abs_grid

    # convert your absolute prior_time (if any) into a [0,1] loc/scale
    if prior_time is None:
        prior_time = T_min + (T_max - T_min) / 2
        prior_time_sd = prior_timespan / 2.0
    else:
        prior_time_sd = prior_timespan / 6.0

    with numpyro.plate("cells", batch_size):
        t_c = numpyro.sample(
            "t_c",
            dist.TruncatedNormal(
                loc=prior_time,
                scale=prior_time_sd,
                low=T_limits[0],
                high=T_limits[1],
            ),
        )
        T_c = numpyro.deterministic("T_c", T_scaling * t_c)

    # ============= Expression model =============== #

    # scale of alpha
    alpha_0 = numpyro.sample(
        "alpha_0",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Initial Conditions for ODE, sampling only for spliced and unspliced
    initial_state_2d = numpyro.sample(
        "initial_state_2d",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([1, num_genes, 2]).to_event(1),
    )

    # Create the third dimension containing proteins, only for TFs:
    third_dimension = jnp.zeros((1, num_genes))
    third_dimension = third_dimension.at[0, tf_indices].set(
        numpyro.sample(
            "initial_state_tf",
            dist.Gamma(1.0, 1.0, validate_args=True).expand([len(tf_indices)]),
        )
    )

    # Concatenate the dimensions to form the final initial state
    initial_state = jnp.concatenate(
        [initial_state_2d, third_dimension[..., None]], axis=-1
    )

    # Neural Net parameters
    in_dim = num_tfs
    out_dim = num_genes

    _key = numpyro.prng_key()
    key_W, key_b = jax.random.split(_key, 2)

    W = numpyro.param(
        "W", jax.random.normal(key_W, (in_dim, out_dim)) * 0.01
    )
    b = numpyro.param("b", jnp.zeros((out_dim,)))

    # Organize parameters into a dictionary
    nn_params = {
        "W": W,
        "b": b,
    }

    # Prepare Parameters for ODE Solver
    ode_args = (alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices)

    # Run euler integration
    sol_grid = euler_integrator(times_grid, initial_state, dstate_dt, ode_args)

    # Interpolate each cell’s trajectory at its sampled time T_c
    sol_at_cells = interpolate_solution(sol_grid, times_grid, T_c)

    # Track as predictions_rearranged for compatibility purposes with some plotting functions
    numpyro.deterministic('predictions_rearranged', sol_at_cells)

    # Extract unspliced & spliced for your likelihood
    mu_expression = jnp.clip(sol_at_cells[:,0,:, :2], 1e-5, 1e5)

    # ============= Detection efficiency of spliced and unspliced counts =============== #

    with numpyro.plate("batch", n_batch):
        detection_mean_y_e = numpyro.sample(
            "detection_mean_y_e",
            dist.Beta(
                detection_mean_hyp_prior_alpha * jnp.ones((1,)),
                detection_mean_hyp_prior_beta * jnp.ones((1,)),
                validate_args=True,
            ).to_event(1),
        )

    beta = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_y_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_y_c = numpyro.sample(
            "detection_y_c", dist.Gamma(detection_hyp_prior_alpha, beta)
        )

    detection_y_i = numpyro.sample(
        "detection_y_i",
        dist.Gamma(detection_i_prior_alpha, detection_i_prior_alpha, validate_args=True)
        .expand([1, 1, 2])
        .to_event(3),
    )

    detection_y_gi = numpyro.sample(
        "detection_y_gi",
        dist.Gamma(
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            validate_args=True,
        )
        .expand([1, num_genes, 2])
        .to_event(3),
    )

    # ======= Gene-specific additive component (Ambient RNA/ "Soup") for spliced and unspliced counts ====== #

    s_g_gene_add_alpha_hyp = numpyro.sample(
        "s_g_gene_add_alpha_hyp",
        dist.Gamma(
            gene_add_alpha_hyp_prior_alpha,
            gene_add_alpha_hyp_prior_beta,
            validate_args=True,
        ),
        sample_shape=(2,),
    )

    s_g_gene_add_mean = numpyro.sample(
        "s_g_gene_add_mean",
        dist.Gamma(
            gene_add_mean_hyp_prior_alpha,
            gene_add_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1, 2])
        .to_event(3),
    )

    s_g_gene_add_alpha_e_inv = numpyro.sample(
        "s_g_gene_add_alpha_e_inv",
        dist.Exponential(s_g_gene_add_alpha_hyp).expand([n_batch, 1, 2]).to_event(3),
    )

    s_g_gene_add_alpha_e = jnp.ones((1, 1)) / s_g_gene_add_alpha_e_inv**2

    s_g_gene_add = numpyro.sample(
        "s_g_gene_add",
        dist.Gamma(
            s_g_gene_add_alpha_e,
            s_g_gene_add_alpha_e / s_g_gene_add_mean,
            validate_args=True,
        )
        .expand([n_batch, num_genes, 2])
        .to_event(3),
    )

    # ========= Gene-specific overdispersion of spliced and unspliced counts ============== #

    stochastic_v_ag_hyp = numpyro.sample(
        "stochastic_v_ag_hyp",
        dist.Gamma(
            stochastic_v_ag_hyp_prior_alpha,
            stochastic_v_ag_hyp_prior_beta,
            validate_args=True,
        )
        .expand([1, 2])
        .to_event(2),
    )

    stochastic_v_ag_inv = numpyro.sample(
        "stochastic_v_ag_inv",
        dist.Exponential(stochastic_v_ag_hyp).expand([1, num_genes, 2]).to_event(3),
    )

    stochastic_v_ag = jnp.ones((1, 1)) / stochastic_v_ag_inv**2

    # ===================== Expected expression ======================= #

    additive_term = numpyro.deterministic(
        "additive_term", jnp.einsum("cb,bgi->cgi", obs2sample, s_g_gene_add)
    )

    normalizing_term = numpyro.deterministic(
        "normalizing_term",
        detection_y_c[:, None, None] * detection_y_i * detection_y_gi * M_c,
    )

    mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)

    # ===================== DATA likelihood ======================= #

    concentration = stochastic_v_ag * M_c
    rate = concentration / mu

    # Likelihood (sampling distribution)
    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by (total_num_cells / batch_size). That ensures an unbiased gradient estimate.
    scale_factor = total_num_cells / batch_size
    with scale(scale=scale_factor):
        data_target = numpyro.sample(
            "data_target", dist.GammaPoisson(concentration, rate), obs=data
        )
