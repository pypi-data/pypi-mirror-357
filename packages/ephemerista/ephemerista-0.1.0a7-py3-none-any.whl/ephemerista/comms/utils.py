"""The utils.py module.

This module provides various utilities and physical constants for link budget calculations.
"""

import math
import typing
from typing import Literal, overload

import numpy as np
from numpy.typing import ArrayLike

"""The Boltzmann constant"""
BOLTZMANN_CONSTANT: float = 1.38064852e-23  # J/K

"""Average room temperature in K"""
ROOM_TEMPERATURE = 290  # K

"""The speed of light in vacuum in m/s"""
SPEED_OF_LIGHT_VACUUM: float = 2.99792458e8  # m/s


def wavelength(frequency: float) -> float:
    """Return the wavelength of electromagnetic radiation of a given frequency."""
    return SPEED_OF_LIGHT_VACUUM / frequency


@overload
def to_db(val: float) -> float: ...


@overload
def to_db(val: ArrayLike) -> ArrayLike: ...


def to_db(val: ArrayLike | float) -> ArrayLike | float:
    """Convert a given value to decibel."""
    return 10 * np.log10(val)


@overload
def from_db(val: float) -> float: ...


@overload
def from_db(val: np.ndarray) -> np.ndarray: ...


def from_db(val: np.ndarray | float) -> np.ndarray | float:
    """Convert from decibel."""
    return 10 ** (val / 10)


def free_space_path_loss(distance: float, frequency: float) -> float:
    """Calculate the free-space path loss for a given frequency and distance.

    Parameters
    ----------
    distance : float
        Distance in km
    frequency : float
        Frequency in Hz


    Returns
    -------
    float
        Free-space path loss in dB
    """
    return to_db((4 * math.pi * distance * 1e3 / wavelength(frequency)) ** 2)


Band = Literal["HF", "VHF", "UHF", "L", "S", "C", "X", "Ku", "K", "Ka", "V", "W"]

BAND_NAMES = typing.get_args(Band)

BAND_FREQS = np.array([3e6, 30e6, 300e6, 1e9, 2e9, 4e9, 8e9, 12e9, 18e9, 27e9, 40e9, 75e9, 110e9])

MAX_FREQ = 110e9


def frequency_band(freq: float) -> Literal[Band] | None:
    """Return the corresponding frequency band for a given frequency."""
    if freq < BAND_FREQS[0] or freq > MAX_FREQ:
        return None
    return BAND_NAMES[np.flatnonzero(BAND_FREQS <= freq)[-1]]
