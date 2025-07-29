# jax_radio_tools : A JAXified version of radiotools (in progress!)

Utility functions for radio emission of cosmic rays in the JAX framework. Based on [radiotools](https://github.com/nu-radio/radiotools/tree/master).

## Installation

The tool can easily be installed via `pip`:

```
pip install -U jax_radio_tools
```

which will also install the necessary packages for installation.

## Dependencies
- `jax`
- `jaxlib`
- `numpy >=1.20`
- `typing_extensions`
- `python>=3.11` (May be possible with older python versions, but not yet tested)

## Current implementations

Currently, the following tools are implemented:

### Trace Utilities

These can be accessed via `jax_radio_tools.trace_utils`.

- zero padding
- bandpass filter
- hilbert envelope
- resampler
- trace centering
- relative trace centering 
- signal window truncation

### Shower Utilities

These can be accessed via `jax_radio_tools.shower_utils`.

- calculating arrival times
- calculating gaisser hillas functions (coreas formalism, LR formalism)
    - change: updated the functions to make it more numerically stable
- calculating fluences
- calculating cross correlations

### Atmosphere model
Following radiotools, an importable module to define the atmosphere. 

These can be accessed via `jax_radio_tools.atmosphere.Atmosphere`.

Current features implemented are:
- calculation of distance from grammages
- calculation of cherenkov angle
- calculation of vertical heights
- calculation of density
- calculation of refractive index
- all atmospheric models from radiotools are supported
- additionally, GDAS atmospheric files are also now supported

### Coordinate system
Following radiotools, we define a cstrafo object that takes care of coordinate systems. This is defined
by a zenith angle, azimuthal angle, and magnetic field vector.

These can be accessed via `jax_radio_tools.cstrafo`.

Further calculations that are in the `coordinate_transformations`:
- transformation from GEO/CE <-> vxB / vxvxB axis in the shower plane
- function to get the normalised angle (for accurate angles when porting from e.g. CoREAS)

More implementations to come!

## TODOS

- [ ] include documentation
- [ ] include CI/CD pipeline
- [ ] implement other useful radiotools functions
- [ ] make the cstrafo object jax-compatible with zenith & azimuth angles

## LICENSE

This code is under the BSD-3 License. See [LICENSE](LICENSE) for more details.


