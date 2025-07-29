"""Helper for reading GDAS models"""

from typing_extensions import Self
import jax
import jax.numpy as jnp
import numpy as np

class GDASAtmosphere:
    """Class that encodes the GDAS atmosphere."""

    def __init__(self : Self, gdas_file : str) -> None:
        """
        Initialize the GDAS atmosphere.

        Parameter:
        ----------
        gdas_file: str
            Path to the GDAS file

        """
        self.gdas_file = gdas_file
        print(f"Reading GDAS file: {gdas_file.split('/')[-1]}")

    def get_gdas_atm_model(self : Self) -> tuple[jnp.array, jnp.array, jnp.array, jnp.array]:
        """
        Parse a GDAS file and gets the parameter a, b, c, h.

        Parameter:
        ----------
        gdas_file: str
            Path to the GDAS file

        Return:
        ------- 
        the parameters a, b, c, h

        """
        with open(self.gdas_file, "rb") as f:
            # pipe contents of the file through
            lines = f.readlines()

            # skip first entry (0), conversion cm -> m
            h = jnp.array(lines[1].strip(b"\n").split()[1:], dtype=float) / 100

            a = jnp.array(lines[2].strip(b"\n").split(), dtype=float) * 1e4
            b = jnp.array(lines[3].strip(b"\n").split(), dtype=float) * 1e4
            c = jnp.array(lines[4].strip(b"\n").split(), dtype=float) * 1e-2

        return a, b, c, h

    def get_refractive_index_profile(self : Self) -> jnp.array:
        """
        Parse a GDAS file and returns the refractive index profile.

        Parameter:
        ----------

        gdas_file: str
            Path to the GDAS file

        Return: 
        --------
        Refractive index profile (heights, n) as numpy array

        """
        h, n = np.genfromtxt(self.gdas_file, unpack=True, skip_header=6)
        return jnp.array([h, n])
    
    def get_refractive_index(self : Self, h : float) -> float:
        """
        Get the refractive index at a given height.

        Parameter:
        ----------
        h: float
            Height in meters

        Return:
        -------
        Refractive index at height h

        """
        h_grid, n_grid = self.get_refractive_index_profile()
        return jnp.interp(x=h, xp=h_grid, fp=n_grid)