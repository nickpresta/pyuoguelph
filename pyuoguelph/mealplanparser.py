#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""This script is used for parsing meal plan data from the University of Guelph
Hostpitality Services website."""

import urllib2
from datetime import datetime
import re

from bs4 import BeautifulSoup
import requests

__author__ = "Nicholas Presta"
__copyright__ = "Copyright 2011, The Pyuoguelph project"
__license__ = "GPL"
__version__ = "0.0.3"
__maintainer__ = "Nicholas Presta"
__email__ = "nick@nickpresta.ca"

class InvalidCredentialsException(Exception):
    """Used to signal when invalid credentials have been used."""
    pass

class MealPlanParserConnectionException(Exception):
    """Used to signal when a connection could not be made."""
    pass

class MealPlanParser(object):
    """This class is responsible for grabbing event data given an event URL."""

    login_url = ('https://www.hospitality.uoguelph.ca/accountservices/'
        'chooseaccount.cfm?action=balance')
    payload = {'j_username': '', 'j_password': '', 'args': 'action=balance',
            'redirect': '/accountservices/chooseaccount.cfm'}

    def __init__(self, username, password):
        """Requires the username and password for an account we're querying."""
        self.payload['j_username'] = username
        self.payload['j_password'] = password

    def get_balance(self):
        """Returns your meal card balance(s).

        Returns:
            A dictionary containing your meal card balances.

        Exceptions:
            InvalidCredentialsException: When you have specified invalid
                credentials.
        """

        source = self._fetch_source()
        return MealPlanParser.parse_source(source)

    @staticmethod
    def parse_source(source):
        """Returns your meal card balances.

        Returns:
            Various pieces of information about your meal card.
            Keys are always present, regardless of the data existing or not.

        Arguments:
            The HTML source for an account balance page.
        """

        soup = BeautifulSoup(source)

        info = {}
        info['type'] = ''
        info['balance'] = ''

        table = soup.findAll('table', attrs={'border': '0', 'width': '100%'})[1]
        # Skip first header row
        # Should only loop once, but I can't test this
        # since I only have 1 type of plan
        for row in table.findAll('tr')[1:]:
            first, second, garbage = row.findAll('td')
            info['type'] = first.text.strip()
            info['balance'] = MealPlanParser._format_text(second.text)

        return info

    @staticmethod
    def _format_text(text):
        return text.replace('$', '').strip()

    def _fetch_source(self):
        """Fetches the source code for your account balance.

        Returns: Data as a string from the meal plan account balance page.

        Exceptions:
            MealPlanParserConnectionException: Could not connect (urllib2 error).
            InvalidCredentialsException: Could not login (invalid input).
        """
        try:
            request = requests.post(self.login_url, data=self.payload,
                    allow_redirects=True)
        except requests.exceptions.RequestException:
            raise MealPlanParserConnectionException(
                    "Could not fetch information at %s" % url)

        data = request.text

        if 'Your login information is not valid' in data:
            raise InvalidCredentialsException(
                "Could not fetch information: invalid credentials supplied.")

        return data

if __name__ == '__main__':
    username, password = raw_input().split()
    m = MealPlanParser(username, password)
    print m.get_balance()
