"""
Provides a declarative means of defining forecasts.

The purpose of this module is to allow users to define and run forecasting
simulations **without writing any Python code**, by instead defining all of
the necessary settings and parameters in a `TOML`_ file.
"""

import argparse
import logging
from importlib.metadata import version


def common_parser(scenarios, config):
    """A command-line argument parser with common settings."""
    if scenarios:
        usage_str = '%(prog)s [options] FILE [FILE ...]'
    else:
        usage_str = '%(prog)s [options]'

    parser = argparse.ArgumentParser(usage=usage_str, add_help=False)

    h = parser.add_argument_group('Information')
    h.add_argument(
        '-h', '--help', action='help', help='Show this help message'
    )
    h.add_argument(
        '--version',
        action='version',
        version='epifx {}'.format(version('epifx')),
        help='Print the version information and exit.',
    )

    og = parser.add_argument_group('Output options')
    log = og.add_mutually_exclusive_group()
    log.add_argument(
        '-d',
        '--debug',
        action='store_const',
        dest='loglevel',
        help='Enable debugging output',
        const=logging.DEBUG,
        default=logging.INFO,
    )
    log.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        dest='loglevel',
        help='Suppress logging output',
        const=logging.WARNING,
    )

    if config:
        parser.add_argument(
            'config',
            nargs='+',
            metavar='FILE',
            help='Configuration file(s) that define the scenarios',
        )

    if scenarios:
        sg = parser.add_argument_group('Scenario selection')
        sg.add_argument(
            '-s',
            '--scenario',
            metavar='ID',
            action='append',
            help=('Select scenarios by their identifier(s)'),
        )

    return parser
