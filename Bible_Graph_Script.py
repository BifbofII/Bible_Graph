#! /bin/python
# ---------------------------------------------------------------------------------------
# Author: Christoph Jabs
# Name: Bible_Graph_Script
# Date: 24.07.2017
# Python version: 3.6.2
# ---------------------------------------------------------------------------------------

import csv
import cairo
import configparser

# Static variable declarations
data_path = "data/"
data_files = {"books":"books.csv", "events":"events.csv", "persons":"persons.csv"}
data = {}

def read_data():
    for data_name, data_file_name in data_files.items():
        with open(data_path+data_file_name, newline='') as data_file:
            csv_reader = csv.DictReader(data_file, quotechar='"',
                    quoting=csv.QUOTE_NONNUMERIC)
            data_list = []
            for row in csv_reader:
                data_list.append(row)
            data[data_name] = data_list

def main():
    read_data()

main()
