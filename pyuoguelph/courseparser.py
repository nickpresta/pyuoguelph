#!/usr/bin/env python

""" This script is used for parsing course data from the uoguelph.ca website """

import urllib2
from datetime import datetime
import re

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    import sys
    print("You must have Beautiful Soup installed. Exiting...")
    sys.exit(1)

# If you don't have Shove, we just use a simple dictionary
# See: __init__ for CourseParser
try:
    from shove import Shove
    SHOVE_IMPORTED = True
except ImportError:
    SHOVE_IMPORTED = False
    print("Shove not installed. No caching available.")

import settings

__author__ = "Nicholas Presta"
__copyright__ = "Copyright 2011, The Pyuoguelph project"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Nicholas Presta"
__email__ = "nick@nickpresta.ca"

class CourseNotFoundException(Exception):
    pass

class CourseParserConnectionException(Exception):
    pass

class CourseParser(object):
    """ This class is responsible for grabbing course data for a specific year

        It is possible to grab:
        1. All course data for a specific course in a specific year

        TODO:
        1. Grab all courses available for a specific year
        2. Grab all courses available for a specific program in a specific year """

    UNDERGRADUATE_CALENDAR = 'undergraduate'
    GRADUATE_CALENDAR = 'graduate'
    DIPLOMA_CALENDAR = 'diploma'
    GUELPHHUMBER_CALENDAR = 'guelphhumber'
    CALENDAR_TYPES = (UNDERGRADUATE_CALENDAR, GRADUATE_CALENDAR,
            DIPLOMA_CALENDAR, GUELPHHUMBER_CALENDAR)

    def __init__(self, store=settings.store, cache=settings.cache):
        """Assigns the default settings to the local settings so they can be
            easily overridden at runtime.

            Arguments:
                store: Your backend store. By default, uses what ever is in
                       settings.store. If you don't have Shove installed,
                       will use a plain Python dictionary.
                cache: Your cache store. By default, uses what ever is in
                       settings.cache. If you don't have shove installed,
                       no cache will exist."""
        # This is the URL for a course calendar
        # Use %s as placeholders for dynamic information
        # In this case, the %s are for the calendar type, year and course code
        self.DESC_URL = "http://www.uoguelph.ca/registrar/calendars/%s/%s/courses/%s.shtml"
        if SHOVE_IMPORTED:
            self.store = Shove(store, cache)
        else:
            self.store = {}

    def get_course(self, year, code, calendar_type=UNDERGRADUATE_CALENDAR,
            fresh=False):
        """Returns the course description, the semester it was offered, the
           credit value, and the restrictions (if any).

           Returns:
               A dictionary containing various pieces of information about a
               course. Keys are always present, regardless of the data
               existing or not.

           Arguments:
               year: Calendar year (i.e. 2011).
               code: Course code (i.e. cis1910).
               calendar_type: The calendar type (see
                              CourseParser.CALENDAR_TYPES for valid options.
               fresh: Whether or not to fetch the data from your cache,
                      if possible.

            Exceptions:
                CourseNotFoundException: When the course is not found for a given
                                         calendar year or type."""
        key = self._build_key(year, code, calendar_type)
        if key in self.store and fresh:
            return self.store[key]

        source = self._fetch_source(self._build_url(year, code, calendar_type))
        soup = BeautifulSoup(source)

        info = {}

        raw_title = soup.find(attrs={'class': 'title'}).text
        course_parts = raw_title.split()
        info['course_code'] = course_parts[0].replace("*", "")
        info['course_number'] = course_parts[0].split("*")[1]
        info['course_department'] = course_parts[0].split("*")[0]
        info['course_title'] = ' '.join(course_parts[1:-3])
        info['course_semesters'] = course_parts[-3]
        info['course_credit'] = course_parts[-1].replace("[", "").replace("]", "")

        raw_desc = soup.find(attrs={'class': 'description'}).text
        info['course_description'] = re.sub("\s{2,}", " ",
                raw_desc.replace("\n", ""))

        try:
            restrictions = soup.find(
                    attrs={'class': 'restrictions'}).findChild('td').text
            info['course_restrictions'] = restrictions.replace("*", "")
        except AttributeError:
            # Course has no restrictions
            info['course_restrictions'] = ""

        try:
            prereqs = soup.find(attrs={'class': 'prereqs'}).findChild('td',
                attrs={'class': 'text'}).text
            info['course_prereqs'] = prereqs.replace("*", "")
        except AttributeError:
            # Course has no prereqs
            info['course_prereqs'] = ""

        # store this dict
        self.store[key] = info

        return info

    def _build_key(self, year, code, calendar_type):
        """Returns a (hopefully) unique key for our store.

           Returns a unique key for a given calendar year/type and
           course code.

           Arguments:
               year: The calendar year (i.e. 2011).
               code: The course code (i.e. cis1910).
               calendar_type: The calendar type (see
                              CourseParser.CALENDAR_TYPES for valid options."""
        return str(year) + str(code) + str(calendar_type)

    def _build_year_string(self, year):
        """Returns the year in a format that can be used directly in the URL
            The format is either 'current' for the current year, or
            the 'year - year+1'.

           Returns:
               The year needed for a given calendar (current, if the current year,
               or a range, like 1999-2000 if in the past)."""
        if int(year) == int(datetime.now().year):
            return 'current'
        else:
            return "%s-%s" % (year, str(int(year) + 1))

    def _build_url(self, year, code, calendar_type):
        """Returns the full URL based on the uoguelph.ca domain, year, and
            course code.

            Arguments:
                year: The calendar year
                code: The course code (i.e. cis1910)
                calendar_type: The calendar type (see
                               CourseParser.CALENDAR_TYPES for valid options."""
        year = self._build_year_string(year)
        return self.DESC_URL % (calendar_type, year, code.lower())

    def _fetch_source(self, url):
        """Fetches the source code from the given URL.

           Returns: Data as a string from the course page.

           Arguements:
               url: URL to fetch (generated from other private methods.

           Exceptions:
               CourseParserConnectionException: Could not connect (urllib2 error).
               CourseNotFoundException: Could not find course (invalid input)."""
        try:
            site = urllib2.urlopen(url)
        except (urllib2.HTTPError, IOError):
            raise CourseParserConnectionException("Could not fetch course information"
                    " at %s" % url)
        if url != site.geturl():
            raise CourseNotFoundException("Course/year not found at %s" % url)
        data = site.read()
        site.close()
        return data

if __name__ == '__main__':
    # no checks, just input all:
    # e.g. 2011 cis1910 undergraduate f
    cp = CourseParser()
    while True:
        inp = raw_input(">>> (Year, Code, Calendar, Fresh): ").split()
        print(cp.get_course(inp[0], inp[1], inp[2], inp[3]))
