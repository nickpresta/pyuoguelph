#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""This script is used for parsing event data from the University of Guelph
Student Affairs website"""

import urllib2
from datetime import datetime
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    import sys
    print("You must have Beautiful Soup >4.0 installed. Exiting...")
    sys.exit(1)

__author__ = "Nicholas Presta"
__copyright__ = "Copyright 2011, The Pyuoguelph project"
__license__ = "GPL"
__version__ = "0.0.2"
__maintainer__ = "Nicholas Presta"
__email__ = "nick@nickpresta.ca"

class EventNotFoundException(Exception):
    """Used to signal when an event could not be found."""
    pass

class EventParserConnectionException(Exception):
    """Used to signal when a connection could not be made."""
    pass

class EventParser(object):
    """This class is responsible for grabbing event data given an event URL."""

    def get_event(self, url):
        """Returns the event description, the date/time it is offered, etc.

        Returns:
            A dictionary containing various pieces of information about an
            event. Keys are always present, regardless of the data
            existing or not.

        Arguments:
            url: The URL to a single event.

        Exceptions:
            EventNotFoundException: When the event cannot be found. Most likely
                due to an incorrect URL.
        """

        source = EventParser.fetch_source(url)
        return EventParser.parse_source(source)

    @staticmethod
    def parse_source(source):
        """Returns the event description for a given event.

        Returns:
            Various pieces of information about a course.
            Keys are always present, regardless of the data existing or not.

        Arguments:
            The HTML source for a given event.
        """

        soup = BeautifulSoup(source)

        info = {}

        info['title'] = soup.find('p', attrs={'class': 'text12'}).find('strong').text.strip()
        info['organization'] = soup.find('span', attrs={'class': 'text11'}).text.strip()
        info['description'] = soup.find('p', attrs={'class': 'text11'}).text.strip()
        table = soup.find('table', attrs={'width': '98%'})
        for row in table.findAll('tr'):
            first, second = row.findAll('td')
            info[EventParser._format_key(first.text)] = \
                    EventParser._format_text(second.text)

        # The above is generated dynamically, it might be missing field names
        # I want to add those missing names back in, if they're missing
        if 'qualifies_as' not in info:
            info['qualifies_as'] = ''
        if 'advanced_registration' not in info:
            info['advanced_registration'] = ''
        if 'more_information' not in info:
            info['more_information'] = ''

        return info

    @staticmethod
    def _format_key(key):
        key = key.replace('(', '').replace(')', '')
        formatted = re.sub('[^\w]', ' ', key).lower().strip()
        return re.sub('\s{1,}', '_', formatted)

    @staticmethod
    def _format_text(text):
        formatted = re.sub('\s{2,}', ' ', text).strip()
        return formatted.replace('( ', '(').replace(' )', ')')

    @staticmethod
    def fetch_source(url):
        """Fetches the source code from the given URL.

        Returns: Data as a string from the event page.

        Arguements:
            url: URL to fetch

        Exceptions:
            EventParserConnectionException: Could not connect (urllib2 error).
            EventNotFoundException: Could not find event (invalid input).
        """
        try:
            site = urllib2.urlopen(url)
        except (urllib2.HTTPError, IOError):
            raise EventParserConnectionException(
                    "Could not fetch event information at %s" % url)
        if 'event_id' not in site.geturl():
            raise EventNotFoundException("Event not found at %s" % url)
        data = site.read()
        site.close()
        return data

if __name__ == '__main__':
    e = EventParser()
    print e.get_event(raw_input())
