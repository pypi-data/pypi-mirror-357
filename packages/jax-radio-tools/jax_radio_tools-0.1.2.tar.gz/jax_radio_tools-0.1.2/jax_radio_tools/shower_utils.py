import os
from typing import Union, Callable
import jax
import jax.numpy as jnp
from scipy import constants

from . import units, trace_utils

prmpar_map = {14: "p", 5626: "Fe"}


def get_arrival_times(
    traces: jax.typing.ArrayLike,
    trace_times: jax.typing.ArrayLike,
    sample_axis: int = 2,
) -> jax.typing.ArrayLike:
    """
    Get the arrival times from the trace for each antenna.

    To determine this, we apply a Hilbert envelope and get the maximum position.

    Parameter
    ---------
    traces : jax.typing.ArrayLike
        the traces to take the Hilbert envelope of. Shape must be in
        (Npol, Nant, Nsamples)
    trace_times : jax.typing.ArrayLike
        the time array of the traces. Must be in shape (Nant, Nsamples)
    sample_axis : int, default=2
        the axis where the samples are located
    """
    traces_hilbert = trace_utils.hilbert(traces, sample_axis=sample_axis)

    # summing over polarisations
    hilbert_envelope = jnp.sqrt(
        jnp.linalg.norm(traces, axis=0) ** 2
        + jnp.linalg.norm(traces_hilbert, axis=0) ** 2
    )
    # finding the indicies of the pulse maximum for each antenna position
    arrtime_idces = jnp.argmax(jnp.abs(hilbert_envelope), axis=1)

    arr_times_ant = []
    for iant, antmax_idx in enumerate(arrtime_idces):
        arr_times_ant.append(trace_times[iant, antmax_idx])

    return jnp.array(arr_times_ant)


def gaisser_hillas_function_coreas(
    X: jax.typing.ArrayLike,
    nmax: float,
    x0: float,
    xmax: float,
    p0: float,
    p1: float,
    p2: float,
) -> jax.Array:
    """Return a Gaisser-Hillas function."""
    lmbda = p0 + p1 * X + p2 * X**2  # interaction length, parameterised by polynomial
    return (
        nmax
        * ((X - x0) / (xmax - x0)) ** ((xmax - x0) / lmbda)
        * jnp.exp((xmax - X) / lmbda)
    )


def gaisser_hillas_function(
    x: jax.typing.ArrayLike, nmax: float, xmax: float, x0: float, lmbda: float
) -> jax.Array:
    """Return a Gaisser-Hillas function in standard formalism."""
    power = (xmax - x0) / lmbda

    result = jnp.nan_to_num(jnp.where((x - x0) >= 0, (
        nmax
        * ((x - x0) / (xmax - x0)) ** power
        * jnp.exp((xmax - x) / lmbda)
    ), 0.0))
    return result


def gaisser_hillas_function_error(
    x: jax.typing.ArrayLike,
    nmax_tup: tuple,
    xmax_tup: tuple,
    x0_tup: tuple,
    lmbda_tup: tuple,
) -> jax.Array:
    """Return the error of the Gaisser Hillas function, using mean and std of GH parameters."""
    nmax, nmax_err = nmax_tup
    xmax, xmax_err = xmax_tup
    x0, x0_err = x0_tup
    lmbda, lmbda_err = lmbda_tup

    gh = gaisser_hillas_function(x, nmax, xmax, x0, lmbda)
    ln_term = jnp.log(((x - x0) / (xmax - x0)))

    x0_err_term = ln_term * x0 - x * ln_term - (xmax - x) / (lmbda * (x0 - x))
    lmbda_err_term = ((xmax - x0) - ln_term + (xmax - x)) / (lmbda**2)

    return jnp.sqrt(
        (gh / nmax * nmax_err) ** 2
        + (gh * ln_term / lmbda * xmax_err) ** 2
        + (gh * x0_err_term * x0_err) ** 2
        + (gh * lmbda_err_term * lmbda_err) ** 2
    )


def gaisser_hillas_function_LR(
    x: jax.typing.ArrayLike, nmax: float, xmax: float, L: float, R: float
) -> jax.Array:
    """Return a Gaisser-Hillas function in L-R formalism"""
    return nmax * jnp.nan_to_num(jnp.exp((xmax - x) / (L * R)) * (1 + R * (x - xmax) / L) ** (R**-2))


def convert_GH_to_LR(xmax, x0, lmbda) -> tuple[float, float]:
    """
    Convert the standard Gaisser-Hillas parameters to those in the LR formalism.

    Parameter:
    ---------
    xmax : float
        the atmospheric depth at shower maximum
    x0 : float
        the first interaction point in the shower
    lmbda : float
        the interaction length
    Return:
    ------
    L, R : tuple[float, float]
        the width and asymmetry parameter of the profile
    """
    x0p = xmax - x0
    return (jnp.sqrt(jnp.abs(x0p * lmbda)), jnp.sqrt(jnp.abs(lmbda / x0p)))


def get_fluences(
    efield_traces: jax.typing.ArrayLike,
    delta_t: float,
    pol_axis: int = 0,
    sample_axis: int = 2,
) -> jax.Array:
    """
    Return the fluences from electric field traces.

    Parameters
    ----------
    efield_traces : jax.typing.ArrayLike
        the electric field traces
    delta_t : float
        the timing resolution in ns
    pol_axis : int, default=2
        the axis in which the polarisations are located.
    """
    eps_0 = constants.epsilon_0 * units.farad / units.m
    c_vacuum = constants.c * units.m / units.s
    return (
        eps_0
        * c_vacuum
        * jnp.sum(
            delta_t * jnp.linalg.norm(efield_traces, axis=pol_axis),
            axis=sample_axis - 1,
        )
    )


def get_cross_correlations(
    efield_traces_1: jax.typing.ArrayLike,
    efield_traces_2: jax.typing.ArrayLike,
    pol_axis: int = 0,
    sample_axis: int = 2,
) -> jax.Array:
    """
    Return the cross correlations of two electric field traces.

    Parameters
    ----------
    efield_traces_1 : jax.typing.ArrayLike
        the first electric field traces
    efield_traces_2 : jax.typing.ArrayLike
        the second electric field traces
    pol_axis : int, default=0
        the axis in which the polarisations are located.
    sample_axis : int, default=2
        the axis in which the samples are located.
    """
    total_efield_trace_1 = jnp.linalg.norm(efield_traces_1, axis=pol_axis)
    total_efield_trace_2 = jnp.linalg.norm(efield_traces_2, axis=pol_axis)
    return jnp.sum(
        (total_efield_trace_1 * total_efield_trace_2), axis=sample_axis-1
    ) / jnp.sqrt(
        jnp.sum(total_efield_trace_1**2, axis=sample_axis-1)
        * jnp.sum(total_efield_trace_2**2, axis=sample_axis-1)
    )
