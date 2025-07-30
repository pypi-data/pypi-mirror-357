"""Stochastic compartmental models."""

import numpy as np
from pypfilt.model import ministeps
from .model import Model


class SEEIIR(Model):
    r"""A stochastic SEEIIR compartment model.

    The mean rates are defined by the following equations:

    .. math::

        \frac{dS}{dt} &= - \beta \frac{S}{N} (I_1 + I_2) \\[0.5em]
        \frac{dE_1}{dt} &= \beta \frac{S}{N} (I_1 + I_2)
          - 2 \sigma E_1 \\[0.5em]
        \frac{dE_2}{dt} &= 2 \sigma E_1 - 2 \sigma E_2 \\[0.5em]
        \frac{dI_1}{dt} &= 2 \sigma E_2 - 2 \gamma I_1 \\[0.5em]
        \frac{dI_2}{dt} &= 2 \gamma I_1 - 2 \gamma I_2 \\[0.5em]
        \frac{dR}{dt} &= 2 \gamma I_2 \\[0.5em]
        \beta &= R_0 \cdot \gamma \\[0.5em]
        E_1(0) &= 10

    ==============  ================================================
    Parameter       Meaning
    ==============  ================================================
    :math:`R_0`     Basic reproduction number
    :math:`\sigma`  Inverse of the incubation period (day :sup:`-1`)
    :math:`\gamma`  Inverse of the infectious period (day :sup:`-1`)
    :math:`t_0`     The time at which the epidemic begins
    ==============  ================================================

    The basic reproduction number :math:`R_0` can be sampled from the lookup
    table ``'R0'``, in which case each particle is associated with a specific
    :math:`R_0` trajectory ``'R0_ix'``.
    In this case, there **must be** prior samples for ``'R0_ix'``.
    Note that this allows :math:`R_0` to vary over time.

    External exposures can be injected into the model from the lookup table
    ``'external_exposures'``.
    These exposures :math:`e_\mathrm{ext}(t)` have the following effect on the
    model equations:

    .. math::

       \frac{dS}{dt} &= - \beta \frac{S}{N} (I_1 + I_2) - e_\mathrm{ext}(t)
       \\[0.5em]
       \frac{dE_1}{dt} &= \beta \frac{S}{N} (I_1 + I_2) + e_\mathrm{ext}(t)
       - 2 \sigma E_1

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
        't0',
        'R0_ix',
        'R0_val',
    ]

    def field_types(self, ctx):
        return [(name, float) for name in self.__fields]

    def can_smooth(self):
        return {'R0', 'sigma', 'gamma', 'R0_ix'}

    def population_size(self):
        return self.popn_size

    def init(self, ctx, vec):
        """Initialise a state vector.

        :param ctx: The simulation context.
        :param vec: An uninitialised state vector of correct dimensions.
        """
        self.popn_size = ctx.settings['model']['population_size']

        prior = ctx.data['prior']
        num_exps = 10
        vec[:] = 0
        vec['S'] = self.popn_size - num_exps
        vec['E1'] = num_exps
        vec['R0'] = prior['R0']
        vec['sigma'] = prior['sigma']
        vec['gamma'] = prior['gamma']
        vec['t0'] = prior['t0']

        # Initialise R0 from the lookup table.
        R0_table = ctx.component['lookup'].get('R0')
        if R0_table is not None:
            R0_ixs = prior['R0_ix']
            when = ctx.settings['time']['start']
            R0_values = R0_table.lookup(when)[R0_ixs]
            vec['R0_ix'] = R0_ixs
            vec['R0_val'] = R0_values

    @ministeps(1)
    def update(self, ctx, time_step, is_fs, prev, curr):
        """Perform a single time-step.

        :param ctx: The simulation context.
        :param time_step: The time-step details.
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        """

        rnd = ctx.component['random']['model']

        # Update parameters and lookup tables that are defined in self.init()
        # and which will not exist if we are resuming from a cached state.
        self.popn_size = ctx.settings['model']['population_size']

        # Extract each parameter.
        R0 = prev['R0'].copy()
        sigma = prev['sigma'].copy()
        gamma = prev['gamma'].copy()
        t0 = prev['t0'].copy()
        R0_ix = np.around(prev['R0_ix']).astype(int)

        R0_table = ctx.component['lookup'].get('R0')
        if R0_table is not None:
            start = ctx.get_setting(['time', 'sim_start'])
            forecast_with_future_R0 = ctx.get_setting(
                ['model', 'forecast_with_future_R0'], False
            )
            if is_fs and not forecast_with_future_R0:
                # NOTE: Forecasting run, only using Reff(forecast_time).
                when = start
            else:
                when = time_step.end
            # Retrieve R0(t) values from the lookup table.
            R0_values = R0_table.lookup(when)
            R0 = R0_values[R0_ix]

        beta = R0 * gamma

        external = np.zeros(beta.shape)
        external_table = ctx.component['lookup'].get('external_exposures')
        if external_table is not None:
            external_values = external_table.lookup(time_step.end)
            n = len(external_values)
            if n == 1:
                external[:] = external_values[0]
            elif n == len(external):
                # NOTE: we currently assume that when there are multiple
                # external exposure trajectories, that the values will only be
                # non-zero in the forecasting period (i.e., there are no more
                # observations, so particles will not be resampled) and we can
                # simply assign the trajectories to each particle in turn.
                external[:] = external_values[:]
            else:
                raise ValueError(
                    'Invalid number of lookup values: {}'.format(n)
                )

        epoch = ctx.settings['time']['epoch']
        epoch = ctx.component['time'].to_scalar(epoch)
        curr_t = ctx.component['time'].to_scalar(time_step.end)
        zero_mask = t0 > (curr_t - epoch)
        R0[zero_mask] = 0
        beta[zero_mask] = 0
        sigma[zero_mask] = 0
        gamma[zero_mask] = 0

        # Extract each compartment.
        S = prev['S'].astype(int)
        E1 = prev['E1'].astype(int)
        E2 = prev['E2'].astype(int)
        I1 = prev['I1'].astype(int)
        I2 = prev['I2'].astype(int)

        # Calculate the rates at which an individual leaves each compartment.
        dt = time_step.dt
        s_out_rate = dt * (beta * (I1 + I2) + external) / self.popn_size
        s_out_rate[S < 1] = 0
        e_out_rate = dt * 2 * sigma
        i_out_rate = dt * 2 * gamma

        # Calculate an individual's probability of leaving each compartment.
        s_out_prob = -np.expm1(-s_out_rate)
        e_out_prob = -np.expm1(-e_out_rate)
        i_out_prob = -np.expm1(-i_out_rate)

        # Sample the outflow rate for each compartment.
        s_out = rnd.binomial(S, s_out_prob)
        e1_out = rnd.binomial(E1, e_out_prob)
        e2_out = rnd.binomial(E2, e_out_prob)
        i1_out = rnd.binomial(I1, i_out_prob)
        i2_out = rnd.binomial(I2, i_out_prob)

        if any(np.isinf(s_out_rate)) or any(np.isinf(s_out_prob)):
            print(
                'S out rate: {} to {}'.format(
                    np.min(s_out_rate), np.max(s_out_rate)
                )
            )
            print(
                'S out prob: {} to {}'.format(
                    np.min(s_out_prob), np.max(s_out_prob)
                )
            )
            print('S: {} to {}'.format(np.min(S), np.max(S)))
            print('S out: {} to {}'.format(np.min(s_out), np.max(s_out)))
            print('when:', when)
            print('dt:', dt)
            print('beta:', np.min(beta), np.max(beta))
            print('R0:', np.min(R0), np.max(R0))
            print('gamma:', np.min(gamma), np.max(gamma))
            print(np.max(dt * (beta * (I1 + I2))))
            print(np.max(dt * external / S))
            print(np.min(dt * (beta * (I1 + I2))))
            print(np.min(dt * external / S))
            raise ValueError('stop')

        # Update the compartment values.
        curr['S'] = S - s_out
        curr['E1'] = E1 + s_out - e1_out
        curr['E2'] = E2 + e1_out - e2_out
        curr['I1'] = I1 + e2_out - i1_out
        curr['I2'] = I2 + i1_out - i2_out

        # Calculate the size of the R compartment and clip appropriately.
        sum_SEI = (
            curr['S'] + curr['E1'] + curr['E2'] + curr['I1'] + curr['I2']
        )
        curr['R'] = np.clip(self.popn_size - sum_SEI, 0.0, self.popn_size)

        # Keep parameters fixed.
        param_cols = ['R0', 'sigma', 'gamma', 't0', 'R0_ix']
        curr[param_cols] = prev[param_cols]
        # Record the R0(t) values for each particle.
        curr['R0_val'] = R0

    def pr_inf(self, prev, curr):
        """
        Return the probability of an individual becoming infected, for any
        number of state vectors.

        :param prev: The model states at the start of the observation period.
        :param curr: The model states at the end of the observation period.
        """
        # Count the number of susceptible / exposed individuals at both ends
        # of the simulation period.
        prev_amt = prev['S'] + prev['E1'] + prev['E2'] + prev['I1']
        curr_amt = curr['S'] + curr['E1'] + curr['E2'] + curr['I1']
        # Avoid returning very small negative values (e.g., -1e-10).
        num_infs = np.maximum(prev_amt - curr_amt, 0)
        return num_infs / self.popn_size

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
        num_exps = 10
        initial_S = self.popn_size - num_exps
        return np.ceil(hist['S'] < initial_S)

    def is_extinct(self, hist):
        """
        Return an array that identifies state vectors where the epidemic has
        become extinct.

        By default, this method returns ``False`` for all particles.
        Stochastic models should override this method.

        :param hist: A matrix of arbitrary dimensions, whose final dimension
            covers the model state space (i.e., has a length no smaller than
            that returned by :py:func:`state_size`).
        :type hist: numpy.ndarray

        :returns: A matrix of one fewer dimensions than ``hist`` that contains
            ``True`` for state vectors where the epidemic is extinct and
            ``False`` for state vectors where the epidemic is ongoing.
        :rtype: numpy.ndarray
        """
        # Count the number of individuals in E1, E2, I1, and I2.
        num_exposed = hist['E1'] + hist['E2'] + hist['I1'] + hist['I2']
        return num_exposed == 0

    def is_valid(self, hist):
        """Ignore state vectors where no infections have occurred, as their
        properties (such as parameter distributions) are uninformative."""
        return self.is_seeded(hist)

    def stat_info(self):
        """
        Return the summary statistics that are provided by this model.

        Each statistic is represented as a ``(name, stat_fn)`` tuple, where
        ``name`` is a string and ``stat_fn`` is a function that accepts one
        argument (the particle history matrix) and returns the statistic (see,
        e.g., :py:func:`stat_generation_interval`).
        """
        return [('gen_int', self.stat_generation_interval)]

    def stat_generation_interval(self, hist):
        """
        Calculate the mean generation interval for each particle.

        :param hist: The particle history matrix, or a subset thereof.
        """
        return 1 / hist['sigma'] + 0.75 / hist['gamma']
