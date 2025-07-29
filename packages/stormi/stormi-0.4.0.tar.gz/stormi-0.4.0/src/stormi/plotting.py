import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import jax.numpy as jnp
import matplotlib.pyplot as plt
import numpy as np
from beartype import beartype
from jax import Array
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure
from scipy import sparse


@beartype
def predictions_vs_data(
    observed: Union[np.ndarray, Array],
    predictions: Union[np.ndarray, Array],  # Renamed from "prior"
    bins: int = 50,
    figsize: Tuple[int, int] = (8, 6),
    log_norm: bool = True,
    x_log: bool = True,
    y_log: bool = True,
    log_base: int = 10,
    min_value: float = 5 * 1e-1,
    title: Optional[str] = "Predictions vs Data Density Heatmap",
    xlabel: str = "Observed Data",
    ylabel: str = "Predictions",
    seed: int = 42,
    log_bins: bool = True,
    normalize_cols: bool = False,
) -> plt.Figure:
    """
    Creates a heatmap that visualizes the density of points for observed data vs predictions.

    If the predictions array contains multiple posterior samples, each observed data point
    is paired with all corresponding samples by repeating it.

    All data points are clipped to be at least `min_value` (default: 9e-2). The x and y axes
    are optionally set to a logarithmic scale using the specified `log_base`. If `log_bins=True`,
    then the bins themselves are logarithmically spaced based on `log_base`.

    If `normalize_cols=True`, each column (observed bin) is normalized so that the density
    across predictions sums to 1.

    Args:
        observed (Union[np.ndarray, Array]): Observed data values (num_cells, num_genes, 2).
        predictions (Union[np.ndarray, Array]): Prediction values, possibly with multiple samples.
        bins (int): Number of bins for the 2D histogram. Defaults to 50.
        figsize (Tuple[int, int]): Figure size (width, height). Defaults to (8, 6).
        log_norm (bool): Apply logarithmic normalization to the color scale.
        x_log (bool): Set the x-axis to a logarithmic scale.
        y_log (bool): Set the y-axis to a logarithmic scale.
        log_base (int): Base of the logarithm (default: 2).
        min_value (float): Minimum value for data points (avoids log(0)).
        title (Optional[str]): Title of the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        seed (int): Random seed for reproducibility.
        log_bins (bool): Use logarithmically spaced bins based on `log_base`.
        normalize_cols (bool): Normalize each column in the density plot.

    Returns:
        matplotlib.figure.Figure: The figure object containing the heatmap.
    """
    # Convert inputs to NumPy arrays
    observed = np.asarray(observed)
    predictions = np.asarray(predictions)

    # Ensure observed data has the same shape as predictions (minus samples dim)
    if observed.shape != predictions.shape[1:]:
        raise ValueError(
            f"Observed data shape {observed.shape} does not match prediction shape {predictions.shape[1:]}"
        )

    # Flatten observed and prediction arrays, handling multiple posterior samples
    if predictions.ndim == observed.ndim + 1:
        # predictions shape: (n_samples, *observed.shape)
        n_samples = predictions.shape[0]
        obs_flat = observed.flatten()
        pred_flat = predictions.reshape(n_samples, -1).flatten()
        observed = np.tile(obs_flat, n_samples)
        predictions = pred_flat
    else:
        observed = observed.flatten()
        predictions = predictions.flatten()

    # Clip values to avoid log(0)
    observed = np.clip(observed, min_value, None)
    predictions = np.clip(predictions, min_value, None)

    # Compute common axis limits from the data
    common_min = min(observed.min(), predictions.min())
    common_max = max(observed.max(), predictions.max())

    # Decide on bin edges
    if log_bins:
        xedges = np.logspace(
            np.log(common_min) / np.log(log_base),
            np.log(common_max) / np.log(log_base),
            bins,
            base=log_base,
        )
        yedges = xedges
    else:
        xedges = np.linspace(common_min, common_max, bins)
        yedges = xedges

    # Compute the 2D histogram
    hist, xedges, yedges = np.histogram2d(observed, predictions, bins=[xedges, yedges])

    # Normalize columns if needed
    if normalize_cols:
        col_sums = hist.sum(axis=0, keepdims=True)
        hist = hist / (col_sums + 1e-8)

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    norm = LogNorm(vmin=max(1, hist[hist > 0].min())) if log_norm else None
    mesh = ax.pcolormesh(
        xedges, yedges, hist.T, shading="auto", cmap="viridis", norm=norm
    )
    fig.colorbar(
        mesh, ax=ax, label="Normalized Density" if normalize_cols else "Density"
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)

    # Perfect match line (dashed, semi-transparent)
    ax.plot(
        [common_min, common_max],
        [common_min, common_max],
        linestyle="--",
        linewidth=1,
        alpha=0.7,
        color="black",
    )

    # Set log scale if needed
    if x_log:
        ax.set_xscale("log", base=log_base)
    if y_log:
        ax.set_yscale("log", base=log_base)

    # Use the same range for both axes
    ax.set_xlim(common_min - 0.1, common_max + 0.5)
    ax.set_ylim(common_min - 0.1, common_max + 0.5)

    plt.tight_layout()
    plt.show()

    return fig


@beartype
def prior_data_geneset(
    prior_samples: Dict[str, Any],
    model_input: Dict[str, Any],
    adata_rna,
    geneset: List[str],
    subplot_size: Tuple[int, int] = (15, 12),
    window_size: int = 40,
    plot_alpha: bool = False,  # Toggle alpha plotting
    alpha_clamp: Tuple[float, float] = (1e-3, 1e5),
    plot_moving_average: bool = True,  # Toggle moving average plotting
) -> Figure:
    """
    Plot prior predictions (all samples) and observed RNA expression for selected genes,
    with an optional overlay of alpha_cg (transcription rates) on the same y-axis, and an optional
    moving average for the observed expression.
    """
    # 1) Shared time axis by averaging across all prior samples
    T_c_obs = np.mean(prior_samples["T_c"], axis=0)  # shape: (num_cells,)
    n_samples = prior_samples["T_c"].shape[0]

    # 2) Sort this time axis so smoothing aligns with ascending time
    sort_idx = np.argsort(T_c_obs)
    T_c_sorted = T_c_obs[sort_idx]

    T_c_sorted = T_c_sorted - np.min(T_c_sorted)

    # 3) Helper function to smooth only the y-values
    @beartype
    def smooth_expression(y: Array, window: int) -> np.ndarray:
        y = np.asarray(y)
        return np.convolve(y, np.ones(window) / window, mode="same")

    # 4) Observed data
    detection_y_c_med = np.mean(
        prior_samples["detection_y_c"], axis=0
    )  # shape: (num_cells,)
    M_c = model_input["M_c"]  # e.g. shape: (num_cells, 1, 1)
    rna_scaling = detection_y_c_med[:, None, None] * M_c

    observed_rna_adjusted = (
        np.stack(
            [
                adata_rna.layers["unspliced"].toarray(),
                adata_rna.layers["spliced"].toarray(),
            ],
            axis=2,
        )
        / rna_scaling
    )  # shape: (num_cells, num_genes, 2)

    # 5) Convert user-specified gene names to indices
    gene_indices = [np.where(adata_rna.var_names == gene)[0][0] for gene in geneset]

    # 6) Subplots
    n_genes = len(geneset)
    n_cols = int(np.ceil(np.sqrt(n_genes)))
    n_rows = int(np.ceil(n_genes / n_cols))
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=subplot_size, sharex=True, sharey=False
    )
    axes = np.atleast_1d(axes).flatten()

    # 7) Loop over each gene
    for ax, gene_idx, gene_name in zip(axes, gene_indices, geneset, strict=False):
        # Observed unspliced/spliced
        observed_unspliced = observed_rna_adjusted[:, gene_idx, 0] + 1e-2
        observed_spliced = observed_rna_adjusted[:, gene_idx, 1] + 1e-2

        # Sort them
        obs_u_sorted = observed_unspliced[sort_idx]
        obs_s_sorted = observed_spliced[sort_idx]

        # Smooth them
        obs_u_smooth = smooth_expression(obs_u_sorted, window_size)
        obs_s_smooth = smooth_expression(obs_s_sorted, window_size)

        # Plot Observed on main axis
        ax.scatter(
            T_c_sorted,
            obs_u_sorted,
            marker="x",
            color="red",
            alpha=0.8,
            label="Observed U",
        )
        ax.scatter(
            T_c_sorted,
            obs_s_sorted,
            marker="x",
            color="blue",
            alpha=0.8,
            label="Observed S",
        )
        if plot_moving_average:
            ax.plot(
                T_c_sorted, obs_u_smooth, color="darkred", linewidth=2, label="Smooth U"
            )
            ax.plot(
                T_c_sorted,
                obs_s_smooth,
                color="darkblue",
                linewidth=2,
                label="Smooth S",
            )

        # Plot all prior samples for unspliced/spliced on main axis
        for sample_idx in range(n_samples):
            unspliced_prior = (
                prior_samples["predictions_rearranged"][sample_idx, 0, :, gene_idx, 0]
                + 1e-2
            )
            spliced_prior = (
                prior_samples["predictions_rearranged"][sample_idx, 0, :, gene_idx, 1]
                + 1e-2
            )

            unspliced_sorted = unspliced_prior[sort_idx]
            spliced_sorted = spliced_prior[sort_idx]

            label_u = "Prior U" if sample_idx == 0 else None
            label_s = "Prior S" if sample_idx == 0 else None

            ax.scatter(
                T_c_sorted,
                unspliced_sorted,
                color="red",
                alpha=0.25 / n_samples,
                label=label_u,
            )
            ax.scatter(
                T_c_sorted,
                spliced_sorted,
                color="blue",
                alpha=0.25 / n_samples,
                label=label_s,
            )

        # Optionally plot alpha on the same y-axis
        if plot_alpha and "alpha_cg" in prior_samples:
            for sample_idx in range(n_samples):
                alpha_prior = prior_samples["alpha_cg"][
                    sample_idx, :, gene_idx
                ]  # shape: (num_cells,)
                alpha_sorted = alpha_prior[sort_idx]

                # Clamp to avoid extreme log scales
                alpha_clamped = np.clip(alpha_sorted, alpha_clamp[0], alpha_clamp[1])

                label_a = "Alpha" if sample_idx == 0 else None
                ax.plot(
                    T_c_sorted,
                    alpha_clamped,
                    color="green",
                    alpha=1,
                    linewidth=1,
                    label=label_a,
                )

        # Finishing touches per subplot
        ax.set_title(gene_name)
        ax.set_xlabel("Time (T_c)")
        ax.set_ylabel("Expression")
        ax.set_yscale("log")

    # Remove extra subplots if any
    for ax in axes[n_genes:]:
        ax.set_visible(False)

    # Create one global legend above the subplots.
    # Gather unique handles and labels from all axes
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l, strict=False):
            if label is not None and label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(4, len(labels)),
        bbox_to_anchor=(0.5, 0.98),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    return fig


@beartype
def posterior_data_geneset(
    posterior: Dict[str, Any],
    model_input: Dict[str, Any],
    adata_rna,
    geneset: List[str],
    subplot_size: Tuple[int, int] = (15, 12),
    window_size: int = 50,
    plot_alpha: bool = False,  # Toggle alpha plotting
    alpha_clamp: Tuple[float, float] = (1e-3, 1e5),
    plot_moving_average: bool = True,  # Toggle moving average plotting
) -> Figure:
    """
    Plot posterior mean predictions and observed RNA expression for selected genes,
    with an optional overlay of posterior α (transcription rates) on the same y-axis,
    and an optional moving average for the observed expression.
    """

    # Helper function to extract the mean estimate for a given key.
    def get_mean_estimate(key: str) -> np.ndarray:
        if "means" in posterior and key in posterior["means"]:
            candidate = np.asarray(posterior["means"][key])
        elif "medians" in posterior and key in posterior["medians"]:
            candidate = np.asarray(posterior["medians"][key])
        elif "posterior_samples" in posterior and key in posterior["posterior_samples"]:
            candidate = np.mean(np.asarray(posterior["posterior_samples"][key]), axis=0)
        elif "deterministic" in posterior and key in posterior["deterministic"]:
            candidate = np.mean(posterior["deterministic"][key], axis=0)
        else:
            raise ValueError(f"Key '{key}' not found in posterior estimates.")
        return candidate

    # 1) Get the common (mean) time axis from the posterior.
    T_c_est = get_mean_estimate("T_c")  # Expected shape: (num_cells,)
    if T_c_est.ndim != 1:
        raise ValueError(f"Expected T_c to be 1D (per cell), got shape {T_c_est.shape}")
    n_cells = T_c_est.shape[0]

    # 2) Sort the time axis so that smoothing is applied in ascending time.
    sort_idx = np.argsort(T_c_est)
    T_c_sorted = T_c_est[sort_idx]

    T_c_sorted = T_c_sorted - np.min(T_c_sorted)

    # 3) Helper function: smooth only the y-values (expression)
    @beartype
    def smooth_expression(y: Array, window: int) -> np.ndarray:
        y = np.asarray(y)
        return np.convolve(y, np.ones(window) / window, mode="same")

    # 4) Prepare observed data (as in prior_data_geneset)
    detection_y_c_med = get_mean_estimate("detection_y_c")  # shape: (num_cells,)
    M_c = model_input["M_c"]  # e.g. shape: (num_cells, 1, 1)
    rna_scaling = detection_y_c_med[:, None, None] * M_c

    # helper to get a float32 ndarray from a layer
    def _to_dense_f32(layer):
        if sparse.issparse(layer):
            # cast & densify in one shot
            return layer.astype(np.float32).toarray()
        else:
            return np.asarray(layer, dtype=np.float32)

    observed_rna_adjusted = (
        np.stack(
            [
                _to_dense_f32(adata_rna.layers["unspliced"]),
                _to_dense_f32(adata_rna.layers["spliced"]),
            ],
            axis=2,
        )
        / rna_scaling
    )  # shape: (num_cells, num_genes, 2)

    # 5) Convert the geneset to gene indices.
    gene_indices = [np.where(adata_rna.var_names == gene)[0][0] for gene in geneset]

    # 6) Figure layout.
    n_genes = len(geneset)
    n_cols = int(np.ceil(np.sqrt(n_genes)))
    n_rows = int(np.ceil(n_genes / n_cols))
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=subplot_size, sharex=True, sharey=False
    )
    axes = np.atleast_1d(axes).flatten()

    # 7) Get the posterior predicted expression ("mu") mean.
    # Expected shape: (num_cells, num_genes, 2) with last dimension: [unspliced, spliced]
    mu_est = get_mean_estimate("predictions_rearranged")[:, 0, ...]

    # 8) Optionally get posterior α if available.
    if plot_alpha:
        try:
            alpha_est = get_mean_estimate(
                "alpha_cg"
            )  # Expected shape: (num_cells, num_genes)
        except ValueError:
            alpha_est = None
            plot_alpha = False

    # 9) Loop over each gene and plot.
    for ax, gene_idx, gene_name in zip(axes, gene_indices, geneset, strict=False):
        # --- Observed data ---
        observed_unspliced = observed_rna_adjusted[:, gene_idx, 0] + 1e-2
        observed_spliced = observed_rna_adjusted[:, gene_idx, 1] + 1e-2

        obs_u_sorted = observed_unspliced[sort_idx]
        obs_s_sorted = observed_spliced[sort_idx]

        obs_u_smooth = smooth_expression(obs_u_sorted, window_size)
        obs_s_smooth = smooth_expression(obs_s_sorted, window_size)

        ax.scatter(
            T_c_sorted,
            obs_u_sorted,
            marker="x",
            color="red",
            alpha=0.2,
            label="Observed U",
        )
        ax.scatter(
            T_c_sorted,
            obs_s_sorted,
            marker="x",
            color="blue",
            alpha=0.2,
            label="Observed S",
        )
        if plot_moving_average:
            ax.plot(
                T_c_sorted, obs_u_smooth, color="darkred", linewidth=2, label="Smooth U"
            )
            ax.plot(
                T_c_sorted,
                obs_s_smooth,
                color="darkblue",
                linewidth=2,
                label="Smooth S",
            )

        # --- Posterior predictions ---
        unspliced_pred = mu_est[:, gene_idx, 0] + 1e-2  # shape: (num_cells,)
        spliced_pred = mu_est[:, gene_idx, 1] + 1e-2  # shape: (num_cells,)

        unspliced_pred_sorted = unspliced_pred[sort_idx]
        spliced_pred_sorted = spliced_pred[sort_idx]

        ax.plot(
            T_c_sorted,
            unspliced_pred_sorted,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Post. U",
        )
        ax.plot(
            T_c_sorted,
            spliced_pred_sorted,
            color="blue",
            linestyle="--",
            linewidth=2,
            label="Post. S",
        )

        # --- Optionally plot posterior α on the same y-axis ---
        if plot_alpha and alpha_est is not None:
            alpha_gene = alpha_est[:, gene_idx]  # shape: (num_cells,)
            alpha_sorted = alpha_gene[sort_idx]
            alpha_clamped = np.clip(alpha_sorted, alpha_clamp[0], alpha_clamp[1])
            ax.plot(
                T_c_sorted,
                alpha_clamped,
                color="green",
                linestyle="-",
                linewidth=2,
                label="Post. Alpha",
            )

        ax.set_title(gene_name)
        ax.set_xlabel("Time (T_c)")
        ax.set_ylabel("Expression")
        ax.set_yscale("log")

    for ax in axes[n_genes:]:
        ax.set_visible(False)

    # Create one global legend above the subplots.
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l, strict=False):
            if label is not None and label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(4, len(labels)),
        bbox_to_anchor=(0.5, 0.98),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    return fig


def plot_elbo_loss(
    losses, directory=None, figsize=(12, 5), save=False, dpi=300, save_format="png"
):
    """
    Plot the ELBO loss over all iterations and the last 10%, with optional saving.

    Parameters
    ----------
    losses : list or np.ndarray
        List or array of ELBO loss values over iterations.
    directory : str, optional
        Directory where figures will be saved (required if save=True).
    figsize : tuple, optional
        Figure size for the plots (default: (12, 5)).
    save : bool, optional
        Whether to save the plots (default: False).
    dpi : int, optional
        Resolution of the saved figure in dots per inch (default: 300).
    save_format : str, optional
        File format for saving figures (default: "png", e.g., "pdf", "svg", etc.).
    """
    if save and directory is None:
        warnings.warn(
            "Saving is enabled, but no directory was provided. Figures will not be saved.",
            UserWarning,
        )

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Plot all iterations
    axes[0].plot(range(len(losses)), losses, label="Scaled ELBO Loss")
    axes[0].set_xlabel("Iteration")
    axes[0].set_ylabel("Scaled ELBO Loss")
    axes[0].set_title("SVI Training Loss with Scaled ELBO")
    axes[0].legend()
    axes[0].grid(True)

    # Ensure last_10_percent is at least 1 to avoid an empty slice
    last_10_percent = max(1, int(np.round(len(losses) / 10)))

    # Plot last 10% of iterations
    axes[1].plot(
        range(len(losses) - last_10_percent, len(losses)),
        losses[-last_10_percent:],
        label="Scaled ELBO Loss",
    )
    axes[1].set_xlabel("Iteration")
    axes[1].set_ylabel("Scaled ELBO Loss")
    axes[1].set_title("SVI Training Loss (Last 10%)")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()

    if save and directory:
        plt.savefig(
            f"{directory}/ELBOloss_All.{save_format}", dpi=dpi, format=save_format
        )

    plt.show()


@beartype
def posterior_data_geneset_multipath(
    posterior: Dict[str, Any],
    model_input: Dict[str, Any],
    adata_rna,
    geneset: List[str],
    paths: List[int],
    subplot_size: Tuple[int, int] = (15, 12),
    window_size: int = 50,
    plot_alpha: bool = False,
    alpha_clamp: Tuple[float, float] = (1e-3, 1e5),
    plot_moving_average: bool = False,
) -> Figure:
    """
    Generate side‐by‐side plots of posterior mean predictions and observed RNA expression
    for a selected set of genes across multiple lineage paths.

    This function arranges a grid of subplots where each row corresponds to one gene in
    `geneset` and each column corresponds to one path index from `paths`. For each subplot,
    it overlays:
      - Observed unspliced (U) and spliced (S) counts (after adjusting by the model’s
        deterministic normalizing and additive terms), optionally smoothed via moving
        average.
      - Posterior predictions of U, S, and protein abundance from the `posterior` object.
      - Optionally, the posterior estimate of transcription rate α (per gene, not path‐specific).

    Observed points are shown in lighter colors (“salmon” for U, “skyblue” for S), while
    posterior predictions use darker shades (“red”/“blue” for U/S, “black” for protein).
    If `plot_moving_average=True`, a smoothed curve of observed data is overlaid.

    Parameters
    ----------
    posterior : dict[str, Any]
        Dictionary containing posterior estimates generated by the model. Expected keys:
        - "means", "medians", "posterior_samples", or "deterministic" entries for at least:
          • "T_c"                (shape: [n_cells])
          • "normalizing_term"   (shape: [n_cells, 1, 1])
          • "additive_term"      (shape: [n_cells, n_genes, 2])
          • "sol_at_cells"       (shape: [n_cells, n_paths, n_genes, 3], where 3 = [U, S, protein])
          Optionally:
          • "alpha_cg"           (shape: [n_cells, n_genes], if `plot_alpha=True`)
    model_input : dict[str, Any]
        Dictionary of inputs used to generate the posterior. This argument is accepted for
        consistency with related pipeline functions but is not used directly in this routine.
    adata_rna : AnnData
        Annotated data matrix containing single‐cell RNA counts. Must include:
        - `adata_rna.layers['unspliced']`: (n_cells × n_genes) unspliced counts
        - `adata_rna.layers['spliced']`:   (n_cells × n_genes) spliced counts
        - `adata_rna.var_names`:           Array of gene names, length = n_genes
    geneset : list[str]
        List of gene names (strings) to plot. Each gene name must appear in `adata_rna.var_names`.
    paths : list[int]
        List of integer indices specifying which lineage paths to plot. These indices correspond
        to the second axis of the posterior “sol_at_cells” estimate.
    subplot_size : tuple[int, int], optional
        Overall size (width, height) in inches of the figure containing all subplots.
        Default: (15, 12).
    window_size : int, optional
        Window length for computing a moving average of the observed U/S counts
        (using a simple uniform filter). Default: 50.
    plot_alpha : bool, optional
        If True, overlay the posterior estimate of the transcription rate α (for each gene)
        on every subplot. Default: False. If “alpha_cg” is missing from `posterior`, it will
        silently disable α plotting.
    alpha_clamp : tuple[float, float], optional
        Lower and upper bounds to which the α values are clamped before plotting
        (only used if `plot_alpha=True`). Default: (1e-3, 1e5).
    plot_moving_average : bool, optional
        If True, draw a smoothed curve (window=window_size) of the observed U/S data
        in each subplot. Default: True.

    Returns
    -------
    fig : matplotlib.figure.Figure
        A Matplotlib Figure object containing a grid of subplots with one row per gene
        and one column per path. Each subplot shows:
          - Observed unspliced (U) and spliced (S) counts (as “x” markers, lighter colors),
            optionally smoothed.
          - Posterior predictions of U, S (dashed lines), and protein (solid black line).
          - Optionally, posterior α (solid green line).
        The y‐axis of each subplot is on a log scale.

    Raises
    ------
    ValueError
        - If a required key (e.g., "T_c", "normalizing_term", "sol_at_cells") is not found
          in the `posterior` dictionary (via the helper `get_mean_estimate`).
        - If any gene in `geneset` cannot be located in `adata_rna.var_names`.

    Notes
    -----
    1. Time sorting: The common time axis “T_c” is extracted, sorted in ascending order,
       and shifted such that its minimum is zero. All observed and predicted quantities
       are then plotted against this sorted time.
    2. Adjusted observed data: Raw U/S counts from `adata_rna.layers` are divided by
       the “normalizing_term” (per‐cell scalar) and subtracted by the “additive_term”
       (per‐cell, per‐gene 2‐vector). A small constant (1e-2) is added to avoid zeros
       before log‐scaling.
    3. Posterior estimates: The function checks for “means” → “medians” → “posterior_samples”
       → “deterministic” in `posterior` for each required key. If “posterior_samples” is used,
       it takes the mean along axis 0.
    4. Plot aesthetics:
       - Observed U: salmon “x” markers (α=0.3)
       - Observed S: skyblue “x” markers (α=0.3)
       - Smoothed U: darksalmon line, width=2
       - Smoothed S: deepskyblue line, width=2
       - Posterior U: red dashed line, width=4
       - Posterior S: blue dashed line, width=4
       - Posterior Protein: black solid line, α=0.33, width=2
       - Posterior α (if plotted): green solid line, clamped to `alpha_clamp`
    5. Global legend: A single legend is placed above all subplots to identify all line types.

    Examples
    --------
    >>> # Suppose `posterior`, `model_input`, and `adata_rna` are already defined:
    >>> genes_to_plot = ['EOMES', 'ISL1', 'MYH6', 'MYH7', 'CDH5', 'PLVAP', 'DDR2', 'TCF21']
    >>> paths_to_plot = [0, 1, 2]
    >>> fig = posterior_data_geneset_multipath(
    ...     posterior=posterior,
    ...     model_input=model_input,
    ...     adata_rna=adata_rna,
    ...     geneset=genes_to_plot,
    ...     paths=paths_to_plot,
    ...     subplot_size=(10, 20),
    ...     plot_alpha=True,
    ...     plot_moving_average=False,
    ... )
    >>> # This call generates a figure with 8 rows (genes) and 3 columns (paths), each subplot
    >>> # comparing observed vs. posterior U/S/protein (and α if requested).
    """

    # Helper function to extract the mean estimate for a given key.
    def get_mean_estimate(key: str) -> np.ndarray:
        if "means" in posterior and key in posterior["means"]:
            candidate = np.asarray(posterior["means"][key])
        elif "medians" in posterior and key in posterior["medians"]:
            candidate = np.asarray(posterior["medians"][key])
        elif "posterior_samples" in posterior and key in posterior["posterior_samples"]:
            candidate = np.mean(np.asarray(posterior["posterior_samples"][key]), axis=0)
        elif "deterministic" in posterior and key in posterior["deterministic"]:
            candidate = np.mean(posterior["deterministic"][key], axis=0)
        else:
            raise ValueError(f"Key '{key}' not found in posterior estimates.")
        return candidate

    # 1) Get the common (mean) time axis from the posterior.
    T_c_est = get_mean_estimate("T_c")  # shape: (num_cells,)
    n_cells = T_c_est.shape[0]

    # 2) Sort the time axis so that smoothing is applied in ascending time.
    sort_idx = np.argsort(T_c_est)
    T_c_sorted = T_c_est[sort_idx] - np.min(T_c_est)

    # 3) Helper function: smooth only the y-values (expression)
    @beartype
    def smooth_expression(y: Any, window: int) -> np.ndarray:
        y = np.asarray(y)
        return np.convolve(y, np.ones(window) / window, mode="same")

    # 4) Adjust observed RNA data using the model's deterministic terms.
    normalizing_term = get_mean_estimate("normalizing_term")  # shape: (num_cells, 1, 1)
    additive_term = get_mean_estimate(
        "additive_term"
    )  # shape: (num_cells, num_genes, 2)

    raw_observed = np.stack(
        [
            adata_rna.layers["unspliced"].toarray(),
            adata_rna.layers["spliced"].toarray(),
        ],
        axis=2,
    )  # shape: (num_cells, num_genes, 2)

    observed_rna_adjusted = raw_observed / normalizing_term - additive_term

    # 5) Convert the geneset to gene indices.
    gene_indices = [np.where(adata_rna.var_names == gene)[0][0] for gene in geneset]
    n_genes = len(geneset)

    # 6) Determine grid dimensions: rows = genes, columns = paths
    n_paths = len(paths)
    n_rows = n_genes
    n_cols = n_paths

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=subplot_size, sharex=True, sharey=False
    )
    axes = np.array(axes).reshape(n_rows, n_cols)

    # 7) Get the posterior predicted expression ("sol_at_cells") mean.
    #    Expected shape: (num_cells, num_paths, num_genes, 3) where 3 = [unspliced, spliced, protein]
    predictions_mean = get_mean_estimate("sol_at_cells")
    mu_rna_est = predictions_mean[
        ..., :2
    ]  # shape: (num_cells, num_paths, num_genes, 2)
    protein_est = predictions_mean[..., 2]  # shape: (num_cells, num_paths, num_genes)

    # 8) Optionally get posterior α if available (shape: (num_cells, num_genes))
    if plot_alpha:
        try:
            alpha_est = get_mean_estimate("alpha_cg")  # shape: (num_cells, num_genes)
        except ValueError:
            alpha_est = None
            plot_alpha = False

    # 9) Loop over each gene (row) and each path (column) and plot.
    for i, (gene_idx, gene_name) in enumerate(zip(gene_indices, geneset)):
        # Extract observed data for this gene (same for all paths)
        observed_unspliced = observed_rna_adjusted[:, gene_idx, 0] + 1e-2
        observed_spliced = observed_rna_adjusted[:, gene_idx, 1] + 1e-2

        obs_u_sorted = observed_unspliced[sort_idx]
        obs_s_sorted = observed_spliced[sort_idx]

        if plot_moving_average:
            obs_u_smooth = smooth_expression(obs_u_sorted, window_size)
            obs_s_smooth = smooth_expression(obs_s_sorted, window_size)

        for j, path_idx in enumerate(paths):
            ax = axes[i, j]

            # --- Observed points (lighter colors) ---
            ax.scatter(
                T_c_sorted,
                jnp.clip(obs_u_sorted, 1e-2),
                marker="x",
                color="salmon",
                alpha=0.3,
                label="Observed U",
            )
            ax.scatter(
                T_c_sorted,
                jnp.clip(obs_s_sorted, 1e-2),
                marker="x",
                color="skyblue",
                alpha=0.3,
                label="Observed S",
            )
            if plot_moving_average:
                ax.plot(
                    T_c_sorted,
                    obs_u_smooth,
                    color="darksalmon",
                    linewidth=2,
                    label="Smooth U",
                )
                ax.plot(
                    T_c_sorted,
                    obs_s_smooth,
                    color="deepskyblue",
                    linewidth=2,
                    label="Smooth S",
                )

            # --- Posterior predictions for this gene & path (darker red/blue) ---
            unspliced_pred = mu_rna_est[:, path_idx, gene_idx, 0] + 1e-2
            spliced_pred = mu_rna_est[:, path_idx, gene_idx, 1] + 1e-2

            unspliced_pred_sorted = unspliced_pred[sort_idx]
            spliced_pred_sorted = spliced_pred[sort_idx]

            # Predicted Protein
            protein_pred = protein_est[:, path_idx, gene_idx] + 1e-2
            protein_pred_sorted = np.clip(protein_pred[sort_idx], 10 ** (-2), None)
            ax.plot(
                T_c_sorted,
                protein_pred_sorted,
                color="black",
                linestyle="-",
                linewidth=2,
                label="Post. Protein",
                alpha=0.33,
            )

            ax.plot(
                T_c_sorted,
                unspliced_pred_sorted,
                color="red",
                linestyle="--",
                linewidth=4,
                label="Post. U",
            )
            ax.plot(
                T_c_sorted,
                spliced_pred_sorted,
                color="blue",
                linestyle="--",
                linewidth=4,
                label="Post. S",
            )

            # Optionally plot posterior α (same curve for all paths, per gene)
            if plot_alpha and (alpha_est is not None):
                alpha_gene = alpha_est[:, gene_idx]
                alpha_sorted = alpha_gene[sort_idx]
                alpha_clamped = np.clip(alpha_sorted, alpha_clamp[0], alpha_clamp[1])
                ax.plot(
                    T_c_sorted,
                    alpha_clamped,
                    color="green",
                    linestyle="-",
                    linewidth=2,
                    label="Post. Alpha",
                )

            # Title and axis labels
            ax.set_title(f"{gene_name} | Path {path_idx}")
            if i == n_rows - 1:
                ax.set_xlabel("Time (T_c)")
            ax.set_ylabel("Expression")
            ax.set_yscale("log")

    # 10) Build one global legend above all subplots.
    handles, labels = [], []
    for ax_row in axes:
        for ax in ax_row:
            h, l = ax.get_legend_handles_labels()
            for handle, label in zip(h, l):
                if (label is not None) and (label not in labels):
                    handles.append(handle)
                    labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(4, len(labels)),
        bbox_to_anchor=(0.5, 0.98),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    return fig
