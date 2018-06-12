import argparse
import logging
import yaml

from .jobs import JobQueue
from .parser import job
from .sites import Site
from .version import version


def main():
    parser = argparse.ArgumentParser(prog='watcher')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + version)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display verbose output')
    parser.add_argument('config', help='config file to use')

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING
    )

    with open('config.yml') as f:
        data = yaml.safe_load(f)
        sites = [Site(**i) for i in data['sites']]

    jobs = JobQueue()
    for i in sites:
        jobs.add(lambda *args: job(i, *args), i.interval)

    try:
        jobs.run()
    except KeyboardInterrupt:
        print('exiting...')
