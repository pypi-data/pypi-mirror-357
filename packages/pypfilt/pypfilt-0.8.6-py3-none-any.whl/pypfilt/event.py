"""Structured types for event handlers."""

import numpy as np
from typing import Any, Dict, List, NamedTuple

from .build import Context
from .state import Snapshot


class LogLikelihood(NamedTuple):
    """
    The log-likelihood of an observation according to each particle.
    """

    obs: Dict[str, Any]
    """The observation dictionary."""

    log_llhds: np.ndarray
    """The log-likelihoods according to each particle (1-D array)."""

    weights: np.ndarray
    """The particle weights prior to this time-step (1-D array)."""


class AfterReweight(NamedTuple):
    """
    The particle states after weights have been updated in response to one or
    more observations for the current time-step.
    """

    ctx: Context
    """The simulation context."""

    snapshot: Snapshot
    """The current particle states."""


class BeforeResample(NamedTuple):
    """
    The particle states before resampling, but after updating weights in
    response to any observations for the current time-step.
    """

    ctx: Context
    """The simulation context."""

    time: Any
    """The current time."""

    partition: int
    """The (zero-based) number of the partition being resampled."""

    vec: np.ndarray
    """The history matrix slice for the current time."""


class BeforeRegularisation(NamedTuple):
    """
    The particle states before post-regularisation.
    """

    ctx: Context
    """The simulation context."""

    partition: int
    """The (zero-based) number of the partition being resampled."""

    vec: np.ndarray
    """The history matrix slice for the current time-step."""


class AfterRegularisation(NamedTuple):
    """
    The particle states after post-regularisation.
    .
    """

    ctx: Context
    """The simulation context."""

    partition: int
    """The (zero-based) number of the partition being resampled."""

    vec: np.ndarray
    """The history matrix slice for the current time-step."""


class AfterResample(NamedTuple):
    """
    The particle states after resampling (including post-regularisation, if
    enabled).
    """

    ctx: Context
    """The simulation context."""

    time: Any
    """The current time."""

    partition: int
    """The (zero-based) number of the partition being resampled."""

    vec: np.ndarray
    """The history matrix slice for the current time-step."""


class AfterTimeStep(NamedTuple):
    """
    The particle states after the completion of a time-step.
    """

    ctx: Context
    """The simulation context."""

    snapshot: Snapshot
    """The current particle states."""

    obs_list: List[Dict[str, Any]]
    """The observations (if any) for this time-step."""

    resample_mask: np.ndarray
    """The particles that have been resampled (1-D boolean array)."""
