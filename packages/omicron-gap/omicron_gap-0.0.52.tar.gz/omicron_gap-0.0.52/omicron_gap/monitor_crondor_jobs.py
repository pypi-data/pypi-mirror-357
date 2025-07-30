#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: nu:ai:ts=4:sw=4

#
#  Copyright (C) 2025 Joseph Areeda <joseph.areeda@ligo.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""

Monitor the condor jobs based on the groups in the config file.
We want to make sure that only one online job is running per group or
confirm that no online jobs are running before we start a new one.
"""
import configparser
import time

from omicron import const

start_time = time.time()

import argparse
import logging
from pathlib import Path

import sys
import traceback

import htcondor
import classad

try:
    from ._version import __version__
except ImportError:
    __version__ = '0.0.0'

__author__ = 'joseph areeda'
__email__ = 'joseph.areeda@ligo.org'
__process_name__ = Path(__file__).name

logger = None


def parser_add_args(parser):
    """
    Set up the command parser
    :param argparse.ArgumentParser parser:
    :return: None but the parser object is updated
    """
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='increase verbose output')
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='show only fatal errors')
    parser.add_argument('-f', '--config-file', type=Path,
                        default=const.OMICRON_CHANNELS_FILE,
                        help='Omicron config file')
    parser.add_argument('groups', nargs='*',
                        help='Groups to monitor. Default is all in the config file')


def query_by_name(constraint, schedd=None, projection=["ClusterId", "ProcId", "JobBatchName", "JobStatus"],):
    """
    Query the schedd for the value of a classad attribute
    :param str constraint: classad constraint to match against JobBatchName. EG: 'regexp("omicron-online-.*", JobBatchName)'
    :param str| htcondor.Schedd schedd: name of schedd to query, defualts to the local schedd
                                        EG: detchar.ligo-wa.caltech.edu
    :param list[str] projection: list of classad attributes to return
    :param htcondor.Schedd schedd: schedd to query
    :param list[str] projection: list of classad attributes to query for,
                                 defaults to ["ClusterId", "ProcId", "JobBatchName", "JobStatus"]
    :return: list of matching Jobs
    """
    if schedd is None:
        schedd = htcondor.Schedd()

    ret = schedd.query(projection=projection, constraint=constraint)
    return ret


def main():
    global logger

    log_file_format = "%(asctime)s - %(levelname)s - %(funcName)s %(lineno)d: %(message)s"
    log_file_date_format = '%m-%d %H:%M:%S'
    logging.basicConfig(format=log_file_format, datefmt=log_file_date_format)
    logger = logging.getLogger(__process_name__)
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description=__doc__, prog=__process_name__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_add_args(parser)
    args = parser.parse_args()
    verbosity = 0 if args.quiet else args.verbose

    if verbosity < 1:
        logger.setLevel(logging.CRITICAL)
    elif verbosity < 2:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    # debugging?
    logger.debug(f'{__process_name__} version: {__version__} called with arguments:')
    for k, v in args.__dict__.items():
        logger.debug('    {} = {}'.format(k, v))

    # scan through online jobs count how many jobs per group are running
    if len(args.groups) == 0:
        config = configparser.ConfigParser()
        config_file = Path(args.config_file)
        config.read(config_file)

        groups = config.sections()
        logger.debug(f'There are {len(groups)} groups in config file: {config_file.absolute()}')
    else:
        groups = args.groups
    logger.debug(f'Groups to monitor: {", ".join(groups)}')
    online_jobs = dict()
    for group in groups:
        online_jobs[group] = 0
        srch_expr = classad.ExprTree(f'regexp("omicron-online-{group}\\s+\\d+", JobBatchName) && '
                                     f'regexp(".*dagman.*", Cmd)')
        jobs = query_by_name(srch_expr)
        for job in jobs:
            logger.debug(f'Job: {job}')
            if job['JobStatus'] == 1:
                online_jobs[group] += 1
    logger.debug(f'Online jobs per group: {online_jobs}')


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OSError, NameError, ArithmeticError, RuntimeError) as ex:
        print(ex, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    if logger is None:
        logging.basicConfig()
        logger = logging.getLogger(__process_name__)
        logger.setLevel(logging.DEBUG)
    # report our run time
    logger.info(f'Elapsed time: {time.time() - start_time:.1f}s')
