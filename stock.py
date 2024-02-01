##########################################################################
# Author: David Beltran
# File: stock.py
# Date: August 19, 2022
# This module holds the Stock class. Used to instantiate stock objects
# that store stock information.
##########################################################################

# Standard libary imports
from datetime import date

# Global variable with number of days in tropical year calendar
YEAR = 365.2422

# Class constructor
class Stock:
    def __init__(self, purchaseID, symbol, quantity, purchase_price,
            current_price, purchase_date):
        self.purchaseID = purchaseID
        self.symbol = symbol.upper()
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.current_price = current_price
        self.purchase_date = purchase_date
        self.earn_loss = self.__create_earn_loss()
        self.price_change = self.__create_price_change()
        self.yearly_value = self.__create_yearly_value()

# Getters and setters
    def get_purchaseID(self):
        return self.purchaseID

    def set_purchaseID(self, purchaseID):
        self.purchaseID = purchaseID
        
    def get_symbol(self):
        return self.symbol

    def set_symbol(self, symbol):
        self.symbol = symbol.upper()

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_purchase_price(self):
        return self.purchase_price

    def set_purchase_price(self, purchase_price):
        self.purchase_price = purchase_price

    def get_current_price(self):
        return self.current_price

    def set_current_price(self, current_price):
        self.current_price = current_price

    def get_purchase_date(self):
        return self.purchase_date

    def set_purchase_date(self, purchase_date):
        self.purchase_date = purchase_date

# Default to_string() method
    def to_string(self):
        if self.earn_loss < 0:
            earn_loss = f"-${str(abs(round(self.earn_loss, 2)))}"
        else:
            earn_loss = f"${str(round(self.earn_loss, 2))}"
        return (f"Purchase ID: {self.purchaseID}, "
        + f"Symbol: {self.symbol}, Quantity: {self.quantity}, "
        + f"Purchase Price: ${str(round(self.purchase_price, 2))}, "
        + f"Current Price: ${str(round(self.current_price, 2))}, "
        + f"Purchase Date: {self.purchase_date.strftime('%B %d, %Y')}, "
        + f"Earnings/Losses: {earn_loss}, "
        + f"Price Change: {round(self.price_change, 2)}%, "
        + f"Yearly Yield: {round(self.yearly_value, 2)}%]")

# Private methods used to calculate values for object attributes
    def __create_earn_loss(self):
        return (self.current_price - self.purchase_price) * self.quantity

    def get_earn_loss(self):
        return self.earn_loss

    def __create_price_change(self):
        return (((self.current_price - self.purchase_price) / 
        self.purchase_price) * 100)

    def get_price_change(self):
        return self.price_change

    def __create_yearly_value(self):
        return (((self.current_price - self.purchase_price) /
        self.purchase_price) /
        (((date.today() - self.purchase_date).days) / YEAR)) * 100

    def get_yearly_value(self):
        return self.yearly_value
