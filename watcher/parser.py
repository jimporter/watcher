import logging
import re
from lxml import html
from lxml.cssselect import CSSSelector
from urllib.request import urlopen

from .sites import Flavor

logger = logging.getLogger(__name__)


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


def job(site, last=None):
    try:
        doc = fetch(site.url)
    except Exception as e:
        logger.error(e)
        return

    curr = match(doc, *site.selector)
    if last is not None:
        eq = compare(last, curr)
        if not eq:
            print('New stuff: {}'.format(eq.added))
    return (curr,)
