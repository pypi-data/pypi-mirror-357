"""Observation models: expected values and log likelihoods."""

import numpy as np
import numpy.lib.recfunctions as np_rec
import pypfilt.obs
import scipy.stats

from pypfilt.io import read_table, time_field, fields_dtype


class SampleFraction(pypfilt.obs.Univariate):
    """
    Generic observation model for relating disease incidence to count data
    where the sample denominator is reported.

    :param obs_unit: A descriptive name for the data.
    :param settings: The observation model settings dictionary.

    The settings dictionary should contain the following keys:

    * ``observation_period``: The observation period (in days).
    * ``denominator``: The denominator to use when generating simulated
      observations.
    * ``k_obs_lookup``: The name of a lookup table for the
      disease-related increase in observation rate
      :math:`\\kappa_\\mathrm{obs}` (default: ``None``).
    * ``k_obs_field``: The name of the state vector field that contains the
      observation rate :math:`\\kappa_\\mathrm{obs}` (default: ``None``).

    .. note:: Do not define both ``k_obs_lookup`` and ``k_obs_field``.

    .. note:: If the ``k_obs_lookup`` table contains more than one value
       column, each particle should be associated with a column by setting
       ``sample_values`` to ``True``:

       .. code-block:: toml

          [scenario.test.lookup_tables]
          k_obs = { file = "k-obs.ssv", sample_values = true }

          [scenario.test.observations.cases]
          model = "epifx.obs.SampleFraction"
          k_obs_lookup = "k_obs"

       If the lookup table contains only one value column, this can be
       omitted:

       .. code-block:: toml

          [scenario.test.lookup_tables]
          k_obs = "k-obs.ssv"

          [scenario.test.observations.cases]
          model = "epifx.obs.SampleFraction"
          k_obs_lookup = "k_obs"
    """

    def __init__(self, obs_unit, settings):
        super().__init__(obs_unit, settings)
        self.period = settings['observation_period']
        self.denom = settings['denominator']
        self.k_obs_lookup = settings.get('k_obs_lookup')
        self.k_obs_field = settings.get('k_obs_field')
        if self.k_obs_lookup is not None and self.k_obs_field is not None:
            msg_fmt = '{}: cannot define k_obs_lookup and k_obs_field'
            raise ValueError(msg_fmt.format(obs_unit))

    def distribution(self, ctx, snapshot):
        """
        Return the case fraction distribution for each particle.
        """
        return self._dist_frac(ctx, snapshot)

    def log_llhd(self, ctx, snapshot, obs):
        """
        Calculate the log-likelihood :math:`\\mathcal{l}(y_t \\mid x_t)` for
        the observation :math:`y_t` (``obs``) and every particle :math:`x_t`.
        """
        num = obs['numerator']
        denom = obs['denominator']
        dist = self._dist_count(ctx, snapshot, denom)
        return dist.logpmf(num)

    def simulate(self, ctx, snapshot, rng):
        """
        Simulate the case fraction with respect to the default denominator.
        """
        dist = self._dist_count(ctx, snapshot, self.denom)
        # NOTE: ensure we always return an array.
        return np.atleast_1d(dist.rvs(random_state=rng)) / self.denom

    def simulated_obs(self, ctx, snapshot, rng):
        fracs = self.simulate(ctx, snapshot, rng)
        return [
            {
                'time': snapshot.time,
                'value': frac,
                'numerator': round(frac * self.denom),
                'denominator': self.denom,
                'unit': self.unit,
            }
            for frac in fracs
        ]

    def simulated_field_types(self, ctx):
        cols = [
            time_field('time'),
            ('numerator', np.int32),
            ('denominator', np.int32),
        ]
        return cols

    def _dist_count(self, ctx, snapshot, denom):
        """
        Return the case count distribution for each particle, for a known
        denominator.
        """
        mean_pr = self._mean(ctx, snapshot)
        op = self.settings['parameters']
        disp = self._disp(mean_pr, op, denom)
        alpha = mean_pr * disp
        beta = (1 - mean_pr) * disp
        return scipy.stats.betabinom(n=denom, a=alpha, b=beta)

    def _dist_frac(self, ctx, snapshot):
        """
        Return the case fraction distribution for each particle.
        """
        mean_pr = self._mean(ctx, snapshot)
        op = self.settings['parameters']
        disp = self._disp(mean_pr, op, self.denom)
        alpha = mean_pr * disp
        beta = (1 - mean_pr) * disp
        return scipy.stats.beta(a=alpha, b=beta)

    def _mean(self, ctx, snapshot):
        """
        Return the expected case proportion.
        """
        op = self.settings['parameters']
        curr = snapshot.vec
        prev = snapshot.back_n_units(self.period)
        pr_inf = ctx.component['model'].pr_inf(
            prev['state_vec'], curr['state_vec']
        )

        if self.k_obs_lookup is not None:
            table = ctx.component['lookup'][self.k_obs_lookup]
            values = table.lookup(snapshot.time)
            if table.value_count() == 1:
                # No need for lookup indices if there is only a single value.
                k_obs = values[0]
            elif 'lookup' not in curr.dtype.names:
                msg_fmt = 'No lookup indices for table {} and {} observations'
                raise ValueError(msg_fmt.format(self.k_obs_lookup, self.unit))
            elif self.k_obs_lookup in curr['lookup'].dtype.names:
                # NOTE: curr['lookup'] may not exist!
                ixs = curr['lookup'][self.k_obs_lookup]
                k_obs = values[ixs]
            else:
                msg_fmt = 'No lookup indices for table {} and {} observations'
                raise ValueError(msg_fmt.format(self.k_obs_lookup, self.unit))
        elif self.k_obs_field is not None:
            k_obs = curr['state_vec'][self.k_obs_field]
        else:
            k_obs = op['k_obs']

        return op['bg_obs'] + pr_inf * k_obs

    def _disp(self, mu, op, denom):
        """
        Return the dispersion parameter for each particle, subject to an
        optional lower bound imposed on the variance.
        """
        disp = op['disp']

        if 'bg_var' in op and op['bg_var'] > 0:
            # Ensure the variance is not smaller than the variance in the
            # background signal.
            disp = op['disp'] * np.ones(mu.shape)
            min_var = op['bg_var']
            frac_var = mu * (1 - mu) * (1 + (denom - 1) / (disp + 1)) / denom
            mask_v = frac_var < min_var
            if np.any(mask_v):
                c = mu[mask_v] * (1 - mu[mask_v]) / denom
                disp[mask_v] = (denom * c - min_var) / (min_var - c)
            else:
                return op['disp']

        return disp

    def from_file(
        self,
        filename,
        time_scale,
        year=None,
        time_col='to',
        value_col='cases',
        denom_col='patients',
    ):
        """
        Load count data from a space-delimited text file with column headers
        defined in the first line.

        Note that returned observation *values* represent the *fraction* of
        patients that were counted as cases, **not** the *absolute number* of
        cases.
        The number of cases and the number of patients are recorded under the
        ``'numerator'`` and ``'denominator'`` keys, respectively.

        :param filename: The file to read.
        :param year: Only returns observations for a specific year.
            The default behaviour is to return all recorded observations.
        :param time_col: The name of the observation time column.
        :param value_col: The name of the observation value column (reported
            as absolute values, **not** fractions).
        :param denom_col: The name of the observation denominator column.
        :return: The observations data table.

        :raises ValueError: If a denominator or value is negative, or if the
            value exceeds the denominator.
        """
        cols = [
            time_scale.column(time_col),
            (value_col, np.int32),
            (denom_col, np.int32),
        ]
        if year is not None:
            year_col = 'year'
            cols.insert(0, (year_col, np.int32))
        df = read_table(filename, cols)

        if year is not None:
            df = df[df[year_col] == year]

        # NOTE: ensure that the data table has the expected column names.
        # This can be done by replacing ``.dtype.names``:
        # https://stackoverflow.com/a/14430013
        rename_to = {
            time_col: 'time',
            value_col: 'numerator',
            denom_col: 'denominator',
        }
        new_names = tuple(
            rename_to.get(name, name) for name in df.dtype.names
        )
        df.dtype.names = new_names

        keep_columns = ['time', 'numerator', 'denominator']
        df = np_rec.repack_fields(df[keep_columns])

        # Perform some basic validation checks.
        if np.any(df['denominator'] < 0):
            raise ValueError('Observation denominator is negative')
        elif np.any(df['numerator'] < 0):
            raise ValueError('Observed value is negative')
        elif np.any(df['numerator'] > df['denominator']):
            raise ValueError('Observed value exceeds denominator')

        fields = [
            time_field('time'),
            ('numerator', np.int32),
            ('denominator', np.int32),
        ]

        return df.astype(fields_dtype(time_scale, fields))

    def row_into_obs(self, row):
        return {
            'time': row['time'],
            'value': row['numerator'] / row['denominator'],
            'numerator': row['numerator'],
            'denominator': row['denominator'],
            'unit': self.unit,
        }

    def obs_into_row(self, obs, dtype):
        return (obs['time'], obs['numerator'], obs['denominator'])


class PopnCounts(pypfilt.obs.Univariate):
    """
    Generic observation model for relating disease incidence to count data
    where the denominator is assumed or known to be the population size.

    :param obs_unit: A descriptive name for the data.
    :param settings: The observation model settings dictionary.

    The settings dictionary should contain the following keys:

    * ``observation_period``: The observation period (in days).
    * ``upper_bound_as_obs``: Treat upper bounds as **point estimates**
      (default: ``False``).
    * ``pr_obs_lookup``: The name of a lookup table for the observation
      probability :math:`p_\\mathrm{obs}` (default: ``None``).
    * ``pr_obs_field``: The name of the state vector field that contains the
      observation probability :math:`p_\\mathrm{obs}` (default: ``None``).

    .. note:: Do not define both ``pr_obs_lookup`` and ``pr_obs_field``.

    .. note:: If the ``pr_obs_lookup`` table contains more than one value
       column, each particle should be associated with a column by setting
       ``sample_values`` to ``True``:

       .. code-block:: toml

          [scenario.test.lookup_tables]
          pr_obs = { file = "pr-obs.ssv", sample_values = true }

          [scenario.test.observations.cases]
          model = "epifx.obs.PopnCounts"
          pr_obs_lookup = "pr_obs"

       If the lookup table contains only one value column, this can be
       omitted:

       .. code-block:: toml

          [scenario.test.lookup_tables]
          pr_obs = "pr-obs.ssv"

          [scenario.test.observations.cases]
          model = "epifx.obs.PopnCounts"
          pr_obs_lookup = "pr_obs"
    """

    def __init__(self, obs_unit, settings):
        super().__init__(obs_unit, settings)
        self.period = settings['observation_period']
        self.upper_bound_as_obs = settings.get('upper_bound_as_obs', False)
        self.pr_obs_lookup = settings.get('pr_obs_lookup')
        self.pr_obs_field = settings.get('pr_obs_field')
        if self.pr_obs_lookup is not None and self.pr_obs_field is not None:
            msg_fmt = '{}: cannot define pr_obs_lookup and pr_obs_field'
            raise ValueError(msg_fmt.format(obs_unit))

    def distribution(self, ctx, snapshot):
        mu = self._mean(ctx, snapshot)
        op = self.settings['parameters']
        nb_k = self._disp(mu, op)
        nb_pr = nb_k / (nb_k + mu)
        return scipy.stats.nbinom(nb_k, nb_pr)

    def _mean(self, ctx, snapshot):
        """
        Return the expected observation for each particle.
        """
        op = self.settings['parameters']
        curr = snapshot.vec
        prev = snapshot.back_n_units(self.period)
        n = ctx.component['model'].population_size()
        pr_inf = ctx.component['model'].pr_inf(
            prev['state_vec'], curr['state_vec']
        )
        if self.pr_obs_lookup is not None:
            table = ctx.component['lookup'][self.pr_obs_lookup]
            values = table.lookup(snapshot.time)
            if table.value_count() == 1:
                # No need for lookup indices if there is only a single value.
                pr_obs = values[0]
            elif 'lookup' not in curr.dtype.names:
                msg = 'No lookup indices for table {} and {} observations'
                raise ValueError(msg.format(self.pr_obs_lookup, self.unit))
            elif self.pr_obs_lookup in curr['lookup'].dtype.names:
                # NOTE: curr['lookup'] may not exist!
                ixs = curr['lookup'][self.pr_obs_lookup]
                pr_obs = values[ixs]
            else:
                msg = 'No lookup indices for table {} and {} observations'
                raise ValueError(msg.format(self.pr_obs_lookup, self.unit))
        elif self.pr_obs_field is not None:
            pr_obs = curr['state_vec'][self.pr_obs_field]
        else:
            pr_obs = op['pr_obs']
        return (1 - pr_inf) * op['bg_obs'] + pr_inf * pr_obs * n

    def _disp(self, mu, op):
        """
        Return the dispersion parameter for each particle, subject to an
        optional lower bound imposed on the variance.
        """
        nb_k = op['disp']

        # Ensure the variance is not smaller than the variance in the
        # background signal.
        if 'bg_var' in op and op['bg_var'] > 0:
            nb_k = op['disp'] * np.ones(mu.shape)
            min_var = op['bg_var']
            nb_var = mu + np.square(mu) / nb_k
            mask_v = nb_var < min_var
            if np.any(mask_v):
                nb_k[mask_v] = np.square(mu[mask_v]) / (min_var - mu[mask_v])

        return nb_k

    def log_llhd(self, ctx, snapshot, obs):
        """
        Calculate the log-likelihood :math:`\\mathcal{l}(y_t \\mid x_t)` for
        the observation :math:`y_t` (``obs``) and every particle :math:`x_t`.

        If it is known (or suspected) that the observed value will increase in
        the future --- when ``obs['incomplete'] == True`` --- then the
        log-likehood :math:`\\mathcal{l}(y > y_t \\mid x_t)` is calculated
        instead (i.e., the log of the *survival function*).

        If an upper bound to this increase is also known (or estimated) ---
        when ``obs['upper_bound']`` is defined --- then the log-likelihood
        :math:`\\mathcal{l}(y_u \\ge y > y_t \\mid x_t)` is calculated
        instead.

        The upper bound can also be treated as a **point estimate** by setting
        ``upper_bound_as_obs = True`` --- then the
        log-likelihood :math:`\\mathcal{l}(y_u \\mid x_t)` is calculated.
        """
        mu = self._mean(ctx, snapshot)
        op = self.settings['parameters']
        nb_k = self._disp(mu, op)
        nb_pr = nb_k / (nb_k + mu)

        # NOTE: scale the probability to account for incomplete detection.
        if 'pr_detect' in obs:
            nb_pr = nb_pr / (nb_pr + obs['pr_detect'] * (1 - nb_pr))

        dist = scipy.stats.nbinom(nb_k, nb_pr)

        if 'incomplete' in obs and obs['incomplete']:
            if 'upper_bound' in obs:
                if self.upper_bound_as_obs:
                    # Return the likelihood of observing the upper bound.
                    return dist.logpmf(obs['upper_bound'])

                # Calculate the likelihood over the interval from the observed
                # value to this upper bound, and return its logarithm.
                cdf_u = dist.cdf(obs['upper_bound'])
                cdf_l = dist.cdf(obs['value'])
                # Handle particles with zero mass in this interval.
                probs = cdf_u - cdf_l
                probs[probs <= 0] = np.finfo(probs.dtype).tiny
                return np.log(probs)
            else:
                # Return the likelihood of observing a strictly greater value
                # than the value reported by this incomplete observation.
                return dist.logsf(obs['value'])

        return dist.logpmf(obs['value'])

    def from_file(
        self,
        filename,
        time_scale,
        year=None,
        time_col='to',
        value_col='count',
        ub_col=None,
        pr_detect_col=None,
    ):
        """
        Load count data from a space-delimited text file with column headers
        defined in the first line.

        :param filename: The file to read.
        :param year: Only returns observations for a specific year.
            The default behaviour is to return all recorded observations.
        :param time_col: The name of the observation time column.
        :param value_col: The name of the observation value column.
        :param ub_col: The name of the estimated upper-bound column, optional.
        :param pr_detect_col: The name of the column that defines a detection
            probability that accounts "incomplete" observations due to, e.g.,
            delays in reporting.
        :return: The observations data table.
        """
        cols = [time_scale.column(time_col), (value_col, np.int32)]
        if year is not None:
            year_col = 'year'
            cols.insert(0, (year_col, np.int32))
        if ub_col is not None:
            cols.append((ub_col, np.int32))
        if pr_detect_col is not None:
            cols.append((pr_detect_col, np.float64))
        df = read_table(filename, cols)

        if year is not None:
            df = df[df[year_col] == year]

        # NOTE: ensure that the data table has the expected column names.
        # This can be done by replacing ``.dtype.names``:
        # https://stackoverflow.com/a/14430013
        rename_to = {
            time_col: 'time',
            value_col: 'value',
            ub_col: 'upper_bound',
            pr_detect_col: 'pr_detect',
        }
        new_names = tuple(
            rename_to.get(name, name) for name in df.dtype.names
        )
        df.dtype.names = new_names

        # NOTE: identify the columns that should be retained.
        keep_columns = ['time', 'value']
        fields = [time_field('time'), ('value', np.int32)]
        if ub_col is not None:
            keep_columns.append('upper_bound')
            fields.append(('upper_bound', np.int32))
        if pr_detect_col is not None:
            keep_columns.append('pr_detect')
            fields.append(('pr_detect', np.float64))
        df = np_rec.repack_fields(df[keep_columns])

        return df.astype(fields_dtype(time_scale, fields))

    def row_into_obs(self, row):
        obs = dict(zip(row.dtype.names, row))
        obs['unit'] = self.unit
        return obs

    def obs_into_row(self, obs, dtype):
        fields = [obs['time'], obs['value']]
        for optional_field in ['upper_bound', 'pr_detect']:
            if optional_field in dtype.names:
                fields.append(obs[optional_field])
        return tuple(fields)
