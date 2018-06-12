import re
from enum import Enum

Flavor = Enum('MatcherFlavor', ['xpath', 'css'])


def parse_interval(t):
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    m = re.match(r'^([\d\.]+)(s|m|h|d)$', t)
    if not m:
        raise ValueError("unable to parse time {!r}".format(t))
    return float(m.group(1)) * units[m.group(2)]


class Site:
    def __init__(self, url, css=None, xpath=None, interval=600.0):
        if (css is None) == (xpath is None):
            raise TypeError('exactly one of css or xpath must be specified')
        self.url = url
        self.css = css
        self.xpath = xpath
        self.interval = parse_interval(interval)

    @property
    def selector(self):
        return ((self.css, Flavor.css) if self.css else
                (self.xpath, Flavor.xpath))

    def __repr__(self):
        if self.css:
            fmt = '<Site(url={url!r}, css={css!r}, time={time!r})>'
        else:
            fmt = '<Site(url={url!r}, xpath={xpath!r}, time={time!r})>'
        return fmt.format(url=self.url, css=self.css, xpath=self.xpath,
                          time=self.time)
