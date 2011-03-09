import sys
import os
import unittest
from datetime import datetime

from courseparser import CourseParser

class KnownUndergraduateCourseNumbers(unittest.TestCase):
    known_course_numbers = (
            ('cis1910', '1910'),
            ('cis2750', '2750'),
            ('cis3000', '3000'))
    course_parser = CourseParser()

    def testCourseNumberKnownValues(self):
        for course, code in self.known_course_numbers:
            result = self.course_parser.get_course(datetime.now().year, course)
            self.assertEqual(result['course_number'], code)

class KnownGuelphHumberCourseNumbers(unittest.TestCase):
    known_course_numbers = (
            ('psyc1130', '1130'),
            ('kin2060', '2060'),
            ('ecs4900', '4900'))
    course_parser = CourseParser()

    def testCourseNumberKnownValues(self):
        for course, code in self.known_course_numbers:
            result = self.course_parser.get_course(datetime.now().year, course,
                    CourseParser.GUELPHHUMBER_CALENDAR)
            self.assertEqual(result['course_number'], code)

if __name__ == '__main__':
    unittest.main()
