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

__author__ = "Nicholas Presta"
__copyright__ = "Copyright 2011, The Pyuoguelph project"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Nicholas Presta"
__email__ = "nick@nickpresta.ca"

class CourseParser(object):
    """ This class is responsible for grabbing course data for a specific year

        It is possible to grab:
        1. All course data for a specific course in a specific year

        TODO:
        1. Grab all courses available for a specific year
        2. Grab all courses available for a specific program in a specific year """

    # This is the URL for a course calendar
    DESC_URL = "http://www.uoguelph.ca/registrar/calendars/undergraduate/%s/courses/%s.shtml"

    def get_course(self, year, code):
        """ Returns the course description, the semester it was offered, the
            credit value, and the restrictions (if any) """
        year = self._build_year_string(year)
        source = self._fetch_source(self._build_url(year, code))
        soup = BeautifulSoup(source)
        raw_data = [tags.text for tags in soup.findAll(attrs={'colspan': '2'})]

        info = {}

        course_parts = raw_data[0].split()
        info['course_code'] = course_parts[0].replace("*", "")
        info['course_number'] = course_parts[0].split("*")[1]
        info['course_department'] = course_parts[0].split("*")[0]

        info['course_description'] = re.sub("\s{2,}", " ",
                raw_data[1].replace("\n", ""))

        try:
            restrictions = soup.find(
                    attrs={'class': 'restrictions'}).findChild('td',
                            attrs={'class': 'text'}).text
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

        course_parts = raw_data[0].split()
        info['course_title'] = ' '.join(course_parts[1:-3])
        info['course_semesters'] = course_parts[-3]
        info['course_credit'] = course_parts[-1].replace("[", "").replace("]", "")

        return info

    def _build_year_string(self, year):
        """ Returns the year in a format that can be used directly in the URL
            The format is either 'current' for the current year, or
            the 'year - year+1' """
        if year == str(datetime.now().year):
            return 'current'
        else:
            return "%s-%s" % (year, str(int(year) + 1))

    def _build_url(self, year, code):
        """ Returns the full URL based on the uoguelph.ca domain, year, and
            course code """
        return self.DESC_URL % (year, code)

    def _fetch_source(self, url):
        """ Fetches the source code from the URL given """
        site = urllib2.urlopen(url)
        if url != site.geturl():
            raise Exception("Course/year not found")
        data = site.read()
        site.close()
        return data

if __name__ == '__main__':
    import sys
    cp = CourseParser()
    print(cp.get_course(sys.argv[1], sys.argv[2]))
