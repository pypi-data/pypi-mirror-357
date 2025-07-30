"""
Run forecasts from a declarative configuration.
"""

import datetime
import logging
import os.path
import parq
import pypfilt

from pathlib import Path

from . import _parser


def get_forecast_dates(all_obs, fs_from, fs_until, settings):
    """
    Return the dates for which forecasts should be generated.

    If no observations are provided, this will return the start of the
    simulation period so that a single estimation pass is performed.

    If ``fs_from`` and ``fs_until`` are both ``None``, only the most recent
    forecasting date will be returned.
    Otherwise, this will return all forecasting dates that are not earlier
    than ``fs_from`` (when specified) and are not later than ``fs_until``
    (when specified).

    :param all_obs: The available observations.
    :type all_obs: List[Dict[str, Any]]
    :param fs_from: The earliest potential forecasting date.
    :type fs_from: Optional[datetime.datetime]
    :param fs_until: The latest potential forecasting date.
    :type fs_until: Optional[datetime.datetime]
    :param settings: The simulation settings.
    """
    # Only consider forecast dates within the simulation period.
    start = settings['time']['start']
    until = settings['time']['until']
    valid_obs = [
        obs for obs in all_obs if obs['time'] >= start and obs['time'] < until
    ]

    # Perform an estimation pass if there are no observations.
    if len(valid_obs) == 0:
        # This might not be the expected outcome, so notify the user.
        logger = logging.getLogger(__name__)
        logger.info('No observations, will perform an estimation pass')
        return [settings['time']['start']]

    fs_times = sorted(obs['time'] for obs in valid_obs)
    if fs_from is None and fs_until is None:
        return [max(fs_times)]
    if fs_from is not None:
        fs_times = [d for d in fs_times if d >= fs_from]
    if fs_until is not None:
        fs_times = [d for d in fs_times if d <= fs_until]
    return fs_times


def run(ctx, forecast_dates, one_file=False, forecast_id=None):
    """
    Run forecast simulations for each forecasting date.

    :param ctx: The simulation context.
    :type ctx: Union[pypfilt.Context, pypfilt.Instance]
    :param forecast_dates: The dates at which to run forecasts.
    :type forecast_dates: List[datetime.datetime]
    :param one_file: Whether to save all forecasts to a single output file.
    :type one_file: bool
    :param forecast_id: An optional identifier for a single forecast, which
        will be used instead of the forecast date in the output file name.
    :type forecast_id: Optional[str]
    :return: The simulation state and forecast output file for each
        forecasting date.
    :rtype: Dict[datetime.datetime, pypfilt.pfilter.Results]
    """
    logger = logging.getLogger(__name__)

    if isinstance(ctx, pypfilt.Context):
        is_instance = False
    elif isinstance(ctx, pypfilt.Instance):
        # NOTE: we want to use a new context for each forecast date.
        # So we construct a constant here, and then construct a new
        # one after each forecast.
        is_instance = True
        instance = ctx
        ctx = instance.build_context()
    else:
        msg_fmt = 'Value of type {} is not a Context or Instance'
        raise ValueError(msg_fmt.format(type(ctx)))

    start = ctx.settings['time']['start']
    until = ctx.settings['time']['until']

    cache_file = filename_for_description(
        ctx.scenario_id, ctx.descriptor, prefix='cache', infix=None
    )
    ctx.settings['files']['cache_file'] = cache_file
    # NOTE: only remove the cache file after all of the forecasts have run.
    remove_after = ctx.settings['files']['delete_cache_file_after_forecast']
    ctx.settings['files']['delete_cache_file_after_forecast'] = False

    # Warn the user about any invalid forecasting dates.
    too_early = [d for d in forecast_dates if d < start]
    if too_early:
        logger.warning(
            'Excluding {} forecast dates prior to {}'.format(
                len(too_early), start
            )
        )
    too_late = [d for d in forecast_dates if d >= until]
    if too_late:
        logger.warning(
            'Excluding {} forecast dates after {}'.format(
                len(too_late), until
            )
        )

    # Determine the valid forecasting dates.
    # Note that this includes the start of the simulation period.
    forecast_dates = [d for d in forecast_dates if d >= start and d < until]

    if one_file:
        if forecast_id is not None:
            msg = 'Cannot use forecast ID for a single output file'
            raise ValueError(msg)

        fs_file = filename_for_description(ctx.scenario_id, ctx.descriptor)
        sim_start = datetime.datetime.now()

        logger.debug(
            'forecast() beginning at {}'.format(
                sim_start.strftime('%H:%M:%S')
            )
        )
        results = pypfilt.forecast(ctx, forecast_dates, filename=fs_file)
        results.metadata['forecast_file'] = fs_file

        # NOTE: remove the cache file after all of the forecasts have run.
        if remove_after:
            # NOTE: remove_cache_file() needs the full path to cache_file.
            cache_path = os.path.join(
                ctx.settings['files']['output_directory'], cache_file
            )
            pypfilt.cache.remove_cache_file(cache_path)

        return results

    # Ensure we only have a single forecast date if a forecast identifier was
    # provided.
    if forecast_id is not None:
        if len(forecast_dates) != 1:
            msg_fmt = 'Can only use forecast ID with 1 forecast date, not {}'
            raise ValueError(msg_fmt.format(len(forecast_dates)))

    # Run each forecast in turn.
    forecast_files = []
    forecast_states = {}
    out_dir = Path(ctx.settings['files']['output_directory'])
    for fs_time in forecast_dates:
        logger.info('Forecasting from {} ...'.format(fs_time))

        if not any(fs_time == o['time'] for o in ctx.all_observations):
            # Warn if are observations have been provided, but there is no
            # observation for the forecasting date itself.
            if len(ctx.all_observations) > 0:
                msg = 'No observation for forecast date {}'
                logger.warning(msg.format(fs_time))
            # NOTE: setting `fs_time` to None has the following effects:
            # 1. The forecast date isn't included in the output file name; and
            # 2. We run pypfilt.fit() instead of pypfilt.forecast().
            fs_time = None

        # NOTE: we don't want to include the time component in filenames, so
        # we have to handle datetime.datetime values as a special case.
        if isinstance(fs_time, datetime.datetime):
            fs_str = str(fs_time.date())
        elif fs_time is None:
            fs_str = None
        else:
            time = ctx.component['time']
            fs_str = time.to_unicode(fs_time)

        # Allow the forecast string to be overridden by the forecast ID.
        if forecast_id is not None:
            fs_str = forecast_id

        # NOTE: no need to add the out_dir prefix.
        fs_file = filename_for_description(
            ctx.scenario_id, ctx.descriptor, infix=fs_str
        )
        forecast_files.append(out_dir / fs_file)
        sim_start = datetime.datetime.now()
        logger.debug(
            'forecast() beginning at {}'.format(
                sim_start.strftime('%H:%M:%S')
            )
        )

        # Record the forecast date identifier in the simulation metadata.
        pypfilt.build.set_chained(
            ctx.settings, ['epifx', 'forecast_id'], fs_str
        )

        if fs_time is None:
            results = pypfilt.fit(ctx, filename=fs_file)
        else:
            results = pypfilt.forecast(ctx, [fs_time], filename=fs_file)
        results.metadata['forecast_file'] = fs_file
        forecast_states[fs_time] = results
        logger.debug(
            'forecast() finishing at {}'.format(
                datetime.datetime.now().strftime('%H:%M:%S')
            )
        )

        if is_instance:
            # NOTE: we create a new context for the next forecast.
            ctx = instance.build_context()

        # NOTE: do not delete the cache file before the subsequent
        # forecast(s), since we treat them as a single forecast.
        ctx.settings['files']['delete_cache_file_before_forecast'] = False
        # NOTE: do not delete the cache file until all forecasts have run.
        ctx.settings['files']['delete_cache_file_after_forecast'] = False

    # NOTE: remove the cache file after all of the forecasts have run.
    if remove_after:
        # NOTE: remove_cache_file() needs the full path to cache_file.
        cache_path = os.path.join(
            ctx.settings['files']['output_directory'], cache_file
        )
        pypfilt.cache.remove_cache_file(cache_path)

    return forecast_states


def run_instance(instance, forecast_from, forecast_until, one_file, fs_id):
    logger = logging.getLogger(__name__)
    logger.info('Running "{}"'.format(instance.scenario_id))
    context = instance.build_context()
    fs_times = get_forecast_dates(
        context.all_observations,
        forecast_from,
        forecast_until,
        context.settings,
    )
    return run(context, fs_times, one_file, forecast_id=fs_id)


def filename_for_description(
    scenario, descr, prefix=None, infix=None, suffix=None, ext=None
):
    if ext is None:
        ext = '.hdf5'

    fields = []
    if prefix is not None and prefix:
        fields.append(prefix)
    fields.append(scenario)
    if infix is not None and infix:
        fields.append(infix)
    if descr is not None and descr:
        fields.append(descr)
    if suffix is not None and suffix:
        fields.append(suffix)
    return '-'.join(fields) + ext


def parser():
    """Return the command-line argument parser for ``epifx-forecast``."""
    parser = _parser.common_parser(scenarios=True, config=True)

    fg = parser.add_argument_group('Forecast settings')

    fg.add_argument(
        '-f', '--from', help='First forecasting date (YYYY-MM-DD)'
    )
    fg.add_argument(
        '-u', '--until', help='Final forecasting date (YYYY-MM-DD)'
    )
    fg.add_argument(
        '-o',
        '--one-output-file',
        action='store_true',
        help='Save all forecasts in a single file',
    )
    fg.add_argument('--id', help='Unique identifier for a single forecast')

    cg = parser.add_argument_group('Computation settings')
    cg.add_argument(
        '--spawn',
        metavar='N',
        type=int,
        default=1,
        help='Spawn N separate processes',
    )
    cg.add_argument(
        '--nice',
        type=int,
        default=5,
        help='Increase the process "niceness" (default: 5)',
    )

    return parser


def parse_date_arg(arg, fmt='%Y-%m-%d'):
    """
    Convert a string argument into a datetime value.
    """
    if arg is None:
        return None
    try:
        return datetime.datetime.strptime(arg, fmt)
    except ValueError as e:
        raise ValueError("Invalid forecast date '{}'".format(arg)) from e


def main(args=None):
    """Generate forecasts from live data."""
    p = parser()
    if args is None:
        args = vars(p.parse_args())
    else:
        args = vars(p.parse_args(args))
    logging.basicConfig(level=args['loglevel'])
    logger = logging.getLogger(__name__)

    if args['config'] is None:
        p.error('must specify at least one configuration file')

    try:
        forecast_from = parse_date_arg(args['from'])
        forecast_until = parse_date_arg(args['until'])
    except ValueError as e:
        p.error(e.args[0])

    forecast_id = args['id']
    scenario_ids = args['scenario']
    one_file = args['one_output_file']

    logger.info('Reading configuration from {}'.format(args['config']))

    instances = list(
        instance
        for instance in pypfilt.load_instances(args['config'])
        if (not scenario_ids) or instance.scenario_id in scenario_ids
    )

    # Warn about scenario IDs that were provided as command-line arguments but
    # were not found in the scenario files.
    if scenario_ids:
        for scenario_id in scenario_ids:
            matches = [
                instance
                for instance in instances
                if instance.scenario_id == scenario_id
            ]
            if len(matches) == 0:
                msg_fmt = 'Could not find scenario "{}"'
                logger.warning(msg_fmt.format(scenario_id))

    n_proc = args['spawn']
    if n_proc < 1:
        p.error('must use at least one process')
    elif n_proc == 1:
        for instance in instances:
            run_instance(
                instance, forecast_from, forecast_until, one_file, forecast_id
            )
        # NOTE: if run() raises an exception the exit status will be non-zero.
        success = True
    else:
        par_instances = (
            (instance, forecast_from, forecast_until, one_file, forecast_id)
            for instance in instances
        )
        success = parq.run(run_instance, par_instances, n_proc)

    # Return whether the forecast simulations completed successfully.
    if success:
        return 0
    else:
        for par_instance in success.unsuccessful_jobs:
            scenario_id = par_instance[0].scenario_id
            logger.error(f'Failed scenario "{scenario_id}"')
        return 1
