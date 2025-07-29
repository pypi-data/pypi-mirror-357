import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import warnings
from .math_utils import derivative_FDM
from .math_utils import safe_divide
from .general_utils import validate_inputs
from .dimless_utils import grashof, prandtl, rayleigh

def conduction_radial_steady_numerical(r, L, bc, k, gridpoints, solver="RK45", tol=1e-3):
    """
    Solve steady-state radial heat conduction in a cylinder numerically with possible temperature-dependent thermal conductivity.

    Parameters
    ----------
    r : tuple of floats
        Radial domain as (r0, R), inner and outer radii.
    L : float
        Axial length of the cylinder (used to calculate cylindrical surface area).
    bc : tuple
        Boundary conditions at r0 as (T0, T1_input, Q):
        - T0: Temperature at inner radius r0.
        - T1_input: Temperature gradient dT/dr at r0 (can be None if unknown).
        - Q: Heat flux at r0 (can be None if unknown).
        Exactly one of T1_input or Q must be provided, or both must be consistent.
    k : float or array-like
        Thermal conductivity. Can be:
        - A constant float or int.
        - An array-like [[T0, k0], [T1, k1], ...] specifying temperature-dependent conductivity,
          which is interpolated internally.
    gridpoints : int
        Number of points in radial mesh for numerical solution.
    solver : str, optional
        ODE solver method for scipy.integrate.solve_ivp (default "RK45").
    tol : float, optional
        Relative tolerance for heat flux conservation check (default 1e-3).

    Returns
    -------
    dict
        Dictionary containing:
        - 'r': radial positions array,
        - 'T': temperature distribution array,
        - 'dT/dr': temperature gradient array,
        - 'Q_error': difference between heat flux at inner and outer boundaries (flux conservation error).

    Description
    -----------
    Solves the nonlinear ODE system describing steady radial heat conduction in a cylinder:

        d/dr [k(T) * A(r) * dT/dr] = 0,

    where A(r) = 2 * pi * r * L is the cylindrical surface area.

    The equation expands to:

        d²T/dr² + (1/k) * (dk/dT) * (dT/dr)² + (1/r) * dT/dr = 0,

    with boundary conditions at the inner radius r0:

        T(r0) = T0,
        and either specified temperature gradient dT/dr(r0) = T1_input
        or specified heat flux Q = -k * A(r0) * dT/dr(r0).

    The function supports temperature-dependent thermal conductivity via interpolation,
    and integrates the ODE system numerically using solve_ivp.

    It verifies heat flux conservation between inner and outer boundaries and warns
    if the flux discrepancy exceeds the specified tolerance.

    Symmetry condition at r=0 is handled by setting the second derivative of temperature to zero.

    Warnings are issued if the ODE solver fails or if boundary fluxes are inconsistent.

    This method is suitable for modeling steady heat conduction in cylindrical coordinates
    with radial dependence and non-constant thermal conductivity.
    """

    r0, R = r
    T0, T1_input, Q = bc

    # Detect constant or interpolated k(T)
    if isinstance(k, (float, int)):
        k_const = float(k)
        def k_interp(T): return k_const
        def dk_interp(T): return 0.0
    else:
        k = np.asarray(k)
        k_interp = interp1d(k[:, 0], k[:, 1], kind='cubic', fill_value="extrapolate")
        T_fine = np.linspace(k[:, 0].min(), k[:, 0].max(), 1000)
        dk_dT_fine = np.gradient(k_interp(T_fine), T_fine)
        dk_interp = interp1d(T_fine, dk_dT_fine, kind='linear', fill_value="extrapolate")

    def area(r): return 2 * np.pi * r * L

    # Compute initial dT/dr with corrected minus sign
    if T1_input is None and Q is not None:
        A0 = area(r0)
        k0 = k_interp(T0)
        T1 = - Q / (k0 * A0)  # <- corrected minus sign
    elif Q is None and T1_input is not None:
        T1 = T1_input
    elif Q is not None and T1_input is not None:
        A0 = area(r0)
        k0 = k_interp(T0)
        expected_T1 = - Q / (k0 * A0)  # corrected minus sign
        if not np.isclose(T1_input, expected_T1, rtol=1e-4):
            raise ValueError("Inconsistent values: T'0 and Q do not satisfy dT/dr = -Q / (k(T) * A(r))")
        T1 = T1_input
    else:
        raise ValueError("Must provide either dT/dr or Q in bc")

    def system(r, y):
        T, dTdr = y
        k_val = k_interp(T)
        dk_dT_val = dk_interp(T)
        if r == 0:
            d2Tdr2 = 0  # symmetry condition
        else:
            d2Tdr2 = - (1 / k_val) * dk_dT_val * dTdr**2 - (1 / r) * dTdr
        return [dTdr, d2Tdr2]

    r_span = (r0, R)
    r_eval = np.linspace(r0, R, gridpoints)
    y0 = [T0, T1]

    sol = solve_ivp(system, r_span, y0, method=solver, t_eval=r_eval)

    if not sol.success:
        warnings.warn("ODE solver failed: " + sol.message)

    T_vals = sol.y[0]
    dTdr_vals = sol.y[1]
    r_vals = sol.t

    # Compute Q at r0 and r=R from numerical solution
    A_r0 = area(r0)
    k_r0 = k_interp(T_vals[0])
    Q_r0_calc = - k_r0 * A_r0 * dTdr_vals[0]

    A_R = area(R)
    k_R = k_interp(T_vals[-1])
    Q_R_calc = - k_R * A_R * dTdr_vals[-1]
    Q_error = Q_r0_calc - Q_R_calc

    # Check flux consistency
    if np.abs(Q_error) > tol * np.abs(Q_r0_calc):
        warnings.warn(f"Flux inconsistency: Q(r0)={Q_r0_calc:.4f}, Q(R)={Q_R_calc:.4f}")


    return {"r":        r_vals, 
            "T":        T_vals, 
            "dT/dr":    dTdr_vals,
            "Q_error":  Q_error}

def conduction_radial_analytical(
    radii,
    T_bounds,
    k_data_list,
    N_points_per_layer,
    L=1.0
):
    """
    Analytical solution for radial conduction in a multi-layered cylinder.

    Returns
    -------
    sol_guess : dict
        Dictionary with 'r', 'T', 'Q_dot', 'q_dot', and 'dT_dr'
    """
    n = len(k_data_list)
    T1, Tn1 = T_bounds

    # Compute average temperature per layer (linear interpolation in log space)
    ln_r = np.log(radii)
    T_interface = np.interp(ln_r, [ln_r[0], ln_r[-1]], [T1, Tn1])

    k_avgs = []
    for i in range(n):
        T_avg = 0.5 * (T_interface[i] + T_interface[i + 1])
        k_data = k_data_list[i]

        if np.isscalar(k_data):
            k_avg = float(k_data)
        else:
            T_vals, k_vals = k_data[:, 0], k_data[:, 1]
            k_interp = interp1d(T_vals, k_vals, kind='linear', fill_value='extrapolate')
            k_avg = float(k_interp(T_avg))

        k_avgs.append(k_avg)

    # Compute total thermal resistance and heat flow Q_dot
    resistances = [np.log(radii[i + 1] / radii[i]) / (2 * np.pi * L * k_avgs[i]) for i in range(n)]
    R_tot = sum(resistances)
    Q_dot = (T1 - Tn1) / R_tot

    # Build temperature profile T(r)
    r_all = []
    T_all = []
    k_all = []

    T_start = T1
    for i in range(n):
        r0, r1 = radii[i], radii[i + 1]
        k = k_avgs[i]
        N = N_points_per_layer[i]

        r_layer = np.linspace(r0, r1, N) if i == 0 else np.linspace(r0, r1, N)[1:]
        T_layer = T_start - (Q_dot / (2 * np.pi * L * k)) * np.log(r_layer / r0)
        T_start = T_layer[-1]

        r_all.append(r_layer)
        T_all.append(T_layer)
        k_all.append(np.full_like(r_layer, k))

    r_all = np.concatenate(r_all)
    T_all = np.concatenate(T_all)
    k_all = np.concatenate(k_all)

    def compute_gradients_per_layer_forward_diff(r_all, T_all, k_all, radii, N_points_per_layer):
        dT_dr = np.empty_like(T_all)
        q_dot = np.empty_like(T_all)
        
        start_idx = 0
        n_layers = len(N_points_per_layer)
        
        for i in range(n_layers):
            if i == 0:
                N = N_points_per_layer[i]
            else:
                N = N_points_per_layer[i] - 1  # skip overlapping first point
            
            end_idx = start_idx + N
            
            r_layer = r_all[start_idx:end_idx]
            T_layer = T_all[start_idx:end_idx]
            k_layer = k_all[start_idx:end_idx]
            
            # Forward difference for gradient
            dT_dr_layer = (T_layer[1:] - T_layer[:-1]) / (r_layer[1:] - r_layer[:-1])
            
            dT_dr_layer_full = np.empty(N)
            dT_dr_layer_full[:-1] = dT_dr_layer
            dT_dr_layer_full[-1] = dT_dr_layer[-1]
            
            dT_dr[start_idx:end_idx] = dT_dr_layer_full
            q_dot[start_idx:end_idx] = -k_layer * dT_dr_layer_full
            
            start_idx = end_idx
        
        return dT_dr, q_dot

    dT_dr, q_dot = compute_gradients_per_layer_forward_diff(r_all, T_all, k_all, radii, N_points_per_layer)

    sol_guess = {
        'r': r_all,
        'T': T_all,
        'Q_dot': Q_dot,
        'q_dot': q_dot,
        'dT_dr': dT_dr
    }
    return sol_guess

def Nusselt_correlations_free(mode, *, Ra=None, Gr=None, Pr = None, d=None, L=None):
    """
    Computes the Nusselt number (Nu) using empirical correlations for natural convection
    in several geometries, based on the selected mode.

    Parameters:
    ----------
    mode : str
        The correlation mode. Supported options are:
        
        - "Annulus_vertical_1": 
            Empirical correlation for natural convection in vertical annuli.
            Equation:
                Nu = 0.761 * (Ra * d / L)^0.283
            Valid for:
                10 < (Ra * d / L) < 1e3
            Source:
                Kubair & Simha (Exact citation/details TBD).
        
        - "Annulus_vertical_2":
            Alternative empirical correlation for vertical annuli.
            Equation:
                Nu = 0.398 * (Ra * d / L)^0.284
            Valid for:
                10 < (Ra * d / L) < 1e5
            Source:
                Kubair & Simha (Exact citation/details TBD).

    Keyword Arguments:
    ------------------
    Ra : float
        Rayleigh number (dimensionless), representing buoyancy-driven flow.
    d : float
        Gap between the inner and outer cylinders (in meters) d = r_o - r_i.
    L : float
        Characteristic length or height of the annular region (in meters).

    Returns:
    -------
    Nu : float
        Computed Nusselt number based on the selected mode and input parameters.

    Raises:
    ------
    ValueError:
        - If any of Ra, d, or L is not provided.
        - If the provided mode is not supported.
    
    Warnings:
    --------
    Issues a warning if the computed Ra*d/L value is outside the valid range for
    the selected correlation mode.

    Notes:
    -----
    The Nusselt number quantifies convective heat transfer relative to conduction.
    These correlations are based on experimental/numerical results and must be applied
    only within their validity range for physically meaningful results.
    """


    if mode == "Annulus_vertical_1":
        if Ra is None or d is None or L is None:
            raise ValueError("Ra, d, and L must all be provided.")
        Ra, d, L = validate_inputs(Ra, d, L, check_broadcast=True)
        ratio = Ra * safe_divide(d, L)
        if not (10 < ratio < 1e3):
            warnings.warn("Ra*d/L is out of the valid range (10 < Ra*d/L < 1e3) for Annulus_vertical_1.")
        Nu = 0.761 * (ratio) ** 0.283
        return Nu

    elif mode == "Annulus_vertical_2":
        if Ra is None or d is None or L is None:
            raise ValueError("Ra, d, and L must all be provided.")
        Ra, d, L = validate_inputs(Ra, d, L, check_broadcast=True)
        ratio = Ra * safe_divide(d, L)
        if not (10 < ratio < 1e5):
            warnings.warn("Ra*d/L is out of the valid range (10 < Ra*d/L < 1e5) for Annulus_vertical_2.")
        Nu = 0.398 * (ratio) ** 0.284
        return Nu

    else:
        raise ValueError(f"Unknown mode '{mode}'. Please choose a supported mode.")

def convection_analytical(
    T_a,
    A,
    d,
    L,
    T_eval,
    beta,
    mu,
    rho,
    cp,
    k,
    nusselt_func,
    *,
    mode="solve_T",
    Q=None,
    T_b=None,
    g=9.81,
    max_iter=50,
    tol=1e-4,
):
    """
    Solves for T_b or Q in a free convection heat transfer problem.

    Parameters
    ----------
    T_a : float or np.ndarray
        Ambient temperature [K]
    A : float
        Surface area [m^2]
    d : float
        Characteristic length [m]
    L : float
        Vertical length [m]
    T_eval : array-like
        Temperature values corresponding to the property vectors
    beta, mu, rho, cp, k : array-like
        Thermophysical property vectors
    nusselt_func : callable
        Function to compute Nu, must accept Gr, Pr, Ra, d, L
    mode : str
        'solve_T' to compute T_b (requires Q),
        'solve_Q' to compute Q (requires T_b)
    Q : float or np.ndarray, optional
        Heat transfer rate [W] (required for mode='solve_T')
    T_b : float or np.ndarray, optional
        Surface temperature [K] (required for mode='solve_Q')
    g : float, optional
        Gravitational acceleration [m/s^2] (default is 9.81)
    max_iter : int, optional
        Maximum number of iterations (only used in mode='solve_T')
    tol : float, optional
        Convergence tolerance (only used in mode='solve_T')

    Returns
    -------
    dict with results including:
    - T_b, T_avg, h, Nu, Q (if solved), Ra, Gr, Pr
    """
    
    # Prepare interpolation functions
    interp = lambda arr: interp1d(T_eval, arr, kind='linear', fill_value='extrapolate')
    interp_beta = interp(beta)
    interp_mu   = interp(mu)
    interp_rho  = interp(rho)
    interp_cp   = interp(cp)
    interp_k    = interp(k)

    if mode == "solve_T":
        if Q is None:
            raise ValueError("Q must be provided for mode='solve_T'")

        # Initial guess
        h = 10
        T_b = T_a - Q / (h * A)

        for _ in range(max_iter):
            T_avg = 0.5 * (T_a + T_b)

            # Interpolate properties
            beta_i = interp_beta(T_avg)
            mu_i   = interp_mu(T_avg)
            rho_i  = interp_rho(T_avg)
            cp_i   = interp_cp(T_avg)
            k_i    = interp_k(T_avg)

            nu = mu_i / rho_i
            alpha = k_i / (rho_i * cp_i)
            delta_T = np.abs(T_b - T_a)

            Gr = grashof(g, d, nu, beta=beta_i, Ts=T_a, T_inf=T_b, mode="heat")
            Pr = prandtl(cp_i, mu_i, k_i,)
            Ra = rayleigh(Gr=Gr,Pr=Pr,mode="grpr")

            Nu = nusselt_func(Gr=Gr, Pr=Pr, Ra=Ra, d=d, L=L)
            h_new = Nu * k_i / d
            T_b_new = T_a - Q / (h_new * A)

            if np.all(np.abs(T_b_new - T_b) < tol):
                break

            T_b = T_b_new
            h = h_new
        else:
            warnings.warn("convection_analytical: Maximum iterations reached without convergence.")

        T_avg = 0.5 * (T_a + T_b)
        Q_solved = Q  # Preserve original input

    elif mode == "solve_Q":
        if T_b is None:
            raise ValueError("T_b must be provided for mode='solve_Q'")

        T_avg = 0.5 * (T_a + T_b)

        # Interpolate properties
        beta_i = interp_beta(T_avg)
        mu_i   = interp_mu(T_avg)
        rho_i  = interp_rho(T_avg)
        cp_i   = interp_cp(T_avg)
        k_i    = interp_k(T_avg)

        nu = mu_i / rho_i
        alpha = k_i / (rho_i * cp_i)
        delta_T = np.abs(T_b - T_a)

        Gr = grashof(g, d, nu, beta=beta_i, Ts=T_a, T_inf=T_b, mode="heat")
        Pr = prandtl(cp_i, mu_i, k_i,)
        Ra = rayleigh(Gr=Gr,Pr=Pr,mode="grpr")

        Nu = nusselt_func(Gr=Gr, Pr=Pr, Ra=Ra, d=d, L=L)
        h = Nu * k_i / d
        Q_solved = h * A * (T_a - T_b)

    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'solve_T' or 'solve_Q'.")
 
    return (
        Q_solved,  # Q
        T_a,       # T_a
        T_b,       # T_b
        T_avg,     # T_avg
        h,         # h
        Nu,        # Nu
        Ra,        # Ra
        Gr,        # Gr
        Pr         # Pr
    )


if __name__ == "__main__":
    import numpy as np
    from functools import partial
    from eppink_utilities.heattransfer_utils import Nusselt_correlations_free

    # Sample temperature range for property interpolation [K]
    T_eval = np.linspace(300, 350, 5)

    # Sample property vectors corresponding to T_eval
    beta = 1 / T_eval
    mu = np.linspace(1.8e-5, 2.1e-5, len(T_eval))
    rho = np.linspace(1.2, 1.1, len(T_eval))
    cp = np.linspace(1000, 1020, len(T_eval))
    k = np.linspace(0.026, 0.030, len(T_eval))

    # Geometric and input conditions
    A = 0.2     # m²
    d = 0.01    # m
    L = 0.1     # m
    T_a = 350   # K
    Q = 20      # W
    T_b = 328.53   # K

    # Bind the Nusselt function to a specific correlation
    nusselt_func = partial(Nusselt_correlations_free, mode="Annulus_vertical_2")

    print("=== Mode: solve_T ===")
    out_T = convection_analytical(
        T_a=T_a,
        Q=Q,
        A=A,
        d=d,
        L=L,
        T_eval=T_eval,
        beta=beta,
        mu=mu,
        rho=rho,
        cp=cp,
        k=k,
        nusselt_func=nusselt_func,
        mode="solve_T"
    )

    print(f"Q      = {out_T[0]:.2f} W")
    print(f"T_a    = {out_T[1]:.2f} K")
    print(f"T_b    = {out_T[2]:.2f} K")
    print(f"T_avg  = {out_T[3]:.2f} K")
    print(f"h      = {out_T[4]:.4f} W/m²K")
    print(f"Nu     = {out_T[5]:.4f}")
    print(f"Ra     = {out_T[6]:.2e}")
    print(f"Gr     = {out_T[7]:.2e}")
    print(f"Pr     = {out_T[8]:.4f}")

    print("\n=== Mode: solve_Q ===")
    out_Q = convection_analytical(
        T_a=T_a,
        T_b=T_b,
        A=A,
        d=d,
        L=L,
        T_eval=T_eval,
        beta=beta,
        mu=mu,
        rho=rho,
        cp=cp,
        k=k,
        nusselt_func=nusselt_func,
        mode="solve_Q"
    )

    print(f"Q      = {out_Q[0]:.2f} W")
    print(f"T_a    = {out_Q[1]:.2f} K")
    print(f"T_b    = {out_Q[2]:.2f} K")
    print(f"T_avg  = {out_Q[3]:.2f} K")
    print(f"h      = {out_Q[4]:.4f} W/m²K")
    print(f"Nu     = {out_Q[5]:.4f}")
    print(f"Ra     = {out_Q[6]:.2e}")
    print(f"Gr     = {out_Q[7]:.2e}")
    print(f"Pr     = {out_Q[8]:.4f}")
