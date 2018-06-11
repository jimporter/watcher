import argparse
import logging
import re
import time
from enum import Enum
from lxml import html
from lxml.cssselect import CSSSelector
from urllib.request import urlopen

from .version import version

logger = logging.getLogger(__name__)

Flavor = Enum('MatcherFlavor', ['xpath', 'css'])


def stringify(element, nested=False, strip=True):
    if isinstance(element, str):
        return element

    result = element.text_content() if nested else element.text
    if strip:
        result = re.sub(r'\s+', ' ', result.strip())
    return result


def stringify_each(elements, *args, **kwargs):
    return [stringify(i, *args, **kwargs) for i in elements]


def match(doc, query, flavor, ordered=False, *args, **kwargs):
    if flavor == Flavor.xpath:
        result = doc.xpath(query)
    elif flavor == Flavor.css:
        result = doc.getroot().cssselect(query)
    else:
        raise TypeError('invalid flavor')

    result = stringify_each(result, *args, **kwargs)
    return result if ordered else set(result)


def fetch(url):
    # with open('index.html') as f:
    with urlopen(url) as f:
        logger.info('fetching {}'.format(url))
        return html.parse(f)


class CompareResult:
    def __init__(self, equal, added, removed):
        self.equal = equal
        self.added = added
        self.removed = removed

    def __bool__(self):
        return self.equal

    def __repr__(self):
        return '<CompareResult(equal={}, added={}, removed={})'.format(
            self.equal, self.added, self.removed
        )


def compare(a, b):
    return CompareResult(a == b, b - a, a - b)


def watch(url, selector, flavor, period):
    last = None
    curr = None

    while True:
        doc = fetch(url)
        last = curr
        curr = match(doc, selector, flavor)

        if last is not None:
            eq = compare(last, curr)
            if not eq:
                print('New stuff: {}'.format(eq.added))

        time.sleep(period)


def main():
    parser = argparse.ArgumentParser(prog='watcher')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + version)

    selector_p = parser.add_mutually_exclusive_group(required=True)
    selector_p.add_argument('-x', '--xpath', dest='selector',
                            type=lambda x: (x, Flavor.xpath),
                            help='the XPath selector to use')
    selector_p.add_argument('-c', '--css', dest='selector',
                            type=lambda x: (x, Flavor.css),
                            help='the CSS selector to use')

    parser.add_argument('-t', '--time', type=float, default=10 * 60,
                        help='time (in seconds) to wait between tries')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display verbose output')
    parser.add_argument('url', help='the URL to load')

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING
    )

    try:
        watch(args.url, *args.selector, args.time)
    except KeyboardInterrupt:
        print('exiting...')
