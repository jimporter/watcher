import argparse
import logging
import yaml

from .jobs import JobQueue
from .notifiers import Notifiers
from .parser import job
from .sites import Site
from .version import version


def make_site(notifiers, kind=None, **kwargs):
    notifier = notifiers.default if kind is None else notifiers[kind]
    return Site(notifier=notifier, **kwargs)


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

    notifiers = Notifiers()
    with open('config.yml') as f:
        data = yaml.safe_load(f)
        for k, v in data['notifiers'].items():
            notifiers.add(k, **v)
        sites = [make_site(notifiers, **i) for i in data['sites']]

    jobs = JobQueue()
    for i in sites:
        jobs.add(lambda *args: job(i, *args), i.interval)

    try:
        jobs.run()
    except KeyboardInterrupt:
        print('exiting...')
