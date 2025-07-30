"""
File copied from radiotools.coordinatesystems.

Contained here to remove unnecessary methods
and such that the translation from np <-> jax can be performed within here instead
of re-mapping everything to jax.numpy.

In the future, a jax version of radiotools should be constructed.
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jax
import jax.numpy as jnp
from typing_extensions import Self

import math
import copy

from .jax_utils import ModelMeta
from . import units

conversion_fieldstrength_cgs_to_SI = (
    2.99792458e10 * units.micro * units.volt / units.meter
)


class cstrafo(metaclass=ModelMeta):
    """class to performe coordinate transformations typically used in air shower radio detection.

    the following transformations are implemented:

    From the cartesian ground coordinate system (x: East, y: North, z: up) to
     * to the vxB-vx(vxB) system
     * to the on-sky coordinate system (spherical coordinates eR, eTheta, ePhi)
     * to a ground coordinate system where the y-axis is oriented to magnetic North (instead of geographic North)
     * to a shower plane coordinate system in which the z-axis is parallel to the shower axis
       and the shower axis projected on ground is in the yz-plane

    and vice versa.
    """

    def __init__(
        self: Self,
        zenith: float,
        azimuth: float,
        magnetic_field_vector: jax.typing.ArrayLike | None = None,
        site: str | None = None,
    ) -> None:
        """Initialize with signal/air-shower direction and magnetic field configuration.

        All parameters should be specified according to the default coordinate
        system of the radiotools package (the Auger coordinate system).

        Parameters
        ----------
        zenith : float
            zenith angle of the incoming signal/air-shower direction (0 deg is pointing to the zenith)
        azimuth : float
            azimuth angle of the incoming signal/air-shower direction (0 deg is North, 90 deg is South)
        magnetic_field_vector (optional): 3-vector, default None
            the magnetic field vector in the cartesian ground coordinate system,
            if no magnetic field vector is specified, the default value for the
            site specified in the 'site' function argument is used.
        site (optional): string, default 'Auger'
            this argument has only effect it 'magnetic_field_vector' is None
            the site for which the magnetic field vector should be used. Currently, default
            values for for the sites 'auger' and 'arianna' are available
        """
        showeraxis = -1 * spherical_to_cartesian(
            zenith, azimuth
        )  # -1 is because shower is propagating towards us
        if magnetic_field_vector is None:
            magnetic_field_vector = get_magnetic_field_vector(site=site)
        magnetic_field_normalized = magnetic_field_vector / jnp.linalg.norm(
            magnetic_field_vector
        )
        vxB = jnp.cross(showeraxis, magnetic_field_normalized)
        e1 = vxB
        e2 = jnp.cross(showeraxis, vxB)
        e3 = jnp.cross(e1, e2)

        e1 /= jnp.linalg.norm(e1)
        e2 /= jnp.linalg.norm(e2)
        e3 /= jnp.linalg.norm(e3)

        self.__transformation_matrix_vBvvB = copy.copy(jnp.array([e1, e2, e3]))
        self.__inverse_transformation_matrix_vBvvB = jnp.linalg.inv(
            self.__transformation_matrix_vBvvB
        )

        # initilize transformation matrix to on-sky coordinate system (er, etheta, ephi)
        ct = jnp.cos(zenith)
        st = jnp.sin(zenith)
        cp = jnp.cos(azimuth)
        sp = jnp.sin(azimuth)
        e1 = jnp.array([st * cp, st * sp, ct])
        e2 = jnp.array([ct * cp, ct * sp, -st])
        e3 = jnp.array([-sp, cp, 0])
        self.__transformation_matrix_onsky = copy.copy(jnp.array([e1, e2, e3]))
        self.__inverse_transformation_matrix_onsky = jnp.linalg.inv(
            self.__transformation_matrix_onsky
        )

        # initilize transformation matrix from magnetic north to geographic north coordinate system
        declination = get_declination(magnetic_field_vector)
        c = jnp.cos(-1 * declination)
        s = jnp.sin(-1 * declination)
        e1 = jnp.array([c, -s, 0])
        e2 = jnp.array([s, c, 0])
        e3 = jnp.array([0, 0, 1])
        self.__transformation_matrix_magnetic = copy.copy(jnp.array([e1, e2, e3]))
        self.__inverse_transformation_matrix_magnetic = jnp.linalg.inv(
            self.__transformation_matrix_magnetic
        )

        # initilize transformation matrix from ground (geographic) cs to ground
        # cs where x axis points into shower direction projected on ground
        c = jnp.cos(-1 * azimuth)
        s = jnp.sin(-1 * azimuth)
        e1 = jnp.array([c, -s, 0])
        e2 = jnp.array([s, c, 0])
        e3 = jnp.array([0, 0, 1])
        self.__transformation_matrix_azimuth = copy.copy(jnp.array([e1, e2, e3]))
        self.__inverse_transformation_matrix_azimuth = jnp.linalg.inv(
            self.__transformation_matrix_azimuth
        )

        # initilize transformation matrix from ground (geographic) cs to shower plane (early-late) cs
        # rotation along z axis -> shower axis along y axis
        c = jnp.cos(-azimuth + jnp.pi / 2)
        s = jnp.sin(-azimuth + jnp.pi / 2)
        e1 = jnp.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

        # rotation along x axis -> rotation in shower plane
        c = jnp.cos(zenith)
        s = jnp.sin(zenith)
        e2 = jnp.array([[1, 0, 0], [0, c, -s], [0, s, c]])

        self.__transformation_matrix_early_late = copy.copy(jnp.matmul(e2, e1))
        self.__inverse_transformation_matrix_early_late = jnp.linalg.inv(
            self.__transformation_matrix_early_late
        )

    def __transform(
        self, positions: jax.typing.ArrayLike, matrix: jax.typing.ArrayLike
    ) -> jax.Array:
        return jnp.squeeze(jnp.asarray(jnp.einsum("ij,...j->...i", matrix, positions)))

    def transform_from_ground_to_onsky(self, positions: jax.typing.ArrayLike):
        """on sky coordinates are eR, eTheta, ePhi"""
        return self.__transform(positions, self.__transformation_matrix_onsky)

    def transform_from_onsky_to_ground(self, positions: jax.typing.ArrayLike):
        """on sky coordinates are eR, eTheta, ePhi"""
        return self.__transform(positions, self.__inverse_transformation_matrix_onsky)

    def transform_from_magnetic_to_geographic(self, positions: jax.typing.ArrayLike):
        return self.__transform(positions, self.__transformation_matrix_magnetic)

    def transform_from_geographic_to_magnetic(self, positions: jax.typing.ArrayLike):
        return self.__transform(
            positions, self.__inverse_transformation_matrix_magnetic
        )

    def transform_from_azimuth_to_geographic(self, positions: jax.typing.ArrayLike):
        return self.__transform(positions, self.__transformation_matrix_azimuth)

    def transform_from_geographic_to_azimuth(self, positions: jax.typing.ArrayLike):
        return self.__transform(positions, self.__inverse_transformation_matrix_azimuth)

    def transform_to_vxB_vxvxB(
        self,
        station_position: jax.typing.ArrayLike,
        core: jax.typing.ArrayLike | None = None,
    ):
        """Transform a single station position or a list of multiple station positions into vxB, vxvxB shower plane.

        This function is supposed to transform time traces with the shape
        (number of polarizations, length of trace) and a list of station positions
        with the shape of (length of list, 3). The function automatically differentiates
        between the two cases by checking the length of the second dimension. If
        this dimension is '3', a list of station positions is assumed to be the input.
        Note: this logic will fail if a trace will have a shape of (3, 3), which is however
        unlikely to happen.

        """
        # to keep station_position constant (for the outside)
        if core is not None:
            station_position = jnp.array(copy.deepcopy(station_position))

        # if a single station position is transformed: (3,) -> (1, 3)
        if station_position.ndim == 1:
            station_position = jnp.expand_dims(station_position, axis=0)

        nY = station_position.shape[-1]  # length of the time traces
        if nY != 3:
            raise ValueError("Dimension in last axis is not == 3.")
        else:
            return self.__transform(
                station_position, self.__transformation_matrix_vBvvB
            )

    def transform_from_vxB_vxvxB(
        self,
        station_position: jax.typing.ArrayLike,
        core: jax.typing.ArrayLike | None = None,
    ):
        """Transform a single station position or a list of multiple station positions back to x,y,z CS.

        This function is supposed to transform time traces with the shape
        (number of polarizations, length of trace) and a list of station positions
        with the shape of (length of list, 3). The function automatically differentiates
        between the two cases by checking the length of the second dimension. If
        this dimension is '3', a list of station positions is assumed to be the input.
        Note: this logic will fail if a trace will have a shape of (3, 3), which is however
        unlikely to happen.
        """
        # to keep station_position constant (for the outside)
        if core is not None:
            station_position = jnp.array(copy.deepcopy(station_position))

        # if a single station position is transformed: (3,) -> (1, 3)
        if station_position.ndim == 1:
            station_position = jnp.expand_dims(station_position, axis=0)

        nY = station_position.shape[-1]  # length of the time traces
        if nY != 3:
            return self.__transform(
                station_position, self.__inverse_transformation_matrix_vBvvB
            )
        else:
            result = []
            for pos in station_position:
                temp = self.__transform(pos, self.__inverse_transformation_matrix_vBvvB)
                if core is not None:
                    result.append(temp + core)
                else:
                    result.append(temp)

            return jnp.squeeze(jnp.array(result))

    def transform_from_vxB_vxvxB_2D(
        self,
        station_position: jax.typing.ArrayLike,
        core: jax.typing.ArrayLike | None = None,
    ):
        """Transform a single station position or a list of multiple station positions back to x,y,z CS."""
        # to keep station_position constant (for the outside)
        if core is not None:
            station_position = jnp.array(copy.deepcopy(station_position))

        # if a single station position is transformed: (3,) -> (1, 3)
        if station_position.ndim == 1:
            station_position = jnp.expand_dims(station_position, axis=0)

        result = []
        for pos in station_position:
            position = jnp.array(
                [pos[0], pos[1], self.get_height_in_showerplane(pos[0], pos[1])]
            )
            pos_transformed = self.__transform(
                position, self.__inverse_transformation_matrix_vBvvB
            )
            if core is not None:
                pos_transformed += core
            result.append(pos_transformed)

        return jnp.squeeze(jnp.array(result))

    def get_height_in_showerplane(self, x, y):
        return (
            -1.0
            * (
                self.__transformation_matrix_vBvvB[0, 2] * x
                + self.__transformation_matrix_vBvvB[1, 2] * y
            )
            / self.__transformation_matrix_vBvvB[2, 2]
        )

    def get_euler_angles(self):
        R = self.__transformation_matrix_vBvvB
        if abs(R[2, 0]) != 1:
            theta_1 = -math.asin(R[2, 0])
            theta_2 = math.pi - theta_1
            psi_1 = math.atan2(R[2, 1] / math.cos(theta_1), R[2, 2] / math.cos(theta_1))
            psi_2 = math.atan2(R[2, 1] / math.cos(theta_2), R[2, 2] / math.cos(theta_2))
            phi_1 = math.atan2(R[1, 0] / math.cos(theta_1), R[0, 0] / math.cos(theta_1))
            phi_2 = math.atan2(R[1, 0] / math.cos(theta_2), R[0, 0] / math.cos(theta_2))
        else:
            phi_1 = 0.0
            if R[2, 0] == -1:
                theta_1 = math.pi * 0.5
                psi_1 = phi_1 + math.atan2(R[0, 1], R[0, 2])
            else:
                theta_1 = -1.0 * math.pi * 0.5
                psi_1 = -phi_1 + math.atan2(-R[0, 1], -R[0, 2])
        return psi_1, theta_1, phi_1


"""
Below helper functions are obtained from radiotools.helper. Only the relevant functions are copied
and converted to jax
"""


def spherical_to_cartesian(zenith: float, azimuth: float):
    sinZenith = jnp.sin(zenith)
    x = sinZenith * jnp.cos(azimuth)
    y = sinZenith * jnp.sin(azimuth)
    z = jnp.cos(zenith)
    if hasattr(zenith, "__len__") and hasattr(azimuth, "__len__"):
        return jnp.array([x, y, z]).T
    else:
        return jnp.array([x, y, z])


def get_magnetic_field_vector(site: str | None = None):
    """
    get the geomagnetic field vector in Gauss. x points to geographic East and y towards geographic North
    """
    magnetic_fields = {
        "auger": jnp.array([0.00871198, 0.19693423, 0.1413841]),
        "mooresbay": jnp.array([0.058457, -0.09042, 0.61439]),
        "summit": jnp.array(
            [-0.037467, 0.075575, -0.539887]
        ),  # Summit station, Greenland
        "southpole": jnp.array(
            [-0.14390398, 0.08590658, 0.52081228]
        ),  # position of SP arianna station
        "lofar": jnp.array([0.004675, 0.186270, -0.456412]),  # values from 2015
    }
    if site is None:
        site = "auger"
    return magnetic_fields[site]


def get_declination(magnetic_field_vector: jax.typing.ArrayLike):
    declination = jnp.arccos(
        jnp.dot(
            jnp.array([0, 1]),
            magnetic_field_vector[:2] / jnp.linalg.norm(magnetic_field_vector[:2]),
        )
    )
    return declination

"""
Code that is contained in utilities.cs_transformations.

I shift them here for better convenience.
"""


def e_geo(
    traces: jax.typing.ArrayLike, x: jax.typing.ArrayLike, y: jax.typing.ArrayLike
) -> jax.Array:
    """
    Calculate the geomagnetic component from the electric field in the showerplane, i.e. the electric field should be in the (vxB, vxvxB, v) CS.

    Parameters
    ----------
    traces : jax.typing.ArrayLike
        The traces in the showerplane (vB, vvB, v).
        The polarisation must be at the last axis!
    x : jax.typing.ArrayLike
        The antenna position along the vxB axis.
        Shapes should match that of the traces.
    y : jax.typing.ArrayLike
        The antenna position along the vxvxB axis
        Shapes should match that of the traces.

    Returns
    -------
    e_geo : jax.Array
        The geomagnetic component of the electric field
    """
    return traces[..., 1] * x / y - traces[..., 0]


def e_ce(
    traces: jax.typing.ArrayLike, x: jax.typing.ArrayLike, y: jax.typing.ArrayLike
) -> jax.Array:
    """
    Calculate the charge-excess (or Askaryan) component of electric field in the showerplane, i.e. the electric field should be in the (vxB, vxvxB, v) CS.

    Parameters
    ----------
    traces : jax.typing.ArrayLike
        The traces in the showerplane (vB, vvB, v).
        The polarisation must be at the last axis!
    x : jax.typing.ArrayLike
        The antenna position along the vxB axis
        Shapes should match that of the traces.
    y : jax.typing.ArrayLike
        The antenna position along the vxvxB axis
        Shapes should match that of the traces.

    Returns
    -------
    e_ce : jax.Array
        The charge-excess component of the electric field
    """
    return -traces[..., 1] * jnp.sqrt(x**2 + y**2) / y


def e_to_geo_ce(
    traces: jax.typing.ArrayLike, x: jax.typing.ArrayLike, y: jax.typing.ArrayLike
) -> tuple[jax.Array, jax.Array]:
    """
    Decompose the electric field traces into geomagnetic & charge-excess components.

    Parameters
    ----------
    traces : jax.typing.ArrayLike
        The traces in the showerplane (vB, vvB, v).
        The polarisation must be at the last axis!
    x : jax.typing.ArrayLike
        The antenna position along the vxB axis
        Shapes should match that of the traces.
    y : jax.typing.ArrayLike
        The antenna position along the vxvxB axis
        Shapes should match that of the traces.

    Returns
    -------
    (e_geo, e_ce) : tuple[jax.Array, jax.Array]
        The geomagnetic and charge-excess component of the electric field
    """
    return e_geo(traces, x, y), e_ce(traces, x, y)


def geo_ce_to_vB_vvB_v(
    traces: jax.typing.ArrayLike, x: jax.typing.ArrayLike, y: jax.typing.ArrayLike
) -> jax.Array:
    """
    Combine geomagnetic & charge-excess component of electric field to antenna E-fields in the shower plane (vB x vvB).
    
    Parameters
    ----------
    traces : jax.typing.ArrayLike
        The traces in geomagnetic and charge excess components.
        The polarisation must be at the last axis!
    x : jax.typing.ArrayLike
        The antenna position along the vxB axis
        Shapes should match that of the traces.
    y : jax.typing.ArrayLike
        The antenna position along the vxvxB axis
        Shapes should match that of the traces.

    Returns
    -------
    traces_vB_vvB : jax.Array
        The electric field traces in (vB, vvB) plane
    """
    my_e_geo = traces.T[0]
    my_e_ce = traces.T[1]

    r = jnp.sqrt(x ** 2 + y ** 2)

    trace_vB = -1 * (my_e_geo + my_e_ce * x / r)
    trace_vvB = -1 * y / r * my_e_ce
    trace_v = jnp.zeros_like(trace_vB)

    return jnp.stack((trace_vB.T, trace_vvB.T, trace_v.T), axis=-1)

def get_normalized_angle(angle, degree=False, interval=jnp.deg2rad(jnp.array([0, 360]))):
    import collections.abc
    if degree:
        interval = jnp.rad2deg(interval)
    delta = interval[1] - interval[0]
    if(isinstance(angle, (collections.abc.Sequence, jnp.ndarray))):
        angle[angle >= interval[1]] -= delta
        angle[angle < interval[0]] += delta
    else:
        while (angle >= interval[1]):
            angle -= delta
        while (angle < interval[0]):
            angle += delta
    return angle

