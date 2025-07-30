import logging
import numpy as np

import pypfilt.build
import pypfilt.cache
import pypfilt.obs
import pypfilt.resample
import pypfilt.stats as stats
import pypfilt.summary
from pypfilt.io import string_field, time_field
from pypfilt.summary import Table, Monitor


class PrOutbreak(Table):
    """
    Record the daily outbreak probability, defined as the sum of the weights
    of all particles in which an outbreak has been seeded.

    .. code-block:: toml

       [summary.tables]
       pr_outbreak.component = "epifx.summary.PrOutbreak"
    """

    def field_types(self, ctx, obs_list, name):
        self.__model = ctx.component['model']
        self.__time = ctx.component['time']
        time = time_field('time')
        return [time, ('pr', np.float64)]

    def n_rows(self, ctx, forecasting):
        return ctx.summary_count()

    def add_rows(self, ctx, fs_time, window, insert_fn):
        for snapshot in window:
            mask = self.__model.is_seeded(snapshot.state_vec)
            seeded_weights = snapshot.weights * mask
            insert_fn((snapshot.time, np.sum(seeded_weights)))


class PeakMonitor(Monitor):
    """
    Record epidemic peak forecasts, for use with other statistics.

    .. code-block:: toml

       [summary.monitors]
       peak_monitor.component = "epifx.summary.PeakMonitor"
    """

    peak_size = None
    """
    A dictionary that maps observation systems to the size of each particle's
    peak with respect to that system: ``peak_size[unit]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    peak_date = None
    """
    A dictionary that maps observation systems to the date of each particle's
    peak with respect to that system: ``peak_date[unit]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    peak_time = None
    """
    A dictionary that maps observation systems to the time of each particle's
    peak with respect to that system, measured in (fractional) days from the
    start of the forecasting period: ``peak_time[unit]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    peak_weight = None
    """
    A dictionary that maps observation systems to the weight of each
    particle at the time that its peak occurs:
    ``peak_weight[unit]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    expected_obs = None
    """
    The expected observation for each particle for the duration of the
    **current simulation window**.

    Note that this is **only** valid for tables to inspect in each call to
    ``add_rows()``, and **not** in a call to ``finished()``.
    """

    def __init__(self):
        self.__run = None
        self.__loaded_from_cache = False

    def prepare(self, ctx, obs_list, name):
        self.__obs_units = sorted(ctx.component['obs'].keys())
        # NOTE: we must reset all simulation-specific variables, because the
        # monitor may be used for multiple simulations (e.g., epifx.select).
        self.__run = None
        self.__loaded_from_cache = False
        self.peak_size = None
        self.peak_time = None
        self.peak_date = None
        self.peak_weight = None
        self.expected_obs = None

    def begin_sim(self, ctx, forecasting):
        logger = logging.getLogger(__name__)
        time_scale = ctx.component['time']
        start_time = ctx.start_time()
        end_time = ctx.end_time()
        if self.__run is None or self.__run != (start_time, end_time):
            # For each particle, record the weight and peak time.
            num_px = ctx.settings['filter']['particles']
            self.__run = (start_time, end_time)
            if self.__loaded_from_cache:
                logger.debug('Using cached monitor state')
                self.__loaded_from_cache = False
                # Adjust the cached peak_time data now that the simulation
                # start time is known.
                dt = time_scale.to_scalar(start_time) - time_scale.to_scalar(
                    self.__loaded_from_time
                )
                logger.debug('Adjusting peak_time by {} days'.format(dt))
                for k, v in self.peak_time.items():
                    self.peak_time[k] = v - dt
                return
            logger.debug('Initialising monitor state')
            self.peak_size = {k: np.zeros(num_px) for k in self.__obs_units}
            self.peak_time = {k: np.zeros(num_px) for k in self.__obs_units}
            self.peak_date = {
                k: np.empty(num_px, dtype='O') for k in self.__obs_units
            }
            self.peak_weight = {k: np.zeros(num_px) for k in self.__obs_units}
        elif self.__run is not None and self.__run == (start_time, end_time):
            logger.debug('Ignoring monitor state')
        else:
            logger.debug('Deleting monitor state')
            self.__run = None
            self.peak_size = None
            self.peak_time = None
            self.peak_date = None
            self.peak_weight = None

    def end_sim(self, ctx, fs_time, window):
        self.expected_obs = None

    def days_to(self, ctx, time):
        """
        Convert a time to the (fractional) number of days from the start of
        the forecasting period.

        :param ctx: The simulation context.
        :param time: The time to convert into a scalar value.
        """
        time_scale = ctx.component['time']
        return time_scale.to_scalar(time)

    def monitor(self, ctx, fs_time, window):
        """Record the peak for each particle during a forecasting run."""
        # Do nothing more if there are no times to summarise.
        num_times = len(window)
        if num_times == 0:
            return

        # Resampling can change the particle order, so we need to iterate over
        # the particle chronologically, and reorder the arrays whenever
        # resampling occurs.
        for snapshot in window:
            prev_ixs = snapshot.vec['prev_ix']
            resampled = not np.all(np.diff(prev_ixs) == 1)
            if resampled:
                # Particles were resampled at this time.
                # Adjust the arrays to reflect the new particle ordering.
                for k in self.__obs_units:
                    self.peak_weight[k] = self.peak_weight[k][prev_ixs]
                    self.peak_size[k] = self.peak_size[k][prev_ixs]
                    self.peak_date[k] = self.peak_date[k][prev_ixs]
                    self.peak_time[k] = self.peak_time[k][prev_ixs]

            # Record the expected observations.
            for unit in self.__obs_units:
                obs_model = ctx.component['obs'][unit]
                values = obs_model.expect(ctx, snapshot)
                # Update the recorded peaks where appropriate.
                mask = values > self.peak_size[unit]
                self.peak_size[unit][mask] = values[mask]
                self.peak_date[unit][mask] = snapshot.time
                self.peak_time[unit][mask] = self.days_to(ctx, snapshot.time)

        # Record the *final* weights.
        for k in self.__obs_units:
            self.peak_weight[k] = window[-1].weights

    def load_state(self, ctx, grp):
        """Load the monitor state for disk."""
        logger = logging.getLogger(__name__)
        logger.debug(
            "{}.load_state('{}')".format(self.__class__.__name__, grp.name)
        )
        # Record the start time used in the cached simulation, as this defines
        # the origin for the peak_time values.
        time_scale = ctx.component['time']
        start_time_enc = grp['start_time'][()]
        self.__loaded_from_time = time_scale.from_dtype(start_time_enc[0])
        # Initialise the data structures.
        self.peak_weight = {}
        self.peak_size = {}
        self.peak_time = {}
        self.peak_date = {}
        # Load the cached state for each observation type.
        for unit in self.__obs_units:
            logger.debug("Loading sub-group '{}'".format(unit))
            sub_grp = grp[unit]
            self.peak_weight[unit] = sub_grp['peak_weight'][()]
            self.peak_size[unit] = sub_grp['peak_size'][()]
            self.peak_time[unit] = sub_grp['peak_time'][()]
            peak_date = sub_grp['peak_date'][()]
            self.peak_date[unit] = np.array(
                [time_scale.from_dtype(d) for d in peak_date]
            )
        # Indicate that the monitor state has been loaded from a cache file,
        # and that the peak_time data needs to be adjusted once the simulation
        # start time is known.
        self.__loaded_from_cache = True

    def save_state(self, ctx, grp):
        """Save the monitor state to disk."""
        logger = logging.getLogger(__name__)
        logger.debug(
            "{}.save_state('{}')".format(self.__class__.__name__, grp.name)
        )
        # Save the start time, as this is the origin for the peak_time values.
        time_scale = ctx.component['time']
        start_time_enc = np.array([time_scale.to_dtype(self.__run[0])])
        if 'start_time' in grp:
            # Delete existing data sets, in case they differ in size or type.
            del grp['start_time']
        grp.create_dataset('start_time', data=start_time_enc)
        data_sets = ['peak_weight', 'peak_size', 'peak_time', 'peak_date']
        for unit in self.__obs_units:
            logger.debug("Saving sub-group '{}'".format(unit))
            sub_grp = grp.require_group(unit)
            # Delete existing data sets, in case they differ in size or type.
            for ds in data_sets:
                if ds in sub_grp:
                    del sub_grp[ds]
            peak_date = np.array(
                [time_scale.to_dtype(d) for d in self.peak_date[unit]]
            )
            sub_grp.create_dataset('peak_weight', data=self.peak_weight[unit])
            sub_grp.create_dataset('peak_size', data=self.peak_size[unit])
            sub_grp.create_dataset('peak_time', data=self.peak_time[unit])
            sub_grp.create_dataset('peak_date', data=peak_date)


class ThresholdMonitor(Monitor):
    """
    Monitor when expected observations exceed a specific threshold.

    The threshold should be specified in the simulation settings.
    For example:

    .. code-block:: toml

       [summary.monitors]
       thresh_500.component = "epifx.summary.ThresholdMonitor"
       thresh_500.threshold = 500
    """

    exceed_time = None
    """
    A dictionary that maps observation systems to the time when each particle
    exceeded the specific threshold: ``exceed_time[unit]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    exceed_weight = None
    """
    A dictionary that maps observation systems to the **final** weight of each
    particle: ``exceed_weight``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    exceed_mask = None
    """
    A dictionary that maps observation systems to Boolean arrays that indicate
    which particles have exceeded the threshold:
    ``exceed_mask[unit]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    def __init__(self):
        self.__threshold = None
        self.__run = None
        self.__loaded_from_cache = False

    def prepare(self, ctx, obs_list, name):
        threshold = ctx.get_setting(
            ['summary', 'monitors', name, 'threshold'], self.__threshold
        )
        if threshold is None:
            msg_fmt = 'Monitor {} has no threshold'
            raise ValueError(msg_fmt.format(name))
        self.__threshold = threshold
        self.__obs_units = sorted(ctx.component['obs'].keys())
        # NOTE: we must reset all simulation-specific variables, because the
        # monitor may be used for multiple simulations (e.g., epifx.select).
        self.__run = None
        self.__loaded_from_cache = False
        self.exceed_time = None
        self.exceed_weight = None
        self.exceed_mask = None

    def begin_sim(self, ctx, forecasting):
        logger = logging.getLogger(__name__)
        start_time = ctx.start_time()
        end_time = ctx.end_time()
        if self.__run is None or self.__run != (start_time, end_time):
            # For each particle, record the weight, whether it exceeded the
            # threshold and, if so, when that occurred .
            num_px = ctx.settings['filter']['particles']
            self.__run = (start_time, end_time)
            if self.__loaded_from_cache:
                logger.debug('Using cached monitor state')
                self.__loaded_from_cache = False
                return
            logger.debug('Initialising monitor state')
            # Note: ensure that exceed_time always contains values that can be
            # successfully (de)serialised by the appropriate time scale.
            native = ctx.component['time'].native_dtype()
            self.exceed_time = {
                k: np.full(num_px, start_time, dtype=native)
                for k in self.__obs_units
            }
            self.exceed_weight = np.zeros(num_px)
            self.exceed_mask = {
                k: np.zeros(num_px, dtype=bool) for k in self.__obs_units
            }
        elif self.__run is not None and self.__run == (start_time, end_time):
            logger.debug('Ignoring monitor state')
        else:
            logger.debug('Deleting monitor state')
            self.__run = None
            self.exceed_time = None
            self.exceed_weight = None
            self.exceed_mask = None

    def monitor(self, ctx, fs_time, window):
        """Record the peak for each particle during a forecasting run."""
        # Do nothing more if there are no time to summarise.
        num_times = len(window)
        if num_times == 0:
            return

        # Resampling can change the particle order, so we need to iterate over
        # the particles chronologically, and reorder the arrays whenever
        # resampling occurs.
        for snapshot in window:
            prev_ixs = snapshot.vec['prev_ix']
            resampled = not np.all(np.diff(prev_ixs) == 1)
            if resampled:
                # Particles were resampled at this time.
                # Adjust the arrays to reflect the new particle ordering.
                self.exceed_weight = self.exceed_weight[prev_ixs]
                for k in self.__obs_units:
                    self.exceed_time[k] = self.exceed_time[k][prev_ixs]
                    self.exceed_mask[k] = self.exceed_mask[k][prev_ixs]

            # Calculate the expected observations for each particle.
            for unit in self.__obs_units:
                values = pypfilt.obs.expect(ctx, snapshot, unit)
                # Identify where the threshold has been exceeded for the first
                # time.
                mask = np.logical_and(
                    values > self.__threshold, ~self.exceed_mask[unit]
                )
                self.exceed_time[unit][mask] = snapshot.time
                self.exceed_mask[unit][mask] = True

        # Record the *final* weights.
        self.exceed_weight[:] = window[-1].weights

    def load_state(self, ctx, grp):
        """Load the monitor state for disk."""
        logger = logging.getLogger(__name__)
        logger.debug(
            "{}.load_state('{}')".format(self.__class__.__name__, grp.name)
        )
        time_scale = ctx.component['time']
        # Initialise the data structures.
        self.exceed_weight = grp['exceed_weight'][()]
        self.exceed_time = {}
        self.exceed_mask = {}
        native = ctx.component['time'].native_dtype()
        # Load the cached state for each observation type.
        for unit in self.__obs_units:
            logger.debug("Loading sub-group '{}'".format(unit))
            sub_grp = grp[unit]
            exceed_time = sub_grp['exceed_time'][()]
            self.exceed_time[unit] = np.array(
                [time_scale.from_dtype(d) for d in exceed_time], dtype=native
            )
            self.exceed_mask[unit] = sub_grp['exceed_mask'][()]
        # Indicate that the monitor state has been loaded from a cache file,
        # and that the peak_time data needs to be adjusted once the simulation
        # start time is known.
        self.__loaded_from_cache = True

    def save_state(self, ctx, grp):
        """Save the monitor state to disk."""
        logger = logging.getLogger(__name__)
        logger.debug(
            "{}.save_state('{}')".format(self.__class__.__name__, grp.name)
        )
        time_scale = ctx.component['time']
        if 'exceed_weight' in grp:
            del grp['exceed_weight']
        grp.create_dataset('exceed_weight', data=self.exceed_weight)
        data_sets = ['exceed_time', 'exceed_mask']
        # Note that time.dtype(...) returns a ``(name, type)`` tuple.
        time_dtype = ctx.component['time'].dtype('ignored')[1]
        for unit in self.__obs_units:
            logger.debug("Saving sub-group '{}'".format(unit))
            sub_grp = grp.require_group(unit)
            # Delete existing data sets, in case they differ in size or type.
            for ds in data_sets:
                if ds in sub_grp:
                    del sub_grp[ds]
            exceed_time = np.array(
                [time_scale.to_dtype(d) for d in self.exceed_time[unit]],
                dtype=time_dtype,
            )
            sub_grp.create_dataset('exceed_time', data=exceed_time)
            sub_grp.create_dataset('exceed_mask', data=self.exceed_mask[unit])


class ExceedThreshold(Table):
    """
    Record when expected observations exceed a specific threshold.

    The simulation is divided into a finite number of bins, and this table
    will record the (weighted) proportion of particles that first exceeded the
    threshold in each of these bins.

    This requires a :class:`ThresholdMonitor`, which should be specified in
    the scenario settings.
    It also requires values for the following settings:

    * ``threshold_monitor``: the name of the :class:`ThresholdMonitor`.
    * ``only_forecasts``: whether to record results only during forecasts.
    * ``start``: the time at which to begin recording events.
    * ``until``: the time at which to stop recording events.
    * ``bin_width``: the width of the time bins.

    For example:

    .. code-block:: toml

       [summary.monitors]
       thresh_500.component = "epifx.summary.ThresholdMonitor"
       thresh_500.threshold = 500

       [summary.tables]
       exceed_500.component = "epifx.summary.ExceedThreshold"
       exceed_500.threshold_monitor = "thresh_500"
       exceed_500.only_forecasts = true
       exceed_500.start = "2014-04-01"
       exceed_500.until = "2014-10-01"
       exceed_500.bin_width = 7
    """

    def __define_bins(self, ctx, start, until, bin_width):
        """
        Divide the time scale into a finite number of bins.

        This table will record the (weighted) proportion of particles that
        first exceeded the threshold in each of these bins.
        Note that the bins **must** be defined before this table can be used.

        :param ctx: The simulation context.
        :param start: The time that marks the start of the first bin.
        :param until: The time that marks the end of the last bin.
        :param bin_width: The **scalar** bin width.
        """
        self.__bins = []
        time_scale = ctx.component['time']

        bin_start = start
        while bin_start < until:
            bin_end = time_scale.add_scalar(bin_start, bin_width)
            self.__bins.append((bin_start, bin_end))
            bin_start = bin_end

    def __apply_settings(self, ctx, name):
        self.__monitor_name = ctx.get_setting(
            ['summary', 'tables', name, 'threshold_monitor']
        )
        self.__fs_only = ctx.get_setting(
            ['summary', 'tables', name, 'only_forecasts'], False
        )
        # NOTE: may need to parse the time values.
        self.__start = ctx.get_setting(
            ['summary', 'tables', name, 'start'],
            ctx.settings['time']['start'],
        )
        if isinstance(self.__start, str):
            self.__start = ctx.component['time'].from_unicode(self.__start)
        self.__until = ctx.get_setting(
            ['summary', 'tables', name, 'until'],
            ctx.settings['time']['until'],
        )
        if isinstance(self.__until, str):
            self.__until = ctx.component['time'].from_unicode(self.__until)
        self.__width = ctx.get_setting(
            ['summary', 'tables', name, 'bin_width']
        )

        # Ensure all required settings were specified.
        if self.__monitor_name is None:
            msg_fmt = 'Table {} has no threshold_monitor'
            raise ValueError(msg_fmt.format(name))
        if self.__start is None:
            msg_fmt = 'Table {} has no start'
            raise ValueError(msg_fmt.format(name))
        if self.__until is None:
            msg_fmt = 'Table {} has no until'
            raise ValueError(msg_fmt.format(name))
        if self.__width is None:
            msg_fmt = 'Table {} has no bin_width'
            raise ValueError(msg_fmt.format(name))

    def field_types(self, ctx, obs_list, name):
        self.__apply_settings(ctx, name)
        self.__define_bins(ctx, self.__start, self.__until, self.__width)
        self.__monitor = ctx.component['summary_monitor'][self.__monitor_name]
        self.__all_obs = obs_list
        self.__obs_units = sorted(ctx.component['obs'].keys())
        unit = string_field('unit')
        fs_time = time_field('fs_time')
        week_start = time_field('week_start')
        prob = ('prob', np.float64)
        return [unit, fs_time, week_start, prob]

    def n_rows(self, ctx, forecasting):
        if self.__bins is None:
            raise ValueError('The week bins have not been defined')
        if forecasting or not self.__fs_only:
            self.__end_time = ctx.end_time()
            n_obs_models = len(ctx.component['obs'])
            return len(self.__bins) * n_obs_models
        else:
            self.__end_time = None
            return 0

    def add_rows(self, ctx, fs_time, window, insert_fn):
        pass

    def finished(self, ctx, fs_time, window, insert_fn):
        for unit in self.__obs_units:
            times = self.__monitor.exceed_time[unit]
            exceed_mask = self.__monitor.exceed_mask[unit]
            times[~exceed_mask] = self.__end_time
            weights = self.__monitor.exceed_weight
            for bin_start, bin_end in self.__bins:
                mask = (times >= bin_start) & (times < bin_end) & exceed_mask
                prob = np.sum(weights[mask])
                row = (unit, fs_time, bin_start, prob)
                insert_fn(row)


class PeakForecastEnsembles(Table):
    """
    Record the weighted ensemble of peak size and time predictions for each
    forecasting simulation.

    This requires a :class:`PeakMonitor`, which should be specified in the
    scenario settings.
    It also requires values for the following settings:

    * ``peak_monitor``: the name of the :class:`PeakMonitor`.
    * ``only_forecasts``: whether to record results only during forecasts.

    For example:

    .. code-block:: toml

       [summary.monitors]
       peak_monitor.component = "epifx.summary.PeakMonitor"

       [summary.tables]
       peak_ensemble.component = "epifx.summary.PeakForecastEnsembles"
       peak_ensemble.peak_monitor = "peak_monitor"
       peak_ensemble.only_forecasts = false
    """

    def __init__(self):
        self.__monitor_name = None
        self.__fs_only = False

    def field_types(self, ctx, obs_list, name):
        self.__monitor_name = ctx.get_setting(
            ['summary', 'tables', name, 'peak_monitor']
        )
        self.__fs_only = ctx.get_setting(
            ['summary', 'tables', name, 'only_forecasts'], False
        )
        if self.__monitor_name is None:
            msg_fmt = 'Table {} has no peak_monitor'
            raise ValueError(msg_fmt.format(name))
        self.__monitor = ctx.component['summary_monitor'][self.__monitor_name]
        self.__all_obs = obs_list
        self.__obs_units = sorted(ctx.component['obs'].keys())
        unit = string_field('unit')
        weight = ('weight', np.float64)
        fs_time = time_field('fs_time')
        time = time_field('time')
        value = ('value', np.float64)
        return [unit, fs_time, weight, time, value]

    def n_rows(self, ctx, forecasting):
        n_obs_models = len(ctx.component['obs'])
        if forecasting:
            return ctx.settings['filter']['particles'] * n_obs_models
        elif self.__fs_only:
            return 0
        else:
            return ctx.settings['filter']['particles'] * n_obs_models

    def add_rows(self, ctx, fs_time, window, insert_fn):
        pass

    def finished(self, ctx, fs_time, window, insert_fn):
        for unit in self.__obs_units:
            # Save the peak time and size ensembles.
            for ix in range(ctx.settings['filter']['particles']):
                pk_date = self.__monitor.peak_date[unit][ix]
                row = (
                    unit,
                    fs_time,
                    self.__monitor.peak_weight[unit][ix],
                    pk_date,
                    self.__monitor.peak_size[unit][ix],
                )
                insert_fn(row)


class PeakForecastCIs(Table):
    """
    Record fixed-probability central credible intervals for the peak size and
    time predictions.

    This requires a :class:`PeakMonitor`, which should be specified in the
    scenario settings.
    It also requires values for the following settings:

    * ``peak_monitor``: the name of the :class:`PeakMonitor`.
    * ``credible_intervals``: the central credible intervals to record; the
      default is ``[0, 50, 60, 70, 80, 90, 95, 99, 100]``.

    For example:

    .. code-block:: toml

       [summary.monitors]
       peak_monitor.component = "epifx.summary.PeakMonitor"

       [summary.tables]
       peak_cints.component = "epifx.summary.PeakForecastCIs"
       peak_cints.peak_monitor = "peak_monitor"
       peak_cints.credible_intervals = [0, 50, 95]
    """

    def __init__(self):
        self.__probs = np.uint8([0, 50, 60, 70, 80, 90, 95, 99, 100])
        self.__monitor_name = None

    def field_types(self, ctx, obs_list, name):
        self.__monitor_name = ctx.get_setting(
            ['summary', 'tables', name, 'peak_monitor']
        )
        if self.__monitor_name is None:
            msg_fmt = 'Table {} has no peak_monitor'
            raise ValueError(msg_fmt.format(name))
        self.__probs = np.uint8(
            ctx.get_setting(
                ['summary', 'tables', name, 'credible_intervals'],
                self.__probs,
            )
        )
        self.__monitor = ctx.component['summary_monitor'][self.__monitor_name]
        self.__all_obs = obs_list
        self.__obs_units = sorted(ctx.component['obs'].keys())
        unit = string_field('unit')
        fs_time = time_field('fs_time')
        prob = ('prob', np.int8)
        s_min = ('sizemin', np.float64)
        s_max = ('sizemax', np.float64)
        t_min = time_field('timemin')
        t_max = time_field('timemax')
        return [unit, fs_time, prob, s_min, s_max, t_min, t_max]

    def n_rows(self, ctx, forecasting):
        if forecasting:
            # Need a row for each interval, for each observation system.
            n_obs_models = len(ctx.component['obs'])
            return len(self.__probs) * n_obs_models
        else:
            return 0

    def add_rows(self, ctx, fs_time, window, insert_fn):
        pass

    def finished(self, ctx, fs_time, window, insert_fn):
        time_scale = ctx.component['time']
        for unit in self.__obs_units:
            # Calculate the confidence intervals for peak time and size.
            sz_ints = stats.cred_wt(
                self.__monitor.peak_size[unit],
                self.__monitor.peak_weight[unit],
                self.__probs,
            )
            tm_ints = stats.cred_wt(
                self.__monitor.peak_time[unit],
                self.__monitor.peak_weight[unit],
                self.__probs,
            )

            # Convert from days after the forecast time to time values.
            def time(days):
                """Convert peak times from days (as measured from the
                forecast time)."""
                return time_scale.add_scalar(fs_time, days)

            for pctl in self.__probs:
                row = (
                    unit,
                    fs_time,
                    pctl,
                    sz_ints[pctl][0],
                    sz_ints[pctl][1],
                    time(tm_ints[pctl][0]),
                    time(tm_ints[pctl][1]),
                )
                insert_fn(row)


class PeakSizeAccuracy(Table):
    """
    Record the accuracy of the peak size predictions against multiple accuracy
    thresholds.

    This requires a :class:`PeakMonitor`, which should be specified in the
    scenario settings.
    It also requires values for the following settings:

    * ``peak_monitor``: the name of the :class:`PeakMonitor`.
    * ``thresholds``: the accuracy thresholds for peak size predictions,
      expressed as percentages of the true size; the default is
      ``[10, 20, 25, 33]``.

    For example:

    .. code-block:: toml

       [summary.monitors]
       peak_monitor.component = "epifx.summary.PeakMonitor"

       [summary.tables]
       peak_size_acc.component = "epifx.summary.PeakSizeAccuracy"
       peak_size_acc.peak_monitor = "peak_monitor"
       peak_size_acc.thresholds = [10, 20, 25, 33]
    """

    def __init__(self):
        self.__toln = np.array([10, 20, 25, 33])
        self.__num_toln = len(self.__toln)
        self.__monitor_name = None

    def field_types(self, ctx, obs_list, name):
        self.__monitor_name = ctx.get_setting(
            ['summary', 'tables', name, 'peak_monitor']
        )
        if self.__monitor_name is None:
            msg_fmt = 'Table {} has no peak_monitor'
            raise ValueError(msg_fmt.format(name))
        self.__toln = np.uint8(
            ctx.get_setting(
                ['summary', 'tables', name, 'thresholds'], self.__toln
            )
        )
        self.__num_toln = len(self.__toln)
        self.__monitor = ctx.component['summary_monitor'][self.__monitor_name]
        self.__all_obs = obs_list
        self.__obs_units = sorted(ctx.component['obs'].keys())
        # Identify the peak for each set of observations.
        # NOTE: zero is a valid peak size, it's possible that no cases have
        # been observed.
        peak_obs = {unit: (-1, None) for unit in self.__obs_units}
        for o in obs_list:
            key = o['unit']
            if o['value'] > peak_obs[key][0]:
                peak_obs[key] = (o['value'], o['time'])
        self.__peak_obs = {
            key: (value, time)
            for (key, (value, time)) in peak_obs.items()
            if value >= 0 and time is not None
        }
        if len(self.__peak_obs) == 0:
            raise ValueError('PeakSizeAccuracy: observations are required')
        unit = string_field('unit')
        fs_time = time_field('fs_time')
        toln = ('toln', np.float64)
        acc = ('acc', np.float64)
        var = ('var', np.float64)
        savg = ('avg', np.float64)
        return [unit, fs_time, toln, acc, var, savg]

    def n_rows(self, ctx, forecasting):
        if forecasting:
            return self.__num_toln * len(self.__peak_obs)
        else:
            return 0

    def add_rows(self, ctx, fs_time, window, insert_fn):
        pass

    def finished(self, ctx, fs_time, window, insert_fn):
        obs_peaks = self.__peak_obs

        for unit in self.__obs_units:
            # Summarise the peak size distribution.
            sop_avg, sop_var = stats.avg_var_wt(
                self.__monitor.peak_size[unit],
                self.__monitor.peak_weight[unit],
            )
            # Calculate the relative size of each forecast peak.
            # Avoid dividing by zero if the peak size is zero.
            if obs_peaks[unit][0] > 0:
                sop_rel = self.__monitor.peak_size[unit] / obs_peaks[unit][0]
            else:
                sop_rel = 0

            for pcnt in self.__toln:
                # Sum the weights of the "accurate" particles.
                sop_min, sop_max = 1 - pcnt / 100.0, 1 + pcnt / 100.0
                sop_mask = np.logical_and(
                    sop_rel >= sop_min, sop_rel <= sop_max
                )
                accuracy = np.sum(self.__monitor.peak_weight[unit][sop_mask])
                row = (unit, fs_time, pcnt, accuracy, sop_var, sop_avg)
                insert_fn(row)


class PeakTimeAccuracy(Table):
    """
    Record the accuracy of the peak time predictions against multiple accuracy
    thresholds.

    This requires a :class:`PeakMonitor`, which should be specified in the
    scenario settings.
    It also requires values for the following settings:

    * ``peak_monitor``: the name of the :class:`PeakMonitor`.
    * ``thresholds``: the accuracy thresholds for peak time predictions,
      expressed as numbers of days; the default is ``[7, 10, 14]``.

    For example:

    .. code-block:: toml

       [summary.monitors]
       peak_monitor.component = "epifx.summary.PeakMonitor"

       [summary.tables]
       peak_time_acc.component = "epifx.summary.PeakTimeAccuracy"
       peak_time_acc.peak_monitor = "peak_monitor"
       peak_time_acc.thresholds = [7, 10, 14]
    """

    def __init__(self):
        self.__toln = np.array([7, 10, 14])
        self.__num_toln = len(self.__toln)
        self.__monitor_name = None

    def field_types(self, ctx, obs_list, name):
        self.__monitor_name = ctx.get_setting(
            ['summary', 'tables', name, 'peak_monitor']
        )
        if self.__monitor_name is None:
            msg_fmt = 'Table {} has no peak_monitor'
            raise ValueError(msg_fmt.format(name))
        self.__toln = np.array(
            ctx.get_setting(
                ['summary', 'tables', name, 'thresholds'], self.__toln
            )
        )
        self.__num_toln = len(self.__toln)
        self.__monitor = ctx.component['summary_monitor'][self.__monitor_name]
        self.__all_obs = obs_list
        self.__obs_units = sorted(ctx.component['obs'].keys())
        # Identify the peak for each set of observations.
        peak_obs = {unit: (-1, None) for unit in self.__obs_units}
        for o in obs_list:
            key = o['unit']
            if o['value'] > peak_obs[key][0]:
                peak_obs[key] = (o['value'], o['time'])
        self.__peak_obs = {
            key: (value, time)
            for (key, (value, time)) in peak_obs.items()
            if value >= 0 and time is not None
        }
        if len(self.__peak_obs) == 0:
            raise ValueError('PeakTimeAccuracy: observations are required')
        unit = string_field('unit')
        fs_time = time_field('fs_time')
        toln = ('toln', np.float64)
        acc = ('acc', np.float64)
        var = ('var', np.float64)
        tavg = time_field('avg')
        return [unit, fs_time, toln, acc, var, tavg]

    def n_rows(self, ctx, forecasting):
        if forecasting:
            return self.__num_toln * len(self.__peak_obs)
        else:
            return 0

    def add_rows(self, ctx, fs_time, window, insert_fn):
        pass

    def finished(self, ctx, fs_time, window, insert_fn):
        obs_peaks = self.__peak_obs

        for unit in self.__obs_units:
            top_true = obs_peaks[unit][1]
            dtp_true = self.__monitor.days_to(ctx, top_true)
            # Summarise the peak size distribution.
            dtp_avg, dtp_var = stats.avg_var_wt(
                self.__monitor.peak_time[unit],
                self.__monitor.peak_weight[unit],
            )
            # Convert the mean time of peak to a time value.
            top_avg = ctx.component['time'].add_scalar(fs_time, dtp_avg)

            # Calculate peak time statistics.
            for days in self.__toln:
                # Sum the weights of the "accurate" particles.
                # Note: Shaman et al. defined accuracy as +/- one week.
                dtp_diff = dtp_true - self.__monitor.peak_time[unit]
                dtp_mask = np.fabs(dtp_diff) <= (days + 0.5)
                accuracy = np.sum(self.__monitor.peak_weight[unit][dtp_mask])
                row = (unit, fs_time, days, accuracy, dtp_var, top_avg)
                insert_fn(row)


class ExpectedObs(Table):
    """
    Record fixed-probability central credible intervals for the expected
    observations.

    The default intervals are: 0%, 50%, 90%, 95%, 99%, 100%.
    These can be overridden in the scenario settings.
    For example:

    .. code-block:: toml

       [summary.tables]
       expected_obs.component = "epifx.summary.ExpectedObs"
       expected_obs.credible_intervals = [0, 50, 95]
    """

    def __init__(self):
        self.__probs = np.uint8([0, 50, 90, 95, 99, 100])

    def field_types(self, ctx, obs_list, name):
        self.__probs = np.array(
            ctx.get_setting(
                ['summary', 'tables', name, 'credible_intervals'],
                self.__probs,
            )
        )
        self.__obs_units = sorted(ctx.component['obs'].keys())
        unit = string_field('unit')
        fs_time = time_field('fs_time')
        time = time_field('time')
        prob = ('prob', np.int8)
        ymin = ('ymin', np.float64)
        ymax = ('ymax', np.float64)
        return [unit, fs_time, time, prob, ymin, ymax]

    def n_rows(self, ctx, forecasting):
        # Need a row for each interval, for each day, for each data source.
        n_obs_models = len(ctx.component['obs'])
        n_times = ctx.summary_count()
        return n_times * len(self.__probs) * n_obs_models

    def add_rows(self, ctx, fs_time, window, insert_fn):
        for unit in self.__obs_units:
            obs_model = ctx.component['obs'][unit]

            for snapshot in window:
                expected = obs_model.expect(ctx, snapshot)
                cinfs = stats.cred_wt(
                    expected, snapshot.weights, self.__probs
                )
                for pctl in self.__probs:
                    row = (
                        unit,
                        fs_time,
                        snapshot.time,
                        pctl,
                        cinfs[pctl][0],
                        cinfs[pctl][1],
                    )
                    insert_fn(row)


class ObsLikelihood(Table):
    """
    Record the likelihood of each observation according to each particle.

    This table registers its ``record_obs_llhd`` method as a handler for the
    ``'obs_llhd'`` event so that it can record the observation likelihoods.

    .. note:: Each observation must have a ``'value'`` field that contains a
       numeric scalar value, or this table will raise an exception.

    .. code-block:: toml

       [summary.tables]
       obs_llhd.component = "epifx.summary.ObsLikelihood"
    """

    def __init__(self):
        self.__fs_time = None

    def load_state(self, ctx, group):
        """Restore the state of each PRNG from the cache."""
        pypfilt.cache.load_rng_states(
            group,
            'prng_states',
            {
                'resample': self.__rnd,
            },
        )

    def save_state(self, ctx, group):
        """Save the current state of each PRNG to the cache."""
        pypfilt.cache.save_rng_states(
            group,
            'prng_states',
            {
                'resample': self.__rnd,
            },
        )

    def field_types(self, ctx, obs_list, name):
        seed = ctx.settings['filter'].get('prng_seed')
        self.__rnd = np.random.default_rng(seed)
        # NOTE: `obs_list` is the same as `ctx.all_observations`.
        self.__all_obs = obs_list
        # Build a time-indexed table of observations.
        self.__obs_tbl = {}
        for o in self.__all_obs:
            if o['time'] in self.__obs_tbl:
                self.__obs_tbl[o['time']].append(o)
            else:
                self.__obs_tbl[o['time']] = [o]
        # Ensure the event handler has been installed.
        ctx.install_event_handler('LogLikelihood', self.record_obs_llhd)
        fs_time = time_field('fs_time')
        time = time_field('time')
        value = ('value', np.float64)
        llhd = ('llhd', np.float64)
        std_err = ('std_err', np.float64)
        forecast = ('forecast', np.bool_)
        unit = string_field('unit')
        return [fs_time, unit, time, value, llhd, std_err, forecast]

    def n_rows(self, ctx, forecasting):
        self.__data = []
        self.__forecasting = forecasting
        start_time = ctx.start_time()
        end_time = ctx.end_time()
        self.__start_time = start_time
        if forecasting:
            # Forecasting from the start of the simulation period.
            self.__fs_time = start_time
        else:
            # Not forecasting, so all observations are included.
            self.__fs_time = end_time
        # Need a row for each observation in the simulation period.
        n_rows = len(
            [
                o
                for o in self.__all_obs
                if o['time'] > start_time and o['time'] <= end_time
            ]
        )
        return n_rows

    def add_rows(self, ctx, fs_time, window, insert_fn):
        # Each observation must be considered separately, as they may or may
        # not be used in the filtering process.
        for snapshot in window:
            # Important: ignore the start of the simulation period.
            if snapshot.time <= self.__start_time:
                continue
            # Identify observations for this time that are not being filtered.
            obs = [
                o
                for o in self.__obs_tbl.get(snapshot.time, [])
                if self.__forecasting
            ]
            if obs:
                # This will trigger the record_obs_llhd event handler.
                pypfilt.obs.log_llhd(ctx, snapshot, obs)

    def record_obs_llhd(self, event):
        if self.__fs_time is None:
            # A forecast may be preceded by an estimation run from the most
            # recent known-good state, and we may only be interested in
            # recording summary statistics for the forecasting simulations.
            return
        # NOTE: resample the particles so that weights are uniform.
        (sample_ixs, wt) = pypfilt.resample.resample_weights(
            event.weights, self.__rnd, method='basic'
        )
        # Convert from log likelihoods to likelihoods.
        probs = np.exp(event.log_llhds[sample_ixs])
        # Calculate the mean and standard error.
        pr_mean = np.mean(probs)
        pr_serr = np.var(probs) / wt
        # Generate a corresponding row to record later.
        row = (
            self.__fs_time,
            event.obs['unit'],
            event.obs['time'],
            event.obs['value'],
            pr_mean,
            pr_serr,
            self.__forecasting,
        )
        self.__data.append(row)

    def finished(self, ctx, fs_time, window, insert_fn):
        for row in self.__data:
            insert_fn(row)
        self.__fs_time = None


def make(ctx):
    """
    A convenience function that adds most of the summary statistics defined in
    the ``pypfilt.summary`` and ``epifx.summary`` modules to forecast
    scenarios.

    :param ctx: The simulation context.


    It currently defines the following tables:

    - ``'model_cints'``: ``pypfilt.summary.ModelCIs``;
    - ``'param_covar'``: ``pypfilt.summary.ParamCovar``;
    - ``'forecasts'``: ``pypfilt.summary.PredictiveCIs``;
    - ``'sim_obs'``: ``pypfilt.summary.SimulatedObs`` (see the note below);
    - ``'pr_epi'``: :class:`~epifx.summary.PrOutbreak`;
    - ``'obs_llhd'``: :class:`~epifx.summary.ObsLikelihood`;
    - ``'peak_size_acc'``: :class:`~epifx.summary.PeakSizeAccuracy`;
    - ``'peak_time_acc'``: :class:`~epifx.summary.PeakTimeAccuracy`;
    - ``'peak_cints'``: :class:`~epifx.summary.PeakForecastCIs`;
    - ``'peak_ensemble'``: :class:`~epifx.summary.PeakForecastEnsembles`;

    and the following monitors:

    - ``'peak_monitor'``: :class:`~epifx.summary.PeakMonitor`.

    .. note:: The ``'sim_obs'`` table (``pypfilt.summary.SimulatedObs``) must
       be associated with an observation unit:

       .. code-block:: toml

          [components]
          summary = "epifx.summary.make"

          [summary.tables]
          sim_obs.observation_unit = "cases"
    """

    summary = pypfilt.summary.HDF5(ctx)

    # Add a peak monitor.
    peak_name = 'peak_monitor'
    peak_mon = PeakMonitor()
    ctx.component['summary_monitor'][peak_name] = peak_mon

    tables = {
        'model_cints': pypfilt.summary.ModelCIs(),
        'param_covar': pypfilt.summary.ParamCovar(),
        'pr_epi': PrOutbreak(),
        'forecasts': pypfilt.summary.PredictiveCIs(),
        'obs_llhd': ObsLikelihood(),
        'peak_size_acc': PeakSizeAccuracy(),
        'peak_time_acc': PeakTimeAccuracy(),
        'peak_cints': PeakForecastCIs(),
        'peak_ensemble': PeakForecastEnsembles(),
        'sim_obs': pypfilt.summary.SimulatedObs(),
    }

    peak_ensemble = ['summary', 'tables', 'peak_ensemble']
    ctx.settings.set_chained(peak_ensemble + ['peak_monitor'], peak_name)
    ctx.settings.set_chained(peak_ensemble + ['only_forecasts'], True)

    peak_cints = ['summary', 'tables', 'peak_cints']
    ctx.settings.set_chained(peak_cints + ['peak_monitor'], peak_name)
    ctx.settings.set_chained(
        peak_cints + ['credible_intervals'], [0, 50, 90, 95, 99, 100]
    )

    peak_size_acc = ['summary', 'tables', 'peak_size_acc']
    ctx.settings.set_chained(peak_size_acc + ['peak_monitor'], peak_name)
    ctx.settings.set_chained(peak_size_acc + ['thresholds'], [10, 20, 25, 33])

    peak_time_acc = ['summary', 'tables', 'peak_time_acc']
    ctx.settings.set_chained(peak_time_acc + ['peak_monitor'], peak_name)
    ctx.settings.set_chained(peak_time_acc + ['thresholds'], [7, 10, 14])

    for name, table in tables.items():
        ctx.component['summary_table'][name] = table

    return summary
