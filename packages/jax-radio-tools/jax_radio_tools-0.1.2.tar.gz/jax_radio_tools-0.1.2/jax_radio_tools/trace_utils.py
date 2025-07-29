"""Utility functions for traces."""

import jax
import jax.numpy as jnp
from typing_extensions import Union

from . import units
from fractions import Fraction


def filter_trace(
    trace: jax.typing.ArrayLike,
    trace_sampling: float,
    f_min: float,
    f_max: float,
    sample_axis: int = 0,
) -> jax.Array:
    """
    Filter the trace within the frequency domain of interest.

    Parameter:
    ----------
    trace : jax.typing.ArrayLike
        The trace to filter. Shape is SAMPLES x ...
    trace_sampling : float
        The sampling rate of the traces
    f_min : float
        The minimum frequency in which to filter, in MHz
    f_max : float
        The maximum frequency in which to filter, in MHz
    sample_axis : int, default=0
        The axis in which the filtering takes place. Default is 0, i.e. the first axis

    Return:
    ------
    filtered_trace : jax.Array
        The filtered trace within the requested frequency domain
    """
    # Assuming `trace_sampling` has the correct internal unit, freq is already in the internal unit system
    freq = jnp.fft.rfftfreq(trace.shape[sample_axis], d=trace_sampling)
    freq_range = jnp.logical_and(freq > f_min, freq < f_max)

    # Find the median maximum sample number of the traces
    max_indces = jnp.median(jnp.argmax(trace, axis=sample_axis))
    to_roll = jnp.int32(trace.shape[sample_axis] // 2 - max_indces)

    # Roll all traces such that max is in the middle
    roll_pulse = jnp.roll(trace, to_roll, axis=sample_axis)

    # FFT, filter, IFFT
    spectrum = jnp.fft.rfft(roll_pulse, axis=sample_axis)
    spectrum = jnp.apply_along_axis(
        lambda ax: ax * jnp.int32(freq_range), sample_axis, spectrum
    )
    filtered = jnp.fft.irfft(spectrum, axis=sample_axis)

    return jnp.roll(filtered, -to_roll, axis=sample_axis)  # back to original position


def hilbert(
    trace: jax.typing.ArrayLike,
    sample_axis: int = 0,
) -> jax.Array:
    """
    Hilbert transform for a given trace.

    Parameter:
    ----------
    trace : jax.typing.ArrayLike
        The trace to get the hilbert envelope of.
    sample_axis : int, default=0
        The axis in which the filtering takes place. Default is 0, i.e. the first axis
    """
    trace = jnp.asarray(trace)
    if jnp.iscomplexobj(trace):
        raise ValueError("x must be real.")
    N = trace.shape[sample_axis]

    Xf = jnp.fft.fft(trace, N, axis=sample_axis)
    h = jnp.zeros(N, dtype=Xf.dtype)
    if N % 2 == 0:
        h = h.at[0].set(1)
        h = h.at[N // 2].set(1)
        h = h.at[1 : N // 2].set(2)
    else:
        h = h.at[0].set(1)
        h = h.at[1 : (N + 1) // 2].set(2)

    if trace.ndim > 1:
        ind = [jnp.newaxis] * trace.ndim
        ind[sample_axis] = slice(None)
        h = h[tuple(ind)]
    hilbert_trace = jnp.fft.ifft(Xf * h, axis=sample_axis)
    return hilbert_trace


def resample_trace(
    trace: jax.typing.ArrayLike,
    dt_resample: float = 2 * units.ns,
    dt_sample: float = 0.1 * units.ns,
    times: Union[jax.typing.ArrayLike, None] = None,
    sample_axis: int = 0,
    sample_time_axis: int = 0,
) -> jax.Array:
    """
    Resample the trace to the given sampling frequency.

    This is jaxified from scipy.signal.resample, combined with the
    wrapper call from NuRadioReco.
    We also remove the functionality for complex signals since only
    real signal are applicable in our scenario.

    Parameter:
    ----------
    trace : jax.typing.ArrayLike
        the trace to downsample
    dt_resample : float, default=2 ns
        the time resolution to downsample to.
        Default is 2 ns, which is slightly better than the LOFAR resolution
    dt_sample : float, default=0.1 ns
        the original time resolution. Required for calculating the
        decimation factor
    times : Union[jax.typing.ArrayLike, None], default=None
        the times describing the trace. If provided, the
        new times for the downsampled traces will be returned.
    sample_axis : int, default=0
        the axis where the trace is to downsample

    Return:
    ------
    y : jax.Array
        the downsampled signal
    new_t : jax.Array
        the new time array for the downsampled signal
    """
    trace = jnp.asarray(trace)
    n_samples = trace.shape[sample_axis]
    resampling_factor = dt_resample / dt_sample
    n_resamples = int(n_samples / resampling_factor)  # divide
    trace_fft = jnp.fft.rfft(trace, axis=sample_axis)

    # print(f"Downsampling from {dt_sample:.2f} ns to {dt_resample :.2f} ns")
    # print(f"Corresponding to reduction of {n_samples:d} to {n_resamples:d} number of samples.")

    # Placeholder array for output spectrum
    newshape = list(trace_fft.shape)
    newshape[sample_axis] = n_resamples // 2 + 1
    Y = jnp.zeros(newshape, trace_fft.dtype)

    # Copy positive frequency components (and Nyquist, if present)
    N = min(n_resamples, n_samples)
    nyq = N // 2 + 1  # Slice index that includes Nyquist if present
    sl = [slice(None)] * trace.ndim
    sl[sample_axis] = slice(0, nyq)
    Y = Y.at[tuple(sl)].set(trace_fft[tuple(sl)])

    # Split/join Nyquist component(s) if present
    # So far we have set Y[+N/2]=X[+N/2]
    if N % 2 == 0:
        if n_resamples < n_samples:  # downsampling
            sl[sample_axis] = slice(N // 2, N // 2 + 1)
            Y = Y.at[tuple(sl)].set(Y[tuple(sl)] * 2.0)
        elif n_samples < n_resamples:  # upsampling
            # select the component at frequency +N/2 and halve it
            sl[sample_axis] = slice(N // 2, N // 2 + 1)
            Y = Y.at[tuple(sl)].set(Y[tuple(sl)] * 0.5)

    # Inverse transform
    y = jnp.fft.irfft(Y, n_resamples, axis=sample_axis)
    y *= float(n_resamples) / float(n_samples)

    if times is None:
        return y
    else:
        # get array for axes
        axes = list(range(len(times.shape)))

        # define 1D array by ratio of n_sampels vs n_resamples to get
        # the most precise dt_resample
        new_t_resampled = (
            jnp.arange(0, n_resamples) * dt_sample * n_samples / n_resamples
        )

        # pop axis in which we want to expand dimensions of 1D array
        axes.pop(sample_time_axis)

        # expand dimensions and shift by first value of array, i.e. the minimum value
        # (assumes monochromatically increasing time bins)
        new_ts = jnp.expand_dims(new_t_resampled, axis=axes) + jnp.min(
            times, axis=sample_time_axis, keepdims=True
        )
        return y, new_ts


def center_trace(
    trace: jax.typing.ArrayLike,
    sample_axis: int = 2,
) -> jax.Array:
    """
    Place the pulse at the center.

    Parameter:
    ----------
    trace : jax.typing.ArrayLike
        the trace to center
    sample_axis : int, defualt=2
        the axis in which the samples are. default is 2
    """
    # Find the median maximum sample number of the traces
    max_indces = jnp.median(jnp.argmax(trace, axis=sample_axis))
    to_roll = jnp.int32(trace.shape[sample_axis] / 2 - max_indces)

    # Roll all traces such that max is in the middle
    traces_centered = jnp.roll(trace, to_roll, axis=sample_axis)

    return traces_centered


def shift_trace_to_center(
    trace: jax.typing.ArrayLike,
    sample_axis: int = 2,
) -> jax.Array:
    """
    Shifts the trace such that it is in the center of the time signal.

    This is a different approach to centering the trace based on the pulse,
    which ignores timing information. Here we move the pulse to the
    middle of the time axes, which is suffcient as the number of samples
    is constant per SlicedShower object.

    Doing so, we preserve the timing information while still being able to
    apply the signal windowing.

    Parameter:
    -----------
    trace : jax.typing.ArrayLike
        the trace to center
    sample_axis : int, defualt=2
        the axis in which the samples are. default is 2
    """
    # find where the middle of the time axis is
    trace_length = trace.shape[sample_axis]
    mid_idx = trace_length // 2  # this is the middle

    traces_centered = jnp.roll(trace, mid_idx, axis=sample_axis)

    return traces_centered


def truncate_to_signal_window(
    trace: jax.typing.ArrayLike,
    times: jax.typing.ArrayLike,
    t_window: float = 250 * units.ns,
    trace_sampling: float = 0.1 * units.ns,
    sample_axis: int = 2,
    ant_axis: int = 1,
    sample_time_axis: int = 1,
) -> jax.typing.ArrayLike:
    """
    Truncate the traces such that we only get the signal window.

    To do this, we simply truncate from the maximum of the absolute value
    of the trace n_window // 2 on each side over all antennas.

    We also take care of the time axes here.

    Note that the signal should be centered in order for this to work.

    Parameter:
    ----------
    trace : jax.typing.ArrayLike
        the trace to truncate
    times : jax.typing.ArrayLike
        the times of the traces
    t_window : float, default=250 ns
        the signal window to truncate in ns
    trace_sampling : float, default=0.1 ns
        the sampling rate of the traces in nanoseconds
    sample_axis : int, defualt=2
        the axis in which the samples are. default is 2
    ant_axis : int, default=1
        the axis in which the antennas are. default is 1
    sample_time_axis : int, default=1
        the axis in which the time is defined. default is 1
    """
    # Find the median maximum sample number of the traces over all antennas as well
    # NOTE: we take the first antenna since its closest to the shower core
    # in principle we should read this from the arrival time information
    # TODO: improve this
    max_indces = jnp.median(
        jnp.argmax(
            jnp.expand_dims(
                jnp.take(jnp.abs(trace), indices=0, axis=ant_axis), axis=ant_axis
            ),  # need to expand dimension to preserve shape
            axis=sample_axis,
        )
    )

    # ensure that the window is even
    assert t_window % 2 == 0, "The window size must be even."

    # calcualte the size of the time window in terms of samples
    # this is the total size of the window / sampling size
    # we then ceil it and multiply by 2 to ensure that we have even
    n_window = int(jnp.ceil(t_window // trace_sampling / 2) * 2)
    print(f"Truncating to a window of {n_window} samples.")
    n_samples_per_side = n_window // 2 # halve it to get it per side

    # then the indices corresponding to the window is just the maximum - nsamples per side
    # shift by 1 in the end to include the very right side
    window_indces = jnp.arange(
        max_indces - n_samples_per_side,
        max_indces + n_samples_per_side + 1,
        1,
        dtype=int,
    )

    # finally use the mask and apply it to the slice traces
    trace_truncated = jnp.take(
        trace, indices=window_indces, axis=sample_axis, mode="clip"
    )

    # do the same for the time axies
    time_truncated = jnp.take(
        times, indices=window_indces, axis=sample_time_axis, mode="clip"
    )

    return trace_truncated, time_truncated


def zero_pad_traces(
    traces: jax.typing.ArrayLike,
    times: jax.typing.ArrayLike,
    trace_sampling: float = 0.1 * units.ns,
    sample_axis: int = 2,
    sample_time_axis: int = 1,
    ant_time_axis: int = 0,
) -> jax.Array:
    """
    Apply zero padding on each end and filter.

    This is done for a cleaner filtering.

    Parameter:
    ----------
    trace : jax.typing.ArrayLike
        the trace to truncate
    times : jax.typing.ArrayLike
        the times of the traces
    trace_sampling : float, default=0.1 ns
        the sampling rate of the traces in nanoseconds
    sample_axis : int, defualt=2
        the axis in which the samples are. default is 2
    sample_time_axis : int, default=1
        the axis in which the time is defined. default is 1
    ant_time_axis : int, default=0
        the axis in which the antennas are. default is 0
    """
    # get pad of shape which is 1/4 of trace shape
    nsamples = traces.shape[sample_axis]
    padded_shape = list(traces.shape)
    padded_shape[sample_axis] -= nsamples * 3 // 4
    nsamples_pad = padded_shape[sample_axis]

    # now pad on one side
    padded_traces = jnp.concatenate(
        [jnp.zeros(padded_shape), traces, jnp.zeros(padded_shape)], axis=sample_axis
    )
    nsamples_extended = int(nsamples + nsamples_pad * 2)

    # now shift the traces such that the signal is now in the center
    # center would be equal to original shape of trace since
    # trace length is now 2 * nsamples
    shifted_traces = shift_trace_to_center(padded_traces, sample_axis=sample_axis)

    # also modify the time traces
    # to do this, get min and max time
    # and manually create a grid
    new_min_times = (
        jnp.min(times, axis=sample_time_axis, keepdims=True)
        - trace_sampling * nsamples_pad
    )
    new_max_times = (
        jnp.max(times, axis=sample_time_axis, keepdims=True)
        + trace_sampling * nsamples_pad
    )

    extended_times = new_min_times + (new_max_times - new_min_times) * jnp.expand_dims(
        jnp.arange(nsamples_extended + 1), axis=ant_time_axis
    ) / (nsamples_extended - 1)

    # then shift the times until where the trace center is
    shifted_times = get_time_axes(
        extended_times, shift_idx=nsamples_extended//2, sample_time_axis=sample_time_axis
    )

    return shifted_traces, shifted_times


def get_time_axes(
    trace_times: jax.typing.ArrayLike,
    shift_idx: Union[int, None] = None,
    sample_time_axis: int = 1,
) -> jax.Array:
    """
    Get the time axes after shifting traces.

    Parameter:
    ----------
    trace_times : jax.typing.ArrayLike
        the time axes for the traces
    shift_idx : int
        the index to shift to
    sample_time_axis : int, default=1
        the axis where the time is defined
    """
    shift_idx = trace_times.shape[sample_time_axis] // 2 if None else shift_idx
    return trace_times + jnp.expand_dims(
        jnp.take(
            trace_times,
            indices=shift_idx,
            axis=sample_time_axis,
        )
        - jnp.min(trace_times, axis=sample_time_axis),
        axis=sample_time_axis,
    )
