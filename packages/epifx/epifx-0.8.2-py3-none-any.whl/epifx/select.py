"""Select particles according to desired target distributions."""

import abc
import epifx.summary
import logging
import numpy as np
from pypfilt.scenario import override_dict
import pypfilt.summary
import scipy.stats


class Target(abc.ABC):
    """The base class for target particle distributions."""

    @abc.abstractmethod
    def define_summary_components(self, instance):
        """
        Add summary monitors and tables so that required summary statistics
        are recorded for each proposed particle.

        :param instance: The simulation instance.
        """
        pass

    @abc.abstractmethod
    def logpdf(self, ctx, result):
        """
        Return the log of the target probability density for each particle.

        :param ctx: The simulation context.
        :param output: The result object returned by ``pypfilt.pfilter.run``;
            summary tables are located at ``output.tables[table_name]``.
        """
        pass


class TargetPeakMVN(Target):
    """A multivariate normal distribution for the peak timing and size."""

    def __init__(self, peak_sizes, peak_times):
        """
        :param peak_sizes: An array of previously-observed peak sizes.
        :param peak_time: An array of previously-observed peak times.
        """
        exp_size = np.mean(peak_sizes)
        std_size = np.std(peak_sizes, ddof=1)
        exp_time = np.mean(peak_times)
        std_time = np.std(peak_times, ddof=1)
        self.pdf_size = scipy.stats.norm(loc=exp_size, scale=std_size)
        self.pdf_time = scipy.stats.norm(loc=exp_time, scale=std_time)
        self.log_p_max = self.pdf_size.logpdf(
            exp_size
        ) + self.pdf_time.logpdf(exp_time)

    def define_summary_components(self, instance):
        # Ensure the summary monitors and summary tables keys exist.
        if 'summary' not in instance.settings:
            instance.settings['summary'] = {}
        if 'monitors' not in instance.settings['summary']:
            instance.settings['summary']['monitors'] = {}
        if 'tables' not in instance.settings['summary']:
            instance.settings['summary']['tables'] = {}

        # Add the necessary monitors and tables.
        instance.settings['summary']['monitors']['peak'] = {
            'component': 'epifx.summary.PeakMonitor',
        }
        instance.settings['summary']['tables']['peak_ensemble'] = {
            'component': 'epifx.summary.PeakForecastEnsembles',
            'peak_monitor': 'peak',
            'only_forecasts': False,
        }

    def logpdf(self, ctx, result):
        logger = logging.getLogger(__name__)
        t = ctx.component['time']
        tbl = result.tables['peak_ensemble']
        size = tbl['value']
        time = np.array([t.to_scalar(d) for d in tbl['time']])
        logger.debug(
            'Peak sizes: {} to {}'.format(np.min(size), np.max(size))
        )
        logger.debug(
            'Peak times: {} to {}'.format(np.min(time), np.max(time))
        )
        log_p_size = self.pdf_size.logpdf(size)
        log_p_time = self.pdf_time.logpdf(time)
        return log_p_size + log_p_time - self.log_p_max


class TargetAny(Target):
    """A distribution that accepts all proposals with equal likelihood."""

    def define_summary_components(self, params):
        peak_mon = epifx.summary.PeakMonitor()

        params['component']['summary_monitor'] = {
            'peak': peak_mon,
        }
        params['component']['summary_table'] = {
            'peak_ensemble': epifx.summary.PeakForecastEnsembles(
                'peak', fs_only=False
            ),
        }

    def logpdf(self, ctx, output):
        return np.zeros(ctx.settings['filter']['particles'])


def select(instance, target, seed, notify_fn=None):
    """
    Select particles according to a target distribution. Proposals will be
    drawn from the model prior distribution.

    :param instance: The simulation instance.
    :param target: The target distribution.
    :param seed: The PRNG seed used for accepting particles.
    :param notify_fn: An optional function that is notified of each acceptance
        loop, and should accept two arguments: the number of particles and the
        number of accepted particles.

    :returns: The initial state vector for each accepted particle.
    :rtype: numpy.ndarray

    .. note:: The ``instance`` **should not be reused** after calling this
        function.
        To prevent this from happening, the instance settings will be deleted.
    """
    logger = logging.getLogger(__name__)

    # Define the required summary monitors and tables.
    target.define_summary_components(instance)

    # Ensure that pypfilt returns the particle history matrices.
    override_dict(
        instance.settings, {'filter': {'results': {'save_history': True}}}
    )

    # Create the simulation context.
    ctx = instance.build_context()

    # Store the prior distribution details so that we can draw new samples.
    prior_table = ctx.prior_table()
    external_samples = ctx.external_prior_samples()

    # Empty instance.settings so that the instance cannot be reused.
    settings_keys = list(instance.settings.keys())
    for key in settings_keys:
        del instance.settings[key]

    # Identify the simulation period.
    start = ctx.settings['time']['start']
    until = ctx.settings['time']['until']

    px_count = ctx.settings['filter']['particles']
    prng = np.random.default_rng(seed)
    saved_hist = None
    saved_ix = 0

    while True:
        # Initialise the summary object.
        ctx.component['summary'].initialise(ctx)
        # Run the estimation pass.
        result = pypfilt.pfilter.run(ctx, start, until, {})

        # Create the history matrix for accepted particles.
        if saved_hist is None:
            # NOTE: must have the same dtype as the history matrix.
            matrix = result.history.matrix
            saved_hist = np.zeros(matrix.shape[1:], dtype=matrix.dtype)
            saved_ix = 0

        # Decide which of the proposed samples to accept.
        log_pr = target.logpdf(ctx, result)
        thresh = prng.uniform(size=px_count)
        accept = np.log(thresh) < log_pr

        # Call the notification function, if provided.
        if notify_fn is not None:
            notify_fn(px_count, np.sum(accept))

        # Log the number of proposed particles that were accepted.
        msg = 'Accept {:5d} of {:5d}'
        logger.debug(msg.format(np.sum(accept), px_count))

        # Record the accepted samples.
        upper_ix = saved_ix + np.sum(accept)
        if upper_ix > px_count:
            # Too many accepted samples, only retain a subset.
            upper_ix = px_count
            num_to_accept = upper_ix - saved_ix
            accept = np.logical_and(
                accept, np.cumsum(accept) <= num_to_accept
            )

        saved_hist[saved_ix:upper_ix] = result.history.matrix[0, accept]
        saved_ix = upper_ix

        if saved_ix >= px_count:
            break

        # Draw new samples from the model prior distribution.
        ctx.data['prior'] = ctx.component['sampler'].draw_samples(
            ctx.settings['sampler'],
            ctx.component['random']['prior'],
            px_count,
            prior_table,
            external_samples,
        )

    # Return the initial state vector of each accepted particle.
    return saved_hist['state_vec']
