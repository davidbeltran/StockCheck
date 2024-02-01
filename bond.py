##########################################################################
# Author: David Beltran
# File: bond.py
# Date: August 19, 2022
# This module holds the Bond class. Used to instantiate bond objects
# that store bond information. Subclass of the Stock class
##########################################################################

# Application author designed module imports
from stock import Stock

# Class constructor
class Bond(Stock):
    def __init__(self, purchaseID, symbol, quantity, purchase_price,
            current_price, purchase_date, coupon, yield_perc):
        super().__init__(purchaseID, symbol, quantity, purchase_price,
            current_price, purchase_date)
        self.coupon = coupon
        self.yield_perc = yield_perc

# Getters and setters for extra attributes
    def get_coupon(self):
        return self.coupon

    def set_coupon(self, coupon):
        self.coupon = coupon

    def get_yield_perc(self):
        return self.yield_perc

    def set_yield_perc(self, yield_perc):
        self.yield_perc = yield_perc

