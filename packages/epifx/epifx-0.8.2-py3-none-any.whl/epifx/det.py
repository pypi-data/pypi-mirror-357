"""Deterministic models of infectious diseases."""

import numpy as np
from .model import Model


class SEIR(Model):
    r"""
    An SEIR compartment model for a single circulating influenza strain, under
    the assumption that recovered individuals are completely protected against
    reinfection.

    .. math::

        \frac{dS}{dt} &= - \beta S^\eta I \\[0.5em]
        \frac{dE}{dt} &= \beta S^\eta I - \sigma E \\[0.5em]
        \frac{dI}{dt} &= \sigma E - \gamma I \\[0.5em]
        \frac{dR}{dt} &= \gamma I \\[0.5em]
        \beta &= R_0 \cdot \gamma \\[0.5em]
        E(0) &= \frac{1}{N}

    ==============  ================================================
    Parameter       Meaning
    ==============  ================================================
    :math:`R_0`     Basic reproduction number
    :math:`\sigma`  Inverse of the incubation period (day :sup:`-1`)
    :math:`\gamma`  Inverse of the infectious period (day :sup:`-1`)
    :math:`\eta`    Inhomogeneous social mixing coefficient
    :math:`\alpha`  Temporal forcing coefficient
    :math:`t_0`     The time at which the epidemic begins
    ==============  ================================================

    The force of infection can be subject to temporal forcing :math:`F(t)`, as
    mediated by :math:`\alpha`:

    .. math::

        \beta(t) = \beta \cdot \left[1 + \alpha \cdot F(t)\right]

    Note that this requires the forcing time-series to be stored in the lookup
    table ``'R0_forcing'``.

    .. note:: The population size :math:`N` must be defined for each scenario:

       .. code-block:: toml

          [model]
          population_size = 1000
    """

    __fields = [
        'S',
        'E',
        'I',
        'R',
        'R0',
        'sigma',
        'gamma',
        'eta',
        'alpha',
        't0',
    ]

    def __init__(self):
        """Initialise the model instance."""
        self.__Forcing_lookup = None

    def field_types(self, ctx):
        return [(name, np.float64) for name in self.__fields]

    def can_smooth(self):
        # NOTE: we choose not to allow smoothing of t0.
        return set(self.__fields[4:-1])

    def population_size(self):
        return self.popn_size

    def init(self, ctx, vec):
        """Initialise a state vector.

        :param ctx: The simulation context.
        :param vec: An uninitialised state vector of correct dimensions (see
            :py:func:`~state_size`).
        """
        self.popn_size = ctx.settings['model']['population_size']

        prior = ctx.data['prior']

        # Initialise the model state (fully susceptible population).
        initial_exposures = 1.0 / self.popn_size
        vec[:] = 0
        vec['S'] = 1 - initial_exposures
        vec['E'] = initial_exposures
        vec['R0'] = prior['R0']
        vec['sigma'] = prior['sigma']
        vec['gamma'] = prior['gamma']
        vec['eta'] = prior['eta']
        vec['alpha'] = 0
        vec['t0'] = prior['t0']

        # Only sample alpha (R0 forcing) if a lookup table was provided.
        forcing_table = ctx.component['lookup'].get('R0_forcing')
        if forcing_table is not None:
            vec['alpha'] = prior['alpha']

    def update(self, ctx, time_step, is_fs, prev, curr):
        """Perform a single time-step.

        :param ctx: The simulation context.
        :param time_step: The time-step details.
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        """
        # Update parameters and lookup tables that are defined in self.init()
        # and which will not exist if we are resuming from a cached state.
        self.popn_size = ctx.settings['model']['population_size']

        # Extract each parameter.
        R0 = prev['R0'].copy()
        sigma = prev['sigma'].copy()
        gamma = prev['gamma'].copy()
        eta = prev['eta'].copy()
        alpha = prev['alpha'].copy()
        t0 = prev['t0'].copy()

        beta = R0 * gamma

        forcing_table = ctx.component['lookup'].get('R0_forcing')
        if forcing_table is not None:
            # Modulate the force of infection with temporal forcing.
            force = forcing_table.lookup(time_step.end)
            # Ensure the force of infection is non-negative (can be zero).
            beta *= np.maximum(1.0 + alpha * force, 0)

        epoch = ctx.settings['time']['epoch']
        epoch = ctx.component['time'].to_scalar(epoch)
        curr_t = ctx.component['time'].to_scalar(time_step.end)
        zero_mask = t0 > (curr_t - epoch)
        R0[zero_mask] = 0
        sigma[zero_mask] = 0
        gamma[zero_mask] = 0
        eta[zero_mask] = 0
        alpha[zero_mask] = 0
        t0[zero_mask] = 0
        beta[zero_mask] = 0

        # Extract the compartment values used to update the model state.
        S = prev['S']
        E = prev['E']
        I = prev['I']

        # Calculate flows between compartments.
        dt = time_step.dt
        s_to_e = dt * beta * I * S**eta
        e_to_i = dt * sigma * E
        i_to_r = dt * gamma * I

        # Update the compartment values.
        curr['S'] = S - s_to_e
        curr['E'] = E + s_to_e - e_to_i
        curr['I'] = I + e_to_i - i_to_r

        # Enforce invariants on the S, E, and I compartments.
        cols_SEI = ['S', 'E', 'I']
        for col in cols_SEI:
            curr[col] = np.clip(curr[col], 0, 1)

        sum_SEI = curr['S'] + curr['E'] + curr['I']
        mask_invalid = sum_SEI > 1
        if np.any(mask_invalid):
            denom = sum_SEI[mask_invalid]
            for col in cols_SEI:
                curr[col][mask_invalid] = curr[col][mask_invalid] / denom
            # Update the net non-R population.
            sum_SEI = curr['S'] + curr['E'] + curr['I']

        # Calculate the size of the R compartment and clip appropriately.
        curr['R'] = np.clip(1.0 - sum_SEI, 0.0, 1.0)

        # Keep parameters fixed.
        param_cols = ['R0', 'sigma', 'gamma', 'eta', 'alpha', 't0']
        curr[param_cols] = prev[param_cols]

    def pr_inf(self, prev, curr):
        """Calculate the likelihood of an individual becoming infected, for
        any number of state vectors.

        :param prev: The model states at the start of the observation period.
        :param curr: The model states at the end of the observation period.
        """
        # Count the number of susceptible / exposed individuals at both ends
        # of the simulation period.
        prev_amt = prev['S'] + prev['E']
        curr_amt = curr['S'] + curr['E']
        # Avoid returning very small negative values (e.g., -1e-10).
        return np.maximum(prev_amt - curr_amt, 0)

    def is_seeded(self, hist):
        """Identify state vectors where infections have occurred.

        :param hist: A matrix of arbitrary dimensions, whose final dimension
            covers the model state space (i.e., has a length no smaller than
            that returned by :py:func:`state_size`).
        :type hist: numpy.ndarray

        :returns: A matrix of one fewer dimensions than ``hist`` that contains
            ``1`` for state vectors where infections have occurred and ``0``
            for state vectors where they have not.
        :rtype: numpy.ndarray
        """
        initial_exposures = 1.0 / self.popn_size
        initial_S = 1 - initial_exposures
        return np.ceil(hist['S'] < initial_S)

    def is_valid(self, hist):
        """Ignore state vectors where no infections have occurred, as their
        properties (such as parameter distributions) are uninformative."""
        return self.is_seeded(hist)

    def stat_info(self):
        """Return the details of each statistic that can be calculated by this
        model. Each such statistic is represented as a ``(name, stat_fn)``
        pair, where ``name`` is a string that identifies the statistic and
        ``stat_fn`` is a function that calculates the statistic (see, e.g.,
        :py:func:`stat_Reff`).
        """
        return [('Reff', self.stat_Reff)]

    def stat_Reff(self, hist):
        """Calculate the effective reproduction number :math:`R_\\mathrm{eff}`
        for every particle.

        :param hist: The particle history matrix, or a subset thereof.
        """
        return hist['S'] * hist['R0']


class SEEIIR(Model):
    r"""An SEEIIR compartment model for a single circulating influenza strain,
    under the assumption that recovered individuals are completely protected
    against reinfection.

    .. math::

        \frac{dS}{dt} &= - \beta S^\eta (I_1 + I_2) \\[0.5em]
        \frac{dE_1}{dt} &= \beta S^\eta (I_1 + I_2) - 2 \sigma E_1 \\[0.5em]
        \frac{dE_2}{dt} &= 2 \sigma E_1 - 2 \sigma E_2 \\[0.5em]
        \frac{dI_1}{dt} &= 2 \sigma E_2 - 2 \gamma I_1 \\[0.5em]
        \frac{dI_2}{dt} &= 2 \gamma I_1 - 2 \gamma I_2 \\[0.5em]
        \frac{dR}{dt} &= 2 \gamma I_2 \\[0.5em]
        \beta &= R_0 \cdot \gamma \\[0.5em]
        E_1(0) &= \frac{1}{N}

    ==============  ================================================
    Parameter       Meaning
    ==============  ================================================
    :math:`R_0`     Basic reproduction number
    :math:`\sigma`  Inverse of the incubation period (day :sup:`-1`)
    :math:`\gamma`  Inverse of the infectious period (day :sup:`-1`)
    :math:`\eta`    Inhomogeneous social mixing coefficient
    :math:`\alpha`  Temporal forcing coefficient
    :math:`t_0`     The time at which the epidemic begins
    ==============  ================================================

    The force of infection can be subject to temporal forcing :math:`F(t)`, as
    mediated by :math:`\alpha`:

    .. math::

        \beta(t) = \beta \cdot \left[1 + \alpha \cdot F(t)\right]

    Note that this requires the forcing time-series to be stored in the lookup
    table ``'R0_forcing'``.

    .. note:: The population size :math:`N` must be defined for each scenario:

       .. code-block:: toml

          [model]
          population_size = 1000
    """

    __fields = [
        'S',
        'E1',
        'E2',
        'I1',
        'I2',
        'R',
        'R0',
        'sigma',
        'gamma',
        'eta',
        'alpha',
        't0',
    ]

    def field_types(self, ctx):
        return [(name, np.float64) for name in self.__fields]

    def can_smooth(self):
        # NOTE: we choose not to allow smoothing of t0.
        return set(self.__fields[6:-1])

    def population_size(self):
        return self.popn_size

    def init(self, ctx, vec):
        """Initialise a state vector.

        :param ctx: The simulation context.
        :param vec: An uninitialised state vector of correct dimensions.
        """
        self.popn_size = ctx.settings['model']['population_size']

        prior = ctx.data['prior']

        # Initialise the model state (fully susceptible population).
        initial_exposures = 1.0 / self.popn_size
        vec[:] = 0
        vec['S'] = 1 - initial_exposures
        vec['E1'] = initial_exposures
        vec['R0'] = prior['R0']
        vec['sigma'] = prior['sigma']
        vec['gamma'] = prior['gamma']
        vec['eta'] = prior['eta']
        vec['alpha'] = 0
        vec['t0'] = prior['t0']

        # Only sample alpha (R0 forcing) if a lookup table was provided.
        forcing_table = ctx.component['lookup'].get('R0_forcing')
        if forcing_table is not None:
            vec['alpha'] = prior['alpha']

    def update(self, ctx, time_step, is_fs, prev, curr):
        """Perform a single time-step.

        :param ctx: The simulation context.
        :param time_step: The time-step details.
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        """
        # Update parameters and lookup tables that are defined in self.init()
        # and which will not exist if we are resuming from a cached state.
        self.popn_size = ctx.settings['model']['population_size']

        # Extract each parameter.
        R0 = prev['R0'].copy()
        sigma = prev['sigma'].copy()
        gamma = prev['gamma'].copy()
        eta = prev['eta'].copy()
        alpha = prev['alpha'].copy()
        t0 = prev['t0'].copy()

        beta = R0 * gamma

        forcing_table = ctx.component['lookup'].get('R0_forcing')
        if forcing_table is not None:
            # Modulate the force of infection with temporal forcing.
            force = forcing_table.lookup(time_step.end)
            # Ensure the force of infection is non-negative (can be zero).
            beta *= np.maximum(1.0 + alpha * force, 0)

        epoch = ctx.settings['time']['epoch']
        epoch = ctx.component['time'].to_scalar(epoch)
        curr_t = ctx.component['time'].to_scalar(time_step.end)
        zero_mask = t0 > (curr_t - epoch)
        R0[zero_mask] = 0
        sigma[zero_mask] = 0
        gamma[zero_mask] = 0
        eta[zero_mask] = 0
        alpha[zero_mask] = 0
        t0[zero_mask] = 0
        beta[zero_mask] = 0

        # Extract each compartment.
        S = prev['S']
        E1 = prev['E1']
        E2 = prev['E2']
        I1 = prev['I1']
        I2 = prev['I2']

        # Calculate flows between compartments.
        dt = time_step.dt
        s_to_e1 = dt * beta * (I1 + I2) * S**eta
        e1_to_e2 = dt * 2 * sigma * E1
        e2_to_i1 = dt * 2 * sigma * E2
        i1_to_i2 = dt * 2 * gamma * I1
        i2_to_r = dt * 2 * gamma * I2

        # Update the compartment values.
        curr['S'] = S - s_to_e1
        curr['E1'] = E1 + s_to_e1 - e1_to_e2
        curr['E2'] = E2 + e1_to_e2 - e2_to_i1
        curr['I1'] = I1 + e2_to_i1 - i1_to_i2
        curr['I2'] = I2 + i1_to_i2 - i2_to_r

        # Enforce invariants on the S, E, and I compartments.
        cols_SEI = ['S', 'E1', 'E2', 'I1', 'I2']
        for col in cols_SEI:
            curr[col] = np.clip(curr[col], 0, 1)
        sum_SEI = (
            curr['S'] + curr['E1'] + curr['E2'] + curr['I1'] + curr['I2']
        )
        mask_invalid = sum_SEI > 1
        if np.any(mask_invalid):
            denom = sum_SEI[mask_invalid]
            for col in cols_SEI:
                curr[col][mask_invalid] = curr[col][mask_invalid] / denom
            # Update the net non-R population.
            sum_SEI = (
                curr['S'] + curr['E1'] + curr['E2'] + curr['I1'] + curr['I2']
            )

        # Calculate the size of the R compartment and clip appropriately.
        curr['R'] = np.clip(1.0 - sum_SEI, 0.0, 1.0)

        # Keep parameters fixed.
        param_cols = ['R0', 'sigma', 'gamma', 'eta', 'alpha', 't0']
        curr[param_cols] = prev[param_cols]

    def pr_inf(self, prev, curr):
        """Calculate the likelihood of an individual becoming infected, for
        any number of state vectors.

        :param prev: The model states at the start of the observation period.
        :param curr: The model states at the end of the observation period.
        """
        # Count the number of susceptible / exposed individuals at both ends
        # of the simulation period.
        prev_amt = prev['S'] + prev['E1'] + prev['E2'] + prev['I1']
        curr_amt = curr['S'] + curr['E1'] + curr['E2'] + curr['I1']
        # Avoid returning very small negative values (e.g., -1e-10).
        return np.maximum(prev_amt - curr_amt, 0)

    def is_seeded(self, hist):
        """Identify state vectors where infections have occurred.

        :param hist: A matrix of arbitrary dimensions, whose final dimension
            covers the model state space (i.e., has a length no smaller than
            that returned by :py:func:`state_size`).
        :type hist: numpy.ndarray

        :returns: A matrix of one fewer dimensions than ``hist`` that contains
            ``1`` for state vectors where infections have occurred and ``0``
            for state vectors where they have not.
        :rtype: numpy.ndarray
        """
        initial_exposures = 1.0 / self.popn_size
        initial_S = 1 - initial_exposures
        return np.ceil(hist['S'] < initial_S)

    def is_valid(self, hist):
        """Ignore state vectors where no infections have occurred, as their
        properties (such as parameter distributions) are uninformative."""
        return self.is_seeded(hist)

    def stat_info(self):
        """Return the details of each statistic that can be calculated by this
        model. Each such statistic is represented as a ``(name, stat_fn)``
        pair, where ``name`` is a string that identifies the statistic and
        ``stat_fn`` is a function that calculates the statistic (see, e.g.,
        :py:func:`stat_Reff`).
        """
        return [('Reff', self.stat_Reff)]

    def stat_Reff(self, hist):
        """Calculate the effective reproduction number :math:`R_\\mathrm{eff}`
        for every particle.

        :param hist: The particle history matrix, or a subset thereof.
        """
        return hist['S'] * hist['R0']


class NoEpidemic(Model):
    """
    A model that assumes there will be no epidemic activity.

    This may be a useful hypothesis against which to evaluate other models.
    """

    def init(self, ctx, vec):
        pass

    def update(self, params, time_step, is_fs, prev, curr):
        pass

    def field_types(self, ctx):
        return []

    def can_smooth(self):
        return {}

    def population_size(self):
        return 0

    def pr_inf(self, prev, curr):
        return np.zeros(curr.shape, dtype=np.float64)

    def is_seeded(self, hist):
        return np.ones(hist[..., 0].shape)
