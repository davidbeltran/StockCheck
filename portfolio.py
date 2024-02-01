##########################################################################
# Author: David Beltran
# File: portfolio.py
# Date: August 19, 2022
# This module holds the Portfolio class. Used to store Bond and Stock
# objects from csv files . Stocks trends data from JSON file are 
# stored into a database. Matplotlib utilized to visualize trend data.
##########################################################################

# Standard libary imports
from datetime import datetime
from datetime import date
import sqlite3
import json 
import matplotlib.pyplot as plt
import numpy as np
from yahoofinancials import YahooFinancials
from dateutil.relativedelta import relativedelta

# Application author designed module imports
from bond import Bond
from stock import Stock

# Global variable used to generate purhase IDs
id_hold = 0

class Portfolio:

    # Class constructor
    def __init__(self, investor):
        self.investor = investor
        self.stocks, self.db_stocks = [], []
        self.dates, self.updated_stock_info = [], []
        self.symbols, self.updated_symbols = set(), set() 
        self.trends, self.updated_trends = {}, {} 

    # Method reads a text file and instantiates Stock and Bond objects.
    # Objects are then entered to self.stocks list. 
    def fill_report(self, filename):
        try:
            with open(filename) as f:
                content = f.read().splitlines()
        except FileNotFoundError:
            print(f"File, {filename}, was not found.")
        content = content[1:]

        # For loop includes handling incorrect value type exceptions
        for item in content:
            stock_info = item.split(',')
            try:
                if len(stock_info) == 7:
                    self.stocks.append(Bond(self.__generate_ID(),
                    stock_info[0], float(stock_info[1]),
                    float(stock_info[2]), float(stock_info[3]),
                    datetime.strptime(stock_info[4], '%m/%d/%Y').date(),
                    float(stock_info[5]), float(stock_info[6])))
                elif len(stock_info) == 5:
                    self.stocks.append(Stock(self.__generate_ID(),
                    stock_info[0], float(stock_info[1]),
                    float(stock_info[2]), float(stock_info[3]),
                    datetime.strptime(stock_info[4], '%m/%d/%Y').date()))
            except ValueError:
                print(f"{stock_info[0]} was given an incorrect value type."
                        + "Stock was not stored.")
                pass 

    # Private method that creates a stocks_trends table in the database
    def __create_stock_trends_table(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE stocks_trends (
            symbol text,
            price_date text,
            open_price text,
            high_price text,
            low_price text,
            close_price real,
            volume real
        )
        """)
        conn.commit()
        conn.close()

    # Private method that creates a stocks table in the database
    def __create_stock_table(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE stocks (
            stock_id text,
            investor_id text,
            symbol text,
            quantity real,
            purchase_price real,
            current_price real,
            purchase_date text
        )
        """)
        conn.commit()
        conn.close()

    # Private method that creates a bonds table in the database
    def __create_bond_table(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE bonds (
            stock_id text,
            investor_id text,
            symbol text,
            quantity real,
            purchase_price real,
            current_price real,
            purchase_date text,
            coupon real,
            yield_perc real
        )
        """)
        conn.commit()
        conn.close()

    # Method handles exception if tables already exist
    # Method designed to create future tables
    def create_tables(self):
        try:
            self.__create_stock_table()
            self.__create_bond_table()
            self.__create_stock_trends_table()
        except sqlite3.OperationalError:
            pass

    # Public method that fills stocks_trends database table with attributes
    # from JSON data. Method also prepares JSON data to be used 
    # for visualization. 
    def fill_stock_trends_table(self, filename):
        with open(filename, encoding = 'utf-8') as f:
            all_trends_data =  json.load(f)
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        print("Loading data to database...")
        trendings = []
        for trend in all_trends_data:
            trendings.append((trend['Symbol'], trend['Date'], trend['Open'],
                trend['High'], trend['Low'], trend['Close'],
                trend['Volume']))
            if trend['Symbol'] not in self.symbols:
                self.symbols.add(trend['Symbol'])
                self.trends[trend['Symbol']] = {'Dates': [], 'Closes': []}
            self.trends[trend['Symbol']]['Dates'].append(
                datetime.strptime(trend['Date'], '%d-%b-%y'))
            self.trends[trend['Symbol']]['Closes'].append(trend['Close'])
        rows = c.execute("""SELECT * FROM stocks_trends""").fetchall()
        if not rows:
            c.executemany(
                "INSERT INTO stocks_trends VALUES (?, ?, ?, ?, ?, ?, ?)",
                trendings)
            conn.commit()
        else:
            pass
        conn.close()
        print("Database table, \'stocks_trends\', " +
                "has been filled with trend data.")

    # Public method that fills stocks and bonds database tables
    # with attributes from objects created from text data
    # Loop iteration utilized to prepare updated stock data
    # for visualization.
    def fill_stock_bonds_tables(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        s_rows = c.execute("""
            SELECT * FROM stocks
            """).fetchall()
        conn.commit()
        b_rows = c.execute("""
            SELECT * from bonds
            """).fetchall()
        conn.commit()
        for stock in self.stocks:
            if (isinstance(stock, Bond)) and (not b_rows):
                c.execute("INSERT INTO bonds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (stock.get_purchaseID(), self.investor.get_ID(),
                        stock.get_symbol(), stock.get_quantity(), 
                        stock.get_purchase_price(), stock.get_current_price(),
                        stock.get_purchase_date(), stock.get_coupon(),
                        stock.get_yield_perc()))
                conn.commit()
            elif (not s_rows):
                c.execute("INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (stock.get_purchaseID(), self.investor.get_ID(),
                        stock.get_symbol(), stock.get_quantity(), 
                        stock.get_purchase_price(), stock.get_current_price(),
                        stock.get_purchase_date()))
                conn.commit()
            else:
                pass
            # Conditional statement utilizes for loop to prepare current
            # stock data for visualization using yahoofinancials library
            if not isinstance(stock, Bond):
                financials = YahooFinancials(stock.get_symbol())
                today = str(date.today())
                before = str(date.today() - relativedelta(years = 5))
                self.updated_stock_info.append(
                    financials.get_historical_price_data(
                        before, today, 'monthly'))
        conn.close()

    # Plots current stock data into a line graph. Data is from
    # yahoofinancials live updates
    def chart_updated_trends(self, filename):
        for info in self.updated_stock_info:
            symbol = list(info.keys())[0]
            if symbol not in self.updated_symbols:
                self.updated_symbols.add(symbol)
                self.updated_trends[symbol] = {'Dates': [], 'Closes': []}
            count = 0
            for month in info[symbol]['prices']:
                self.updated_trends[symbol]['Dates'].append(
                    datetime.strptime(
                        info[symbol]['prices'][count]['formatted_date'],
                        '%Y-%m-%d'))
                self.updated_trends[symbol]['Closes'].append(
                    info[symbol]['prices'][count]['close'])
                count += 1
        plt.style.use('_classic_test_patch')
        fig, ax = plt.subplots(figsize = (13, 7))
        for symbol in self.updated_symbols:
            ax.plot(self.updated_trends[symbol]['Dates'],
            self.updated_trends[symbol]['Closes'], label = symbol)
        ax.legend(loc = 0)
        ax.set_title("Updated trends of " + self.investor.get_name() +
                "'s Stocks", fontsize = 24)
        ax.set_xlabel('', fontsize = 10)
        fig.autofmt_xdate()
        ax.set_ylabel("Price", fontsize = 10)
        ax.tick_params(axis = 'both', which = 'major', labelsize = 10)
        plt.savefig(filename)
        print("\nGraph for recent trends created and saved on " +
                filename + " file.\n")
        

    # Public method that plots stock price trends on a line graph.
    # Data is from a JSON file with stock data 
    def chart_trends(self, filename):
        plt.style.use('_classic_test_patch')
        fig, ax = plt.subplots(figsize = (13, 7))
        # NumPy array utilized to multiply closing prices with
        # Stock object's quantity. 
        for stock in self.stocks:
            if stock.get_symbol() in self.symbols:
                ax.plot(self.trends[stock.get_symbol()]['Dates'],
                list(np.array(self.trends[stock.get_symbol()]['Closes'])
                * stock.get_quantity()), label = stock.get_symbol())
        ax.legend(loc = 0)
        ax.set_title("Trends of " + self.investor.get_name() +
                "'s Portfolio Stocks", fontsize = 24)
        ax.set_xlabel('', fontsize = 10)
        fig.autofmt_xdate()
        ax.set_ylabel("Price", fontsize = 10)
        ax.tick_params(axis = 'both', which = 'major', labelsize = 10)
        plt.savefig(filename)
        print("\nGraph for trends from JSON file created and saved on " +
                filename + " file.\n")

    # Method that takes data from database and instantiates
    # Stock and Bond objects and are added to their own separate list
    def create_db_stocks(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("SELECT * FROM stocks")
        items = c.fetchall()
        for item in items:
            self.db_stocks.append(Stock(item[0], item[2], item[3],
            item[4], item[5], datetime.strptime(item[6], '%Y-%m-%d').date()))
        conn.commit()
        c.execute("SELECT * FROM bonds")
        items = c.fetchall()
        for item in items:
            self.db_stocks.append(Bond(item[0], item[2], item[3],
            item[4], item[5], datetime.strptime(item[6], '%Y-%m-%d').date(),
            item[7], item[8]))
        conn.commit()
        conn.close()

    # Displays Stock and Bond objects instantiated from the database and
    # sends report to a .txt file
    def display_fill_report(self, filename):

        # Output stored in variable, report.
        report = (f"Stock ownership for {self.investor.get_name()}\n"
                + ("=" * 110) + "\n"
                + "{:<15}{:<15}{:<20}{:<30}{:<20}{:<20}".format(
                    'Stock', 'Share #', 'Earnings/Losses',
                    'Yearly Earnings/Losses', 'Coupon', 'Yield') + "\n"
                + ("=" * 110) + "\n")
        print(report)

        max_yield = self.__get_max_yield()
        for stock in self.db_stocks:
            if stock.get_earn_loss() < 0:
                 earn_loss = str("-${:.2f}".format(round(abs(
                    stock.get_earn_loss()), 2)))
            else:
                earn_loss = str("${:.2f}".format(round(
                    stock.get_earn_loss())))

            if isinstance(stock, Bond):
                row = ("{:<15}{:<15}{:<20}{:<30}{:<20}{:<20}".format(
                    stock.get_symbol(), stock.get_quantity(),
                    earn_loss, str(f"{round(stock.get_yearly_value(), 2)}%"),
                    str(stock.get_coupon()),
                    str(f"{stock.get_yield_perc()}%")) + "\n" + ("-" * 110)
                    + "\n")
                print(row)
                report += row
            else:
                row = ("{:<15}{:<15}{:<20}{:<30}{:<20}{:<20}".format(
                    stock.get_symbol(), stock.get_quantity(),
                    earn_loss, str(f"{round(stock.get_yearly_value(), 2)}%"),
                    '-', '-') + "\n" + ("-" * 110) + "\n")
                print(row)
                report += row

            if stock.get_yearly_value() == max_yield:
                high_symbol = stock.get_symbol()

        print("=" * 110)
        if max_yield >= 0:
            line = ("The stock with the highest average yearly yield "
                + f"is: {high_symbol}\n")
            print(line)
            report += line
        elif max_yield < 0:
            line = ("The stock with the lowest average yearly loss "
                + f"is: {high_symbol}")
            print(line)
            report += line

        try:
           with open(filename, 'w') as f:
             f.write(report)
        except Exception:
            print(f"Writing to the file, {filename}, failed")

    # Private method to find the highest average yearly yield
    def __get_max_yield(self):
        yearly_yields = []
        for stock in self.stocks:
            yearly_yields.append(stock.get_yearly_value())
        return max(yearly_yields)

    # Private method that generates a purchase ID 
    def __generate_ID(self):
        global id_hold
        id_hold += 1
        return id_hold

    # Empties the stocks table
    def delete_stocks(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("DELETE from stocks")
        conn.commit()
        conn.close()

    # Empties the bonds table
    def delete_bonds(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("DELETE from bonds")
        conn.commit()
        conn.close()

    # Empties the stocks_trends table
    def delete_stocks_trends(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("DELETE from stocks_trends")
        conn.commit()
        conn.close()

    # Displays contents in stocks_trends table
    def show_stocks_trends_table(self):
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute("SELECT * from stocks_trends")
        rows = c.fetchall()
        print("\nList of rows in stock's trends table.\n")
        for row in rows:
            print(row)
