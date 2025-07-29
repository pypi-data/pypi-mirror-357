from collections import OrderedDict
from functools import partial
from typing import Any, Callable, Dict, List, Optional

import jax
import jax.numpy as jnp
import jax.random as random
import matplotlib.pyplot as plt
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
import scanpy as sc
import scipy.sparse as sp
from anndata import AnnData
from beartype import beartype
from diffrax import Euler, ODETerm, RecursiveCheckpointAdjoint, SaveAt, diffeqsolve
from einops import rearrange
from jaxtyping import Float, jaxtyped
from numpyro.handlers import scale
from numpyro.infer import SVI, Predictive, Trace_ELBO
from numpyro.infer.autoguide import AutoNormal
from numpyro.optim import Adam

from stormi.models.utils import solve_DE, sort_times_over_all_cells


@beartype
def prepare_model_input(
    adata_rna: AnnData,
    adata_atac: AnnData,
    tf_list: List[str],
    motif_scores: pd.DataFrame,
    n_cells_col: Optional[str] = "n_cells",
    prior_time_col: Optional[str] = None,
    batch_annotation: Optional[str] = None,
    species: Optional[str] = "human",
    prior_timespan: Optional[float] = 40,
) -> Dict[str, Any]:
    """
    Prepare input data for the model by converting layers, stacking counts, and
    computing region–TF/gene relationships.

    This function performs the following steps:

      1. **Dense Conversion & Stacking RNA Data:**
         - Converts the `'spliced'` and `'unspliced'` layers of `adata_rna` to dense
           format using `convert_to_dense`.
         - Stacks the two arrays along a new axis (last dimension) and converts the
           resulting array to a JAX array.

      2. **ATAC Data Conversion:**
         - Converts the ATAC data (`adata_atac.X`) to a JAX array.

      3. **Additional Metadata Extraction:**
         - **M_c:** If `n_cells_col` is provided (not `None`), extracts that column from
           `adata_rna.obs` and reshapes it into a (cells, 1, 1) JAX array. Otherwise,
           sets `M_c` to an array of ones.
         - **batch_index:** If `batch_annotation` is provided, maps each unique batch
           to an integer and assigns these to cells. Otherwise, assigns a value of 1
           to all cells.
         - Determines the indices (and count) of transcription factors (TFs) in
           `adata_rna.var_names` using `tf_list`.
         - Determines the number of regions from the ATAC data.

      4. **Region–TF and Region–Gene Relationships:**
         - Computes `region_tf_pairs` using the `motif_scores` DataFrame
           together with `adata_atac` and `adata_rna`.
         - Computes `region_gene_pairs` from the RNA and ATAC AnnData objects.
         - Constructs all unique (region, TF, gene) triplets.
         - Computes the region–TF indices corresponding to each triplet.
         - Extracts gene indices from the triplets.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object containing RNA expression data with at least two layers:
        `'spliced'` and `'unspliced'`. Also requires an observation column (if used)
        containing the number of cells per metacell and a `var_names` attribute.
    adata_atac : AnnData
        AnnData object containing ATAC data. Its main count matrix is used.
    tf_list : List[str]
        List of transcription factor names.
    motif_scores : pd.DataFrame
        DataFrame (previously called moods_scores) that contains at least the columns used in
        the helper function `extract_region_tf_pairs` (by default, columns named `"0"` for regions
        and `"mouse_gene_name"` for TFs).
    n_cells_col : Optional[str], default "n_cells"
        Name of the column in `adata_rna.obs` that contains the number of cells in each metacell.
        If set to `None`, `M_c` is set to an array of ones.
    prior_time_col: Optional[str]
        Name of the column in `adata_rna.obs` that contains the prior expectation about the time for
        each cell in hours. By default it is set to `None`, so no prior knowledge is used.
    batch_annotation : Optional[str], default None
        Name of the column in `adata_rna.obs` that contains batch names.
        If `None`, all cells are assigned a batch value of 1. Otherwise, each unique batch is
        mapped to an integer.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
          - `data`: JAX array of shape (cells, features, 2) with stacked unspliced and spliced RNA counts.
          - `data_atac`: JAX array of ATAC counts.
          - `M_c`: JAX array of shape (cells, 1, 1) holding the per-cell metacell size.
          - `batch_index`: JAX array of batch indices for each cell.
          - `tf_indices`: JAX array of indices of transcription factors.
          - `num_tfs`: Total number of transcription factors (int).
          - `num_regions`: Total number of regions from the ATAC data (int).
          - `region_tf_pairs`: JAX array of region–TF pairs.
          - `region_gene_pairs`: JAX array of region–gene pairs with a weight.
          - `region_tf_gene_triplets`: JAX array of triplets (region, TF, gene).
          - `map_region_tf_to_index`: JAX array mapping each [region, TF] pair to its index.
          - `region_tf_indices`: JAX array of indices corresponding to the triplets.
          - `gene_indices`: JAX array of gene indices from the triplets.

    Example
    -------
    >>> inputs = prepare_model_input_data(adata_rna, adata_atac, tf_list, motif_scores,
    ...                                    n_cells_col="n_cells", batch_annotation="batch")
    >>> print(inputs["data"].shape)
    """
    # lazily import preprocessing functions, which require the preprocessing extras
    # $ pip install stormi[preprocessing]
    try:
        from stormi.preprocessing import (
            build_region_gene_pairs,
            construct_region_tf_gene_triplets,
            convert_to_dense,
            extract_region_tf_pairs,
            rhg_to_rh_indexing,
        )
    except ImportError:
        raise ImportError(
            "Preprocessing module dependencies are required for prepare_model_input. "
            "Install them with 'pip install stormi[preprocessing]'or 'uv sync --extra preprocessing'"
        )

    # --- Step 1: Convert and stack RNA layers ---
    spliced_dense = convert_to_dense(adata_rna.layers["spliced"])
    unspliced_dense = convert_to_dense(adata_rna.layers["unspliced"])
    # Stack along a new last axis: shape becomes (cells, features, 2)
    data = np.stack([unspliced_dense, spliced_dense], axis=-1)
    data = jnp.array(data)
    del unspliced_dense, spliced_dense

    # --- Step 2: Convert ATAC data ---
    data_atac = jnp.array(convert_to_dense(adata_atac.X))

    # --- Step 3: Extract additional metadata ---
    # M_c: Use provided column or default to ones.
    if n_cells_col is not None:
        M_c = jnp.array(
            np.expand_dims(
                np.expand_dims(adata_rna.obs[n_cells_col].to_numpy(), -1), -1
            )
        )
    else:
        M_c = jnp.ones((adata_rna.n_obs, 1, 1))
    total_num_cells = adata_rna.n_obs

    # 3) prior time
    if prior_time_col is not None:
        prior_time = jnp.array(
            adata_rna.obs[prior_time_col].to_numpy(), dtype=jnp.float32
        )
        prior_timespan = float(prior_time.max() - prior_time.min())
        T_min = prior_time.min() - prior_timespan / 6.0
        T_max = prior_time.max() + prior_timespan / 6.0
    else:
        prior_time = None
        T_min = -prior_timespan / 2.0
        T_max = +prior_timespan / 2.0

    # batch_index: Map batch annotation to integer labels if provided; otherwise, assign 1 to all.
    if batch_annotation is not None:
        # Create a mapping from batch names to integers
        batch_series = adata_rna.obs[batch_annotation]
        unique_batches = batch_series.unique()
        batch_map = {batch: i for i, batch in enumerate(unique_batches)}
        batch_index = jnp.array(batch_series.map(batch_map).to_numpy())
    else:
        batch_index = jnp.zeros(adata_rna.n_obs, dtype=int)

    n_batch = len(jnp.unique(batch_index))

    # Determine which genes in adata_rna.var_names are TFs.
    is_tf = adata_rna.var_names.isin(tf_list)
    tf_indices = jnp.array(np.where(is_tf)[0])
    num_tfs = int(tf_indices.shape[0])
    num_regions = int(data_atac.shape[1])

    # --- Step 4: Compute region–TF and region–gene relationships ---
    region_tf_pairs = extract_region_tf_pairs(motif_scores, adata_atac, adata_rna)
    region_gene_pairs = build_region_gene_pairs(adata_atac, adata_rna, species=species)
    region_tf_gene_triplets = construct_region_tf_gene_triplets(
        region_tf_pairs, region_gene_pairs
    )
    region_tf_indices = rhg_to_rh_indexing(region_tf_gene_triplets, region_tf_pairs)
    gene_indices = region_tf_gene_triplets[:, 2]

    # ─ build flat index of known and unknown motif-region pairs
    known_idx = region_tf_pairs[:, 0] * num_tfs + region_tf_pairs[:, 1]
    unknown_idx = jnp.setdiff1d(jnp.arange(num_regions * num_tfs), known_idx)

    return OrderedDict(
        [
            ("data", data),
            ("data_atac", data_atac),
            ("M_c", M_c),
            ("batch_index", batch_index),
            ("tf_indices", tf_indices),
            ("region_tf_pairs", region_tf_pairs),
            ("region_gene_pairs", region_gene_pairs),
            ("region_tf_gene_triplets", region_tf_gene_triplets),
            ("region_tf_indices", region_tf_indices),
            ("gene_indices", gene_indices),
            ("num_regions", num_regions),
            ("total_num_cells", total_num_cells),
            ("n_batch", n_batch),
            ("prior_time", prior_time),
            ("prior_timespan", prior_timespan),
            ("known_idx", known_idx),
            ("unknown_idx", unknown_idx),
            ("T_limits", (T_min, T_max)),
        ]
    )


@beartype
def sample_prior(
    model: Callable[..., Any],
    model_input: Dict[str, Any],
    num_samples: int = 5,
    seed: int = 42,
    *,
    sites: Optional[List[str]] = None,
    sample_n_cells: int = 0,
) -> Dict[str, Any]:
    """
    Runs prior predictive sampling for a given model, optionally on a subset
    of cells and only returning specified sites. Also returns which cells
    were selected (cell_indices).

    Parameters
    ----------
    model : Callable[..., Any]
        The NumPyro model to sample from.
    model_input : Dict[str, Any]
        Input dict for the model (must include at least "data", "num_regions",
        and region‐batching keys if used).
    num_samples : int
        Number of prior draws to generate.
    seed : int
        RNG seed for reproducibility.
    sites : list of str, optional
        If provided, only these sample sites will be returned.
    sample_n_cells : int
        If >0, uniformly subsample this many cells before running Predictive.

    Returns
    -------
    Dict[str, Any]
        A dict with:
          - each requested site → array of shape (num_samples, …)
          - "cell_indices" → 1D int array of length `sample_n_cells` (or all cells)
    """
    # 0) shallow‐copy inputs
    mi = dict(model_input)

    # 1) choose & record which cells to include
    n_cells = mi["data"].shape[0]
    if sample_n_cells and sample_n_cells < n_cells:
        idxs = jnp.arange(n_cells)
        selected = np.random.choice(idxs, sample_n_cells)
    else:
        selected = jnp.arange(n_cells)

    # slice all cell‐indexed arrays
    mi["data"] = mi["data"][selected, ...]
    mi["M_c"] = mi["M_c"][selected, ...]
    mi["batch_index"] = mi["batch_index"][selected]
    mi["prior_time"] = mi["prior_time"][selected]

    # 2) region‐level setup (unchanged)
    num_regions = model_input["num_regions"]
    all_region_indices = np.arange(num_regions)
    rng_local = np.random.default_rng(seed)
    init_region_batch = rng_local.choice(
        all_region_indices, size=num_regions, replace=False
    )
    mi["batch_region_indices"] = init_region_batch
    mi["region_tf_pairs_mask"] = np.where(
        jnp.isin(mi["region_tf_pairs"][:, 0], init_region_batch)
    )[0]

    # 3) draw from the prior with Predictive
    rng_key = random.PRNGKey(seed)
    predictive = Predictive(model, num_samples=num_samples, return_sites=sites)
    prior_samples = predictive(rng_key, **mi)

    # 4) attach which cells we used
    prior_samples["cell_indices"] = selected

    return prior_samples


@beartype
def compute_d_cr_dense(
    p: jnp.ndarray,  # (cells, G)   — protein abundances
    K_rh: jnp.ndarray,  # (R, H)       — dissociation constants
    w_h: jnp.ndarray,  # (H,)         — TF → ATAC effect
    w_r: jnp.ndarray,  # (R,)         — region baseline
    tf_indices: jnp.ndarray,
    num_regions: int,
) -> jnp.ndarray:
    # 1) extract only the TF columns from p
    p_tf = p[:, tf_indices]  # (cells, H)

    # 2) compute binding prob P[r,h](cell) in one broadcast:
    #    P[c,r,h] = p_tf[c,h] / (p_tf[c,h] + K_rh[r,h])
    P = p_tf[:, None, :] / (p_tf[:, None, :] + K_rh[None, :, :])  # (cells, R, H)

    # 3) weight by w_h and sum over H → (cells, R)
    sum_wP = jnp.sum(P * w_h[None, None, :], axis=2)

    # 4) add baseline + ReLU + ε
    return jax.nn.softplus(sum_wP + w_r[None, :]) + 1e-5


@beartype
def dstate_dt(t, state, args):
    """
    ODE derivative for (u, s, p) per gene, using ALL TF×region pairs.

    args unpacks to:
      alpha0_g, beta_g, gamma_g, lamda, kappa,
      K_rh,                       # (R, H)
      w_grh_vector,               # (num_triplets,)
      b_g,                        # (num_genes,)
      tf_indices,                 # (H,)
      region_tf_pairs,            # (R*H, 2)
      region_tf_gene_triplets,    # (num_triplets, 3)
      region_tf_indices,          # (num_triplets,)
      gene_indices,               # (num_triplets,)
      num_genes: int,
      T_ON: float
    """
    (
        alpha0_g,
        beta_g,
        gamma_g,
        lamda,
        kappa,
        K_rh,
        w_grh_vector,
        b_g,
        tf_indices,
        region_tf_pairs,
        region_tf_gene_triplets,
        region_tf_indices,
        gene_indices,
        num_genes,
        T_ON,
    ) = args

    # unpack the state: shape (..., G, 3)
    u = jnp.clip(state[..., 0], 0, 1e3)  # unspliced
    s = jnp.clip(state[..., 1], 0, 1e3)  # spliced
    p = jnp.clip(state[..., 2], 0, 1e3)  # proteins

    # --- compute binding probs for every (r,h) pair ---
    # flatten K_rh and select exactly those pairs in region_tf_pairs
    r_idx = region_tf_pairs[:, 0]  # (P=R*H,)
    h_idx = region_tf_pairs[:, 1]  # (P,)
    K_flat = K_rh[r_idx, h_idx]  # (P,)
    p_h = p[..., h_idx]  # (..., P)
    P_flat = p_h / (p_h + K_flat)  # (..., P)

    # --- now gather into the triplets for gene regulation ---
    # P_trip ends up shape (cells, num_triplets)
    P_trip = P_flat[..., region_tf_indices]  # (..., T)
    wP = w_grh_vector * P_trip  # (..., T)

    # --- **swap axes** so that the T axis is axis 0 for segment_sum ---
    # assume wP is 2D: (cells, T)
    wP_swap = jnp.swapaxes(wP, 0, 1)  # (T, cells)

    # sum contributions by gene: now axis 0 has length T matching gene_indices
    summed = jax.ops.segment_sum(
        wP_swap, gene_indices, num_segments=num_genes
    )  # (num_genes, cells)

    # swap back → (cells, num_genes)
    sum_wP = jnp.swapaxes(summed, 0, 1)  # (cells, G)

    # transcription rate per gene
    alpha = alpha0_g * jax.nn.softplus(b_g + sum_wP)

    # ODE for unspliced / spliced
    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s

    # ODE for proteins (only TF indices)
    dp_dt = jnp.zeros_like(u)
    dp_dt = dp_dt.at[..., tf_indices].set(
        lamda * s[..., tf_indices] - kappa * p[..., tf_indices]
    )

    return jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)


# Define the complete NumPyro model
@beartype
def model(
    data: Any,
    data_atac: Any,
    M_c: Any,
    batch_index: Any,
    tf_indices: Any,
    region_tf_pairs: Any,
    region_gene_pairs: Any,
    region_tf_gene_triplets: Any,
    region_tf_indices: Any,
    gene_indices: Any,
    num_regions: Any,
    total_num_cells: int,
    n_batch: int,
    prior_time: Any,
    prior_timespan: Any,
    known_idx: Any,
    unknown_idx: Any,
    T_limits: Any,
    batch_region_indices: Any,
    region_tf_pairs_mask: Any,
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
    stochastic_v_ag_hyp_prior_alpha_atac: float = 1.0,
    stochastic_v_ag_hyp_prior_beta_atac: float = 1.0,
    sde_rng_key: Any = random.PRNGKey(0),
):
    """
    NumPyro model for coupled transcription, splicing, protein, chromatin dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        ... (other model inputs)
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """
    num_cells, num_genes, num_modalities = data.shape
    num_tfs = tf_indices.shape[0]
    num_pairs = len(region_tf_pairs)
    num_rg_pairs = len(region_gene_pairs)
    num_rtg_triplets = len(region_tf_gene_triplets)
    num_regions_total = num_regions
    num_regions_batch = data_atac.shape[1]
    batch_size = num_cells
    obs2sample = jax.nn.one_hot(
        batch_index, num_classes=n_batch
    )  # Shape: (num_cells, n_batch)

    # Dissociation constant
    K_log10_known = numpyro.sample(
        "K_rh_log10_known",
        dist.Normal(2.0, 1.0).expand([num_pairs]).to_event(1),
    )

    # 4) sample unknown‐pair log10(K) ~ Normal(2+log10(2), 1), shape (U,)
    K_log10_unknown = numpyro.sample(
        "K_rh_log10_unknown",
        dist.Normal(2.0 + jnp.log10(2.0), 1.0)
        .expand([unknown_idx.shape[0]])
        .to_event(1),
    )

    # 5) scatter into a flat vector length P
    K_log10_flat = jnp.zeros(num_regions * num_tfs)
    K_log10_flat = K_log10_flat.at[unknown_idx].set(K_log10_unknown)
    K_log10_flat = K_log10_flat.at[known_idx].set(K_log10_known)

    # 6) reshape to (R, H) and exponentiate
    K_log10 = K_log10_flat.reshape((num_regions, num_tfs))
    K_rh = numpyro.deterministic("K_rh", 10**K_log10)

    # Basal transcription rate
    alpha0_g = numpyro.sample(
        "alpha0_g",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Bias term for transcription rate function:
    b_g = numpyro.sample("b_g", dist.Normal(-1.0, 1.0).expand([num_genes]).to_event(1))

    # Effect of region-tf pairs on target gene transcription rate
    w_grh_vector = numpyro.sample(
        "w_grh_vector", dist.Normal(loc=0.0, scale=1.0).expand([num_rtg_triplets])
    )

    # Effect of TF binding on region ATAC counts:
    w_h = numpyro.sample("w_h", dist.Normal(0.0, 1.0).expand([num_tfs]))
    # Baseline ATAC cound for each region
    w_r = numpyro.sample("w_r", dist.Normal(0.0, 1.0).expand([num_regions_total]))

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
    prior_time_sd = prior_timespan / 6
    if prior_time is None:
        with numpyro.plate("cells", batch_size):
            t_c = numpyro.sample(
                "t_c",
                dist.TruncatedNormal(
                    low=T_limits[0], high=T_limits[1], loc=0, scale=prior_time_sd
                ),
            )
            T_c = numpyro.deterministic("T_c", t_c)
    else:
        T_scaling = numpyro.sample("T_scaling", dist.Beta(1.0, 3.0))
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
    T_ON = T_limits[0] - 0.1

    # ============= Expression model =============== #

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

    # Prepare Parameters for ODE Solver
    params = (
        alpha0_g,
        beta_g,
        gamma_g,
        lamda,
        kappa,
        K_rh,
        w_grh_vector,
        b_g,
        tf_indices,
        region_tf_pairs,
        region_tf_gene_triplets,
        region_tf_indices,
        gene_indices,
        num_genes,
        T_ON,
    )

    # Get Ordered Time Vector
    all_times, time_indices, _ = sort_times_over_all_cells(T_c)

    # Solve the Coupled ODE
    predictions = solve_DE(
        ts=all_times.squeeze(),
        params=params,
        initial_state=initial_state,
        time_step=0.1,
        drift=dstate_dt,
        t0=-15.0,
        t1=15.0,
    )

    # Ensure predictions are floating-point
    predictions = numpyro.deterministic("predictions", predictions.astype(jnp.float32))

    predictions_rearranged = numpyro.deterministic(
        "predictions_rearranged", predictions[time_indices.ravel(), :]
    )

    mu_expression = jnp.clip(
        predictions_rearranged[..., :2].squeeze(1), a_min=10 ** (-5), a_max=10 ** (5)
    )

    mu_protein = predictions_rearranged[..., 2].squeeze(1)

    # ============= Detection efficiency of spliced and unspliced counts =============== #

    detection_mean_y_e = numpyro.sample(
        "detection_mean_y_e",
        dist.Beta(
            jnp.ones((1, 1)) * detection_mean_hyp_prior_alpha,
            jnp.ones((1, 1)) * detection_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1])
        .to_event(2),
    )

    beta1 = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_y_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_y_c = numpyro.sample(
            "detection_y_c", dist.Gamma(detection_hyp_prior_alpha, beta1)
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

    # ============= Detection efficiency of ATAC counts =============== #

    detection_mean_l_e = numpyro.sample(
        "detection_mean_l_e",
        dist.Beta(
            jnp.ones((1, 1)) * detection_mean_hyp_prior_alpha,
            jnp.ones((1, 1)) * detection_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1])
        .to_event(2),
    )

    beta2 = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_l_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_l_c = numpyro.sample(
            "detection_l_c", dist.Gamma(detection_hyp_prior_alpha, beta2)
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

    # ========= Overdispersion for ATAC ============== #

    stochastic_v_ag_hyp_atac = numpyro.sample(
        "stochastic_v_ag_hyp_atac",
        dist.Gamma(
            stochastic_v_ag_hyp_prior_alpha_atac, stochastic_v_ag_hyp_prior_beta_atac
        ),
    )

    stochastic_v_ag_inv_atac = numpyro.sample(
        "stochastic_v_ag_inv_atac",
        dist.Exponential(stochastic_v_ag_hyp_atac).expand([1, num_regions]).to_event(2),
    )

    stochastic_v_ag_atac = jnp.ones((1, 1)) / stochastic_v_ag_inv_atac**2

    # ===================== Expected value for RNA and ATAC counts======================= #

    mu = numpyro.deterministic(
        "mu",
        (mu_expression + jnp.einsum("cb,bgi->cgi", obs2sample, s_g_gene_add))
        * detection_y_c[:, None, None]
        * detection_y_i
        * detection_y_gi
        * M_c,
    )

    d_cr = numpyro.deterministic(
        "d_cr",
        compute_d_cr_dense(
            mu_protein,  # (cells, G)
            K_rh,  # (R, H)
            w_h,  # (H,)
            w_r,  # (R,)
            tf_indices,  # (H,)
            num_regions,
        ),
    )

    mu_atac = numpyro.deterministic(
        "mu_atac", detection_l_c[..., 0] * M_c[..., 0] * d_cr
    )

    # ===================== DATA likelihood ======================= #

    concentration = stochastic_v_ag * M_c
    rate = concentration / mu

    concentration_atac = stochastic_v_ag_atac * M_c[..., 0]
    rate_atac = concentration_atac / mu_atac

    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by the ratio of the full dataset to the minibatch dataset, to have an unbiased gradient estimate.
    scale_factor_rna = total_num_cells / batch_size
    with scale(scale=scale_factor_rna):
        data_target = numpyro.sample(
            "data_target", dist.GammaPoisson(concentration, rate), obs=data
        )

    # # We further adjust the scale factor here to give equal weight to RNA and ATAC data
    # # no matter the number of features in each
    scale_factor_atac = scale_factor_rna * 2 * num_genes / num_regions_batch
    with scale(scale=scale_factor_atac):
        data_target_atac = numpyro.sample(
            "data_target_atac",
            dist.GammaPoisson(concentration_atac, rate_atac),
            obs=data_atac,
        )
