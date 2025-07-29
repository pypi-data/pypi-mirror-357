from functools import partial

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
import optax
from numpyro.handlers import block, seed
from numpyro.infer import SVI, Trace_ELBO
from numpyro.infer.autoguide import AutoGuideList, AutoNormal

# =============================================================================
# 1) Pure‐JAX amortization network forward pass
# =============================================================================

def _make_network_forward(
    pytree_params: dict,
    data_array: jnp.ndarray,
    predict_detection_y: bool,
    predict_detection_l: bool,
    predict_path_weights: bool,
):
    """
    Pure‐JAX version of the amortization network.  Inputs:
      - pytree_params: dict mapping parameter names → JAX DeviceArrays
      - data_array:    shape = (n_cells, n_genes, n_mods)
      - predict_detection_y: whether to compute the detection_y_c branch
      - predict_detection_l: whether to compute the detection_l_c branch
      - predict_path_weights: whether to compute the path_weights branch
    Returns a flat tuple of arrays, in this order:
      (loc_t, scale_t,
       loc_y?, scale_y?,
       loc_l?, scale_l?,
       conc_pw?)
    """
    n_cells, n_genes, n_mods = data_array.shape
    d_in = n_genes * n_mods

    # 1) flatten & normalize counts
    data_2d = data_array.reshape((n_cells, d_in))  # → (n_cells, d_in)
    data_norm = data_2d / (jnp.sum(data_2d, axis=1, keepdims=True) + 1e-8)
    feat = jnp.log1p(data_norm)  # (n_cells, d_in)

    # 2) shared hidden layer
    V_shared = pytree_params["V_shared"]  # (d_in, H_shared)
    c_shared = pytree_params["c_shared"]  # (H_shared,)
    h_shared = jax.nn.elu(feat @ V_shared + c_shared)  # (n_cells, H_shared)

    outputs = []

    # ----- t_c branch -----
    V_t_c = pytree_params["V_t_c"]  # (H_shared, H_t)
    c_t_c = pytree_params["c_t_c"]  # (H_t,)
    V_out_t_c = pytree_params["V_out_t_c"]  # (H_t, 2)
    c_out_t_c = pytree_params["c_out_t_c"]  # (2,)

    h_t = jax.nn.elu(h_shared @ V_t_c + c_t_c)  # (n_cells, H_t)
    t_out = h_t @ V_out_t_c + c_out_t_c  # (n_cells, 2)
    loc_t = t_out[:, 0]  # (n_cells,)
    scale_t = jax.nn.softplus(t_out[:, 1]) + 1e-3  # (n_cells,)
    outputs.append(loc_t)
    outputs.append(scale_t)

    # ----- detection_y_c branch -----
    if predict_detection_y:
        V_det = pytree_params["V_det"]  # (H_shared, H_det)
        c_det = pytree_params["c_det"]  # (H_det,)
        V_out_det = pytree_params["V_out_det"]  # (H_det, 2)
        c_out_det = pytree_params["c_out_det"]  # (2,)

        h_y = jax.nn.elu(h_shared @ V_det + c_det)  # (n_cells, H_det)
        y_out = h_y @ V_out_det + c_out_det  # (n_cells, 2)
        loc_y = y_out[:, 0]  # (n_cells,)
        scale_y = jax.nn.softplus(y_out[:, 1]) + 1e-3  # (n_cells,)
        outputs.append(loc_y)
        outputs.append(scale_y)

    # ----- detection_l_c branch -----
    if predict_detection_l:
        V_det_l = pytree_params["V_det_l"]  # (H_shared, H_det)
        c_det_l = pytree_params["c_det_l"]  # (H_det,)
        V_out_det_l = pytree_params["V_out_det_l"]  # (H_det, 2)
        c_out_det_l = pytree_params["c_out_det_l"]  # (2,)

        h_l = jax.nn.elu(h_shared @ V_det_l + c_det_l)  # (n_cells, H_det)
        l_out = h_l @ V_out_det_l + c_out_det_l  # (n_cells, 2)
        loc_l = l_out[:, 0]  # (n_cells,)
        scale_l = jax.nn.softplus(l_out[:, 1]) + 1e-3  # (n_cells,)
        outputs.append(loc_l)
        outputs.append(scale_l)

    # ----- path_weights branch -----
    if predict_path_weights:
        num_paths = pytree_params["V_pw"].shape[1]
        V_pw       = pytree_params["V_pw"]       # (H_shared, num_paths)
        c_pw       = pytree_params["c_pw"]       # (num_paths,)
        V_out_pw   = pytree_params["V_out_pw"]   # (num_paths, 2 * num_paths)
        c_out_pw   = pytree_params["c_out_pw"]   # (2 * num_paths,)

        h_pw = jax.nn.elu(h_shared @ V_pw + c_pw)        # (n_cells, num_paths)
        z_out = h_pw @ V_out_pw + c_out_pw               # (n_cells, 2 * num_paths)
        loc_z       = z_out[:, :num_paths]               # (n_cells, num_paths)
        raw_scale_z = z_out[:, num_paths:]               # (n_cells, num_paths)
        scale_z = jax.nn.softplus(raw_scale_z) + 1e-3    # (n_cells, num_paths)

        outputs.append(loc_z)
        outputs.append(scale_z)

    return tuple(outputs)

# JIT‐compile the network forward
_network_forward = jax.jit(
    _make_network_forward,
    static_argnames=(
        "predict_detection_y",
        "predict_detection_l",
        "predict_path_weights",
    ),
)

# =============================================================================
# 2) Rewrite amortized_guide to call the JIT‐compiled network_forward
# =============================================================================


def amortized_guide(
    *args,
    predict_detection_l_c: bool = False,
    predict_detection_y_c: bool = True,
    predict_path_weights: bool = False,
    init_net_params: dict = None,
    init_seed: int = 0,
    **kwargs,
):
    """
    An optimized amortized guide that JIT‐compiles the network forward pass once,
    then reuses it on each sample call. Registers all NN parameters with
    numpyro.param, then calls _network_forward(params, data, ...) in one shot.
    """
    # --- 1) Retrieve data & flags from args/kwargs ---
    data = kwargs.get("data", None)
    if data is None:
        if len(args) > 0:
            data = args[0]
        else:
            raise ValueError(
                "amortized_guide expects 'data' as a keyword or first positional argument"
            )

    # Split once into `n_keys` subkeys
    n_keys = 18
    base_key = jax.random.PRNGKey(init_seed)
    all_keys = jax.random.split(base_key, n_keys)

    if predict_path_weights:
        num_paths = kwargs.get("num_paths", None)

    # --- 2) Get network dimensions from data shape ---
    n_cells, n_genes, n_mods = data.shape
    H_shared, H_t, H_det = 256, 128, 128
    out_dim = 2

    # Helper to initialize or reuse parameters
    def make(name, shape, rng):
        if init_net_params and (name in init_net_params):
            return init_net_params[name].astype(jnp.float32)
        return jax.random.normal(rng, shape, dtype=jnp.float32) * 0.01

    # --- 3) Define all NN parameters via numpyro.param ---
    params = {}
    params["V_shared"] = numpyro.param(
        "V_shared",
        make("V_shared", (n_genes * n_mods, H_shared), all_keys[0]),
    )
    params["c_shared"] = numpyro.param(
        "c_shared", make("c_shared", (H_shared,), all_keys[1])
    )
    params["V_t_c"] = numpyro.param(
        "V_t_c", make("V_t_c", (H_shared, H_t), all_keys[2])
    )
    params["c_t_c"] = numpyro.param(
        "c_t_c", make("c_t_c", (H_t,), all_keys[3])
    )
    params["V_out_t_c"] = numpyro.param(
        "V_out_t_c", make("V_out_t_c", (H_t, out_dim), all_keys[4])
    )
    params["c_out_t_c"] = numpyro.param(
        "c_out_t_c", make("c_out_t_c", (out_dim,), all_keys[5])
    )

    if predict_detection_y_c:
        params["V_det"] = numpyro.param(
            "V_det", make("V_det", (H_shared, H_det), all_keys[6])
        )
        params["c_det"] = numpyro.param(
            "c_det", make("c_det", (H_det,), all_keys[7])
        )
        params["V_out_det"] = numpyro.param(
            "V_out_det", make("V_out_det", (H_det, out_dim), all_keys[8])
        )
        params["c_out_det"] = numpyro.param(
            "c_out_det", make("c_out_det", (out_dim,), all_keys[9])
        )

    if predict_detection_l_c:
        params["V_det_l"] = numpyro.param(
            "V_det_l", make("V_det_l", (H_shared, H_det), all_keys[10])
        )
        params["c_det_l"] = numpyro.param(
            "c_det_l", make("c_det_l", (H_det,), all_keys[11])
        )
        params["V_out_det_l"] = numpyro.param(
            "V_out_det_l", make("V_out_det_l", (H_det, out_dim), all_keys[12])
        )
        params["c_out_det_l"] = numpyro.param(
            "c_out_det_l", make("c_out_det_l", (out_dim,), all_keys[13])
        )

    if predict_path_weights:
        params["V_pw"] = numpyro.param(
            "V_pw",
            make("V_pw", (H_shared, num_paths), all_keys[14]),
            constraint=dist.constraints.real,
        )
        params["c_pw"] = numpyro.param(
            "c_pw", make("c_pw", (num_paths,), all_keys[15])
        )
        params["V_out_pw"] = numpyro.param(
            "V_out_pw", make("V_out_pw", (num_paths, 2*num_paths), all_keys[16])
        )
        params["c_out_pw"] = numpyro.param(
            "c_out_pw", make("c_out_pw", (2*num_paths,), all_keys[17])
        )

    # --- 4) One‐shot JIT‐compiled forward pass for the entire batch of cells ---
    outputs = _network_forward(
        params, data, predict_detection_y_c, predict_detection_l_c, predict_path_weights,
    )

    # --- 5) Unpack outputs exactly in the same order as above ---
    idx = 0
    loc_t = outputs[idx]
    idx += 1  # (n_cells,)
    scale_t = outputs[idx]
    idx += 1  # (n_cells,)
    dists = [dist.Normal(loc_t, scale_t)]
    names = ["t_c"]

    if predict_detection_y_c:
        loc_y = outputs[idx]
        idx += 1  # (n_cells,)
        scale_y = outputs[idx]
        idx += 1  # (n_cells,)
        dists.append(
            dist.TransformedDistribution(
                dist.Normal(loc_y, scale_y), dist.transforms.ExpTransform()
            )
        )
        names.append("detection_y_c")

    if predict_detection_l_c:
        loc_l = outputs[idx]
        idx += 1  # (n_cells,)
        scale_l = outputs[idx]
        idx += 1  # (n_cells,)
        dists.append(
            dist.TransformedDistribution(
                dist.Normal(loc_l, scale_l), dist.transforms.ExpTransform()
            )
        )
        names.append("detection_l_c")

    if predict_path_weights:
        loc_z   = outputs[idx]
        scale_z = outputs[idx + 1]
        idx += 2

        numpyro.sample(
            "z_pw", dist.Normal(loc_z, scale_z).to_event(1)  # → (n_cells, num_paths)
        )

    # --- 6) Plate over cells to sample each latent from its distribution ---
    with numpyro.plate("cells", n_cells):
        for nm, sd in zip(names, dists):
            numpyro.sample(nm, sd)

    return {}

# =============================================================================
# 3) JIT‐compile the entire SVI warm‐up loop
# =============================================================================

def run_svi_warmup(
    initial_state,
    initial_rng,
    svi,
    data,
    prior_time,
    T_limits,
    prior_time_sd,
    prior_path,
    num_paths,
    n_steps,
):
    """
    Runs n_steps of svi.update(...) in a single jax.lax.scan, then returns
    (final_state, losses). This is JIT‐compilable because svi and n_steps
    are marked as static.
    """

    def body_fun(carry, _):
        state, rng = carry
        rng, subkey = jax.random.split(rng)
        state, loss = svi.update(
            state,
            data=data,
            prior_time=prior_time,
            T_limits=T_limits,
            prior_time_sd=prior_time_sd,
            prior_path=prior_path,
            num_paths=num_paths,
        )
        return (state, rng), loss

    (final_state, _), losses = jax.lax.scan(
        body_fun, (initial_state, initial_rng), None, length=n_steps
    )
    return final_state, losses

def warm_up_guide(
    model,
    model_input: dict,
    predict_detection_l_c: bool = False,
    predict_detection_y_c: bool = False,
    predict_path_weights: bool = False,
    n_steps: int = 1000,
    seed: int = 0,
) -> dict:

    if predict_path_weights is None:
        num_paths = model_input["num_paths"]
    else:
        num_paths = 1

    amortized_fn = partial(
        amortized_guide,
        predict_detection_l_c=predict_detection_l_c,
        predict_detection_y_c=predict_detection_y_c,
        init_net_params=None,
        num_paths= num_paths,
    )

    # --- 1) Define a minimal prior-only model ----------

    def prior_only_tp_model(
        data,  # (n_cells, …)  – unused
        prior_time,  # (n_cells,)
        T_limits,  # (low, high)
        prior_time_sd,  # float
        prior_path,  # (n_cells,)  contains -2 / -1 / ≥0
        num_paths = None,  # int
    ):
        n_cells = prior_time.shape[0]

        # a) Truncated-Normal prior for t_c (exactly as before)
        with numpyro.plate("cells", n_cells):
            numpyro.sample(
                "t_c",
                dist.TruncatedNormal(
                    loc=prior_time,
                    scale=prior_time_sd,
                    low=T_limits[0],
                    high=T_limits[1],
                ),
            )

        if num_paths is not None:
            # b) Logistic-Normal prior for z_pw

            # 1) Build a mask of “known” cells
            known_mask = prior_path >= 0

            # 2) One‐hot encode the known path index (0…num_paths−1). For unknown cells, we ignore this.
            one_hot_known = jax.nn.one_hot(
                jnp.clip(prior_path, 0, num_paths - 1),
                num_paths
            )  # shape = (n_cells, num_paths)

            # 3) Set loc[i] = 3·one_hot_known[i] if cell i is known, else 0-vector
            loc_matrix = jnp.where(
                known_mask[:, None],
                one_hot_known * 3.0,
                jnp.zeros((n_cells, num_paths))
            )

            # 4) Fixed scale = 0.1 for all cells & all paths
            scale_matrix = jnp.ones((n_cells, num_paths)) * 0.1

            # 5) Sample
            numpyro.sample(
                "z_pw",
                dist.Normal(loc=loc_matrix, scale=scale_matrix).to_event(1),
            )

    # --- 2) Extract constants from model_input ---------
    data = model_input["data"]
    prior_time = model_input["prior_time"]
    T_limits = model_input["T_limits"]
    prior_time_sd = model_input["prior_timespan"] / 100.0
    if predict_path_weights:
        prior_path = model_input["prior_path"]
        num_paths = model_input["num_paths"]
    else:
        num_paths = None
        prior_path = None

    # --- 3) SVI setup (same Adam, same Trace_ELBO) ---
    optimizer = optax.adam(learning_rate=1e-3)
    svi = SVI(prior_only_tp_model, amortized_fn, optimizer, loss=Trace_ELBO())

    # --- 4) Initialize SVI state -----------------------
    rng = jax.random.PRNGKey(seed)
    init_rng, _ = jax.random.split(rng)
    state = svi.init(
        init_rng,
        data=data,
        prior_time=prior_time,
        T_limits=T_limits,
        prior_time_sd=prior_time_sd,
        prior_path=prior_path,
        num_paths=num_paths,
    )

    update_fn = jax.jit(lambda st: svi.update(
        st,
        data=data,
        prior_time=prior_time,
        T_limits=T_limits,
        prior_time_sd=prior_time_sd,
        prior_path=prior_path,
        num_paths=num_paths,
    ))

    def run_svi_warmup_local(st):
        def body(carry, _):
            st, _ = carry
            new_st, loss = update_fn(st)
            return (new_st, loss), loss
        (final_state, _), losses = jax.lax.scan(
            body, (st, 0.0), None, length=n_steps
        )
        return final_state, losses

    run_svi_warmup_jit = jax.jit(run_svi_warmup_local)

    # --- 5) Run JIT-compiled warm-up loop ---------------
    state, losses = run_svi_warmup_jit(state)

    # --- 6) Pull out only the NN parameters ------------
    all_params = svi.get_params(state)
    prefixes = (
        "V_shared",
        "c_shared",
        "V_t_c",
        "c_t_c",
        "V_out_t_c",
        "c_out_t_c",
        "V_det",
        "c_det",
        "V_out_det",
        "c_out_det",
        "V_det_l",
        "c_det_l",
        "V_out_det_l",
        "c_out_det_l",
        "V_pw",
        "c_pw",
        "V_out_pw",
        "c_out_pw",
    )
    net_params = {k: v for k, v in all_params.items() if k in prefixes}
    return net_params

# =============================================================================
# 4) Posterior‐mean extraction helpers (updated to call _network_forward)
# =============================================================================


def _select_net_params(params: dict) -> dict:
    """
    Pull out exactly those numpyro.param entries that belong to the amortized
    network (robust to different flag combinations).
    """
    prefixes = (
        "V_shared",
        "c_shared",
        "V_t_c",
        "c_t_c",
        "V_out_t_c",
        "c_out_t_c",
        "V_det",
        "c_det",
        "V_out_det",
        "c_out_det",
        "V_det_l",
        "c_det_l",
        "V_out_det_l",
        "c_out_det_l",
        "V_pw",
        "c_pw",
        "V_out_pw",
        "c_out_pw",
    )
    return {k: v for k, v in params.items() if k in prefixes}


def extract_global_posterior_mean(guide, svi_state, svi):
    """
    Extract means of *global* latent sites handled by AutoNormal (first sub‐guide).
    """
    auto = guide._guides[0]  # AutoNormal sits first
    params = svi.get_params(svi_state)
    return auto.median(params)  # uses the AutoNormal transform


def extract_local_posterior_mean(
    guide,
    svi_state,
    svi,
    data: jnp.ndarray,
    *,
    unknown_count: int = 0,
    unknown_idx=None,
    num_paths=None,
):
    """
    Extract means of *local* amortized sites:
      • 't_c'
      • 'detection_y_c' (if present)
      • 'detection_l_c' (if present)
      • 'path_weights_full' (if present)
    """
    params_all = svi.get_params(svi_state)
    net_params = _select_net_params(params_all)

    predict_y = all(k in net_params for k in ("V_det", "c_det"))
    predict_l = all(k in net_params for k in ("V_det_l", "c_det_l"))
    predict_pw = all(k in net_params for k in ("V_pw", "c_pw"))

    outputs = _network_forward(
        net_params,
        data,
        predict_y,
        predict_l,
        predict_pw,
    )

    idx = 0
    loc_t = outputs[idx]
    scale_t = outputs[idx + 1]
    idx += 2
    result = {"t_c": loc_t}  # Normal mean = loc

    if predict_y:
        loc_y = outputs[idx]
        scale_y = outputs[idx + 1]
        idx += 2
        result["detection_y_c"] = jnp.exp(loc_y)  # ExpTransform mean

    if predict_l:
        loc_l = outputs[idx]
        scale_l = outputs[idx + 1]
        idx += 2
        result["detection_l_c"] = jnp.exp(loc_l)

    if predict_pw and num_paths is not None:
        conc_pw = outputs[idx]  # (n_cells, num_paths)
        pw_mean = jax.nn.softmax(conc_pw, axis=-1)
        result["path_weights_full"] = pw_mean

    return result

def extract_local_means_full(
    guide,
    svi_state,
    svi,
    data_full: jnp.ndarray,
    *,
    batch_size: int = 8192,
    unknown_count: int = 0,
    unknown_idx: jnp.ndarray | None = None,
    num_paths: int | None = None,
):
    """
    Posterior means for *all* cells, processed in chunks so it works after
    mini‐batch training. Returns a dict mapping:
      • "t_c" → shape (n_cells,)
      • "detection_y_c" → (n_cells,) if present
      • "detection_l_c" → (n_cells,) if present
      • "path_weights_full" → (n_cells, num_paths) if present
    """
    n_cells = data_full.shape[0]
    params_all = svi.get_params(svi_state)
    net_p = {k: v for k, v in params_all.items() if k.startswith(("V_", "c_"))}

    has_y = all(k in net_p for k in ("V_det", "c_det"))
    has_l = all(k in net_p for k in ("V_det_l", "c_det_l"))
    has_pw = all(k in net_p for k in ("V_pw", "c_pw"))

    out = {}

    def _store(key, arr, slc):
        if key not in out:
            out[key] = jnp.empty((n_cells, *arr.shape[1:]), dtype=arr.dtype)
        out[key] = out[key].at[slc].set(arr)

    for start in range(0, n_cells, batch_size):
        stop = min(start + batch_size, n_cells)
        batch = data_full[start:stop]

        outputs = _network_forward(net_p, batch, has_y, has_l, has_pw)
        idx = 0

        # t_c
        loc_t = outputs[idx]
        idx += 1
        _store("t_c", loc_t, slice(start, stop))

        # detection_y_c
        if has_y:
            loc_y = outputs[idx]
            idx += 1
            _store("detection_y_c", jnp.exp(loc_y), slice(start, stop))

        # detection_l_c
        if has_l:
            loc_l = outputs[idx]
            idx += 1
            _store("detection_l_c", jnp.exp(loc_l), slice(start, stop))

        # path_weights_full
        if has_pw and num_paths is not None:
            conc_pw = outputs[idx]
            pw_mean = jax.nn.softmax(conc_pw, axis=-1)
            _store("path_weights_full", pw_mean, slice(start, stop))

    return out


# =============================================================================
# 5) AmortizedNormal helper class (uses the new amortized_guide)
# =============================================================================


class AmortizedNormal:
    def __init__(
        self,
        model,
        predict_detection_y_c: bool = True,
        predict_detection_l_c: bool = False,
        predict_path_weights: bool = False,
        init_net_params: dict = None,
        init_loc_fn=None,
    ):
        self.model = model
        self.predict_detection_l_c = predict_detection_l_c
        self.predict_detection_y_c = predict_detection_y_c
        self.predict_path_weights = predict_path_weights
        self.init_net_params = init_net_params

        # 1) Seed and block any latent sites that the amortized guide will handle
        guided = seed(model, rng_seed=0)
        hide = [
            "K_rh",
            "t_c",
            "detection_y_c",
            "T_c",
            "predictions",
            "mu",
            "d_cr",
            "mu_atac",
            "predictions_rearranged",
            "alpha_cg",
            "additive_term",
            "normalizing_term",
            "P_rh",
            "K_rh_vector",
            "path_weights",
            "sol_at_cells",
            "z_pw",
            "p_model",
            "sigma_tf",
            'p_sim_mean',
            'p_obs_mean',
            "p_sim",
        ]
        if predict_detection_l_c:
            hide.append("detection_l_c")
        blocked = block(guided, hide=hide)

        # 2) Build a guide list: first an AutoNormal over the blocked model,
        #    then the amortized guide (which now uses JIT).
        self.guide_list = AutoGuideList(model)
        self.guide_list.append(AutoNormal(blocked, init_loc_fn=init_loc_fn))
        self.guide_list.append(
            partial(
                amortized_guide,
                predict_detection_l_c=self.predict_detection_l_c,
                predict_detection_y_c=self.predict_detection_y_c,
                predict_path_weights = self.predict_path_weights,
                init_net_params=self.init_net_params,
            )
        )

    def __call__(self, *args, **kwargs):
        return self.guide_list(*args, **kwargs)

    def sample_posterior(self, *a, **k):
        return self.guide_list.sample_posterior(*a, **k)

    def median(self, *a, **k):
        return self.guide_list.median(*a, **k)

    def quantiles(self, *a, **k):
        return self.guide_list.quantiles(*a, **k)

    def get_posterior(self, *a, **k):
        return self.guide_list.get_posterior(*a, **k)

    def extract_global_means(self, svi_state, svi):
        return extract_global_posterior_mean(self.guide_list, svi_state, svi)

    def extract_local_means(self, svi_state, svi, data, **kw):
        return extract_local_posterior_mean(self.guide_list, svi_state, svi, data, **kw)

    def extract_all_means(
        self,
        svi_state,
        svi,
        data,
        *,
        batch_size: int = 1000,
        **kw,
    ):
        global_means = extract_global_posterior_mean(self.guide_list, svi_state, svi)
        local_means = extract_local_means_full(
            self.guide_list,
            svi_state,
            svi,
            data,
            batch_size=batch_size,
            **kw,
        )
        return global_means, local_means
