##########################################################################
# Author: David Beltran
# File: investor.py
# Date: August 19, 2022
# This module holds the Investor class. Used to instantiate an Investor
# object used in the stock summary application 
##########################################################################

# Class constructor
class Investor:
    def __init__(self, investorID = '', name = '', address = '',
            phone_number = ''):
        self.investorID = investorID
        self.name = name.title()
        self.address = address.title()
        self.phone_number = phone_number

# Getter and setter methods
    def get_ID(self):
        return self.investorID

    def set_ID(self, investorID):
        self.investorID = investorID

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name.title()

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address.title()

    def get_phone_number(self):
        return self.phone_number

    def set_phone_number(self, phone_number):
        self.phone_number = phone_number
