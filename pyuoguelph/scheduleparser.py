#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""This script is used for parsing class/exam schedule data."""

__author__ = "Nicholas Presta"
__copyright__ = "Copyright 2011, The Pyuoguelph project"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Nicholas Presta"
__email__ = "nick@nickpresta.ca"

class ScheduleParser(object):
    """This class is responsible for parsing class/exam schedule data."""

    def __init__(self, parts_split_length=7):
        """Define the length of each "part" to form a single item."""
        self.parts_split_length = parts_split_length

    def get_schedule(self, data):
        """Parses the schedule data.

        Returns:
            A dictionary, containing the key 'schedule', which contains a list
            of dictionaries representing a scheduled item.

        Arguments:
            The raw, plain-text data for your schedule.
        """
        info = {}
        info['schedule'] = []

        parts = data.split('|')[1:]
        for i in range(0, len(parts), self.parts_split_length):
            item = parts[i:i+self.parts_split_length]
            info['schedule'].append(ScheduleParser.parse_item(item))

        return info

    @staticmethod
    def parse_item(item):
        """Parses an item list and returns a ScheduleItem namedtuple.

        Returns:
            A ScheduleItem namedtuple with the item data as members.

        Arguments:
            item: An item list of course/exam information.
        """
        out = {
                'name': item[0],
                'start_date': item[1],
                'end_date': item[2],
                'type': item[3],
                'days': item[4],
                'times': item[5],
                'location': item[6]}

        return out

if __name__ == '__main__':
    data = raw_input()
    parser = ScheduleParser()
    out = parser.get_schedule(data)
    print out
