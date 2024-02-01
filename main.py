##########################################################################
# Author: David Beltran
# File: main.py
# Date: August 19, 2022
# This file runs the main part of the application. Stock data is added
# to a database and visualized through a line graph.
##########################################################################

# Application author designed module imports
from investor import Investor
from portfolio import Portfolio

# Investor object instantiation
person = Investor(3, 'Bob Smith', '123 main', '1230432')

# Portfolio object instantiation
portfolio = Portfolio(person)

# Text files given to instantiate Stock and Bond objects
portfolio.fill_report('data/Lesson6_Data_Stocks.csv')
portfolio.fill_report('data/Lesson6_Data_Bonds.csv')

# Stock and Bond tables created and added to a database
portfolio.create_tables()

# stocks_trends table filled with data from JSON file
portfolio.fill_stock_trends_table('data/AllStocks.json')

# Stock trends are visualized and saved to a .png file with a line graph
portfolio.chart_trends('stocks_trends.png')

# Stores Stock and Bond objects into database
portfolio.fill_stock_bonds_tables()

# Plots closing prices of stocks of the last two years
portfolio.chart_updated_trends('updated_stocks_trends.png')

# These functions perform behavior on Investor object's portfolio
# data to query the database.
portfolio.create_db_stocks()
portfolio.display_fill_report('stock_report.txt')

# Added to demonstrate stocks_trends table was filled in database.
#portfolio.show_stocks_trends_table()