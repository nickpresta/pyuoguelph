import sys
import os
import unittest
from datetime import datetime

from pyuoguelph import courseparser
from courseparser import CourseParser
from courseparser import CourseNotFoundException
from courseparser import CourseParserConnectionException

# save the reference to the real urlopen
real_urlopen = courseparser.urllib2.urlopen

class KnownUndergraduateCourseNumbers(unittest.TestCase):
    known_course_numbers = (
            ('cis1910', '1910'),
            ('cis2750', '2750'),
            ('cis3000', '3000'))

    def setUp(self):
        self.course_parser = CourseParser()
        courseparser.urllib2.urlopen = real_urlopen

    def testCourseNumberKnownValues(self):
        for course, code in self.known_course_numbers:
            result = self.course_parser.get_course(datetime.now().year, course)
            self.assertEqual(result['course_number'], code)

    def testCourseNotFoundException(self):
        self.assertRaises(CourseNotFoundException,
                self.course_parser.get_course, '2011', 'cis1234')

    def testCourseParserConnectionException(self):
        # Mock urllib2's urlopen to throw an exception
        def dummy_urlopen(url):
            raise IOError
        courseparser.urllib2.urlopen = dummy_urlopen

        self.assertRaises(CourseParserConnectionException,
                self.course_parser.get_course, '2099', 'cis1910')

class KnownGuelphHumberCourseNumbers(unittest.TestCase):
    known_course_numbers = (
            ('psyc1130', '1130'),
            ('kin2060', '2060'),
            ('ecs4900', '4900'))

    def setUp(self):
        self.course_parser = CourseParser()
        courseparser.urllib2.urlopen = real_urlopen

    def testCourseNumberKnownValues(self):
        for course, code in self.known_course_numbers:
            result = self.course_parser.get_course(datetime.now().year, course,
                    CourseParser.GUELPHHUMBER_CALENDAR)
            self.assertEqual(result['course_number'], code)

    def testCourseNotFoundException(self):
        self.assertRaises(CourseNotFoundException,
                self.course_parser.get_course, '2011', 'psyc9999')

    def testCourseParserConnectionException(self):
        # Mock urllib2's urlopen to throw an exception
        def dummy_urlopen(url):
            raise IOError
        courseparser.urllib2.urlopen = dummy_urlopen

        self.assertRaises(CourseParserConnectionException,
                self.course_parser.get_course, '2099', 'psyc1130')


if __name__ == '__main__':
    unittest.main()
