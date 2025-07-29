"""
An example of the SIRV model of infectious disease epidemics that supports
several interventions.
"""

import numpy as np
import pkgutil
import scipy.stats

from ..io import time_field
from ..model import Model
from ..obs import Univariate
from ..summary import Table


def sirv_toml_data():
    """
    Return the contents of the example file "sirv.toml".
    """
    return pkgutil.get_data('pypfilt.examples', 'sirv.toml').decode()


class SirvOde(Model):
    """
    An ordinary differential equation implementation of the SIRV model, using
    the forward Euler method, which supports two types of interventions:

    * Reducing ``R0`` by some fraction (``R0_reduction``) once daily incidence
      reaches some threshold (``R0_inc_threshold``); and

    * Moving individuals from ``S`` to ``V`` at some rate (``Vaccine_rate``),
      beginning at some time (``Vaccine_start``).

    The model settings must include the following keys:

    * ``population_size``: The number of individuals in the population.
    """

    def field_types(self, ctx):
        """
        Define the state vector structure.
        """
        return [
            # Model state variables.
            ('S', np.float64),
            ('I', np.float64),
            ('R', np.float64),
            ('V', np.float64),
            # Model parameters.
            ('R0', np.float64),
            ('gamma', np.float64),
            # Intervention parameters: reducing R0.
            ('R0_reduction', np.float64),
            ('R0_inc_threshold', np.float64),
            ('R0_effect', bool),
            # Intervention parameters: vaccination.
            ('Vaccine_rate', np.float64),
            ('Vaccine_start', np.float64),
        ]

    def can_smooth(self):
        """
        The fields that can be smoothed by the post-regularisation filter.
        """
        # Return the continuous model parameters.
        return {'R0', 'gamma'}

    def init(self, ctx, vec):
        """
        Initialise the state vectors.
        """
        # Initialise the model state variables.
        population = ctx.settings['model']['population_size']
        vec['S'] = population - 1
        vec['I'] = 1
        vec['R'] = 0
        vec['V'] = 0
        # This records whether a reduction in R0 has already occurred.
        vec['R0_effect'] = False

        # Initialise the model parameters.
        prior = ctx.data['prior']
        for param, samples in prior.items():
            vec[param] = samples

    def update(self, ctx, time_step, is_forecast, prev, curr):
        """
        Update the state vectors.
        """
        # Define vaccination rates for each particle.
        mask_vacc = (prev['Vaccine_rate'] > 0) & (
            prev['Vaccine_start'] <= time_step.start
        )
        if np.any(mask_vacc):
            vacc = mask_vacc.astype(int) * prev['Vaccine_rate']
        else:
            vacc = 0

        # Check for particles where a reduction in R0 should now be imposed.
        past = ctx.component['history'].snapshot(ctx).back_n_units(1)
        daily_incidence = past['state_vec']['S'] - prev['S']
        mask_decr = (prev['R0_reduction'] > 0) & (
            prev['R0_inc_threshold'] <= daily_incidence
        )
        # Define reductions (if any) in R0 for each particle.
        mask_R0_effect = mask_decr | prev['R0_effect']
        if np.any(mask_R0_effect):
            R0_scale = 1 - mask_R0_effect.astype(int) * prev['R0_reduction']
        else:
            R0_scale = 1

        # Calculate the flow rates out of S and I.
        beta = R0_scale * prev['R0'] * prev['gamma']
        N = ctx.settings['model']['population_size']
        s_out = time_step.dt * beta * prev['I'] * prev['S'] / N
        i_out = time_step.dt * prev['gamma'] * prev['I']
        v_in = time_step.dt * np.minimum(vacc, prev['S'] - s_out)

        # Ensure all flows are non-negative.
        s_out = s_out.clip(min=0)
        i_out = i_out.clip(min=0)
        v_in = v_in.clip(min=0)

        # Update the state variables.
        curr['S'] = (prev['S'] - s_out - v_in).clip(min=0)
        curr['I'] = prev['I'] + s_out - i_out
        curr['R'] = prev['R'] + i_out
        curr['V'] = prev['V'] + v_in

        # Copy the model parameters.
        curr['R0'] = prev['R0']
        curr['gamma'] = prev['gamma']
        curr['R0_reduction'] = prev['R0_reduction']
        curr['R0_inc_threshold'] = prev['R0_inc_threshold']
        curr['R0_effect'] = mask_R0_effect
        curr['Vaccine_rate'] = prev['Vaccine_rate']
        curr['Vaccine_start'] = prev['Vaccine_start']


class Incidence(Univariate):
    r"""
    A perfect observation model for incidence in the SIRV model.

    :param obs_unit: A descriptive name for the data.
    :param settings: The observation model settings dictionary.

    The settings dictionary should contain the following keys:

    * ``observation_period``: The observation period :math:`\Delta`.

    For example:

    .. code-block:: toml

       [observations.cases]
       model = "pypfilt.examples.sir.SirvCumIncidence"
       observation_period = 1
    """

    def new_infections(self, ctx, snapshot):
        r"""
        Return the number of new infections :math:`S(t-\Delta) - S(t)` that
        occurred during the observation period :math:`\Delta` for each
        particle.
        """
        period = self.settings['observation_period']
        prev = snapshot.back_n_units_state_vec(period)
        cum_infs_curr = snapshot.state_vec['I'] + snapshot.state_vec['R']
        cum_infs_past = prev['I'] + prev['R']
        incidence = (cum_infs_curr - cum_infs_past).clip(min=0)
        return incidence

    def distribution(self, ctx, snapshot):
        """
        Return the observation distribution for each particle.
        """
        infections = self.new_infections(ctx, snapshot)
        return scipy.stats.norm(loc=infections, scale=0)


class FinalSize(Table):
    """
    Calculate the final epidemic size for each particle.
    """

    def field_types(self, ctx, obs_list, name):
        return [
            time_field('fs_time'),
            ('weight', np.float64),
            ('final_size', np.float64),
        ]

    def n_rows(self, ctx, forecasting):
        return ctx.particle_count()

    def add_rows(self, ctx, fs_time, window, insert_fn):
        pass

    def finished(self, ctx, fs_time, window, insert_fn):
        final_snapshot = window[-1]
        final_sizes = final_snapshot.state_vec['R']
        for ix, final_size in enumerate(final_sizes):
            weight = final_snapshot.weights[ix]
            insert_fn((fs_time, weight, final_size))
