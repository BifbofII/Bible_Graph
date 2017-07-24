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
import configparser
import argparse

# Static variable declarations
data_path = "data/"
data_files = {"books":"books.csv", "events":"events.csv", "persons":"persons.csv"}
data = {}

def read_data(data_file_path):
    with open(data_file_path, newline='') as data_file:
        csv_reader = csv.DictReader(data_file, quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC)
        data_list = []
        for row in csv_reader:
            data_list.append(row)
    return data_list 

def read_config(config_file_path):
    raw_config = configparser.ConfigParser()
    raw_config.read(config_file_path)
    config = {}
    for section in raw_config.sections():
        config[section] = {}
        for key, val in raw_config.items(section):
            try:
                value = int(val)
            except ValueError:
                try:
                    value = float(val)
                except ValueError:
                    for true in ('true','True','yes','Yes'):
                        if val == true:
                            value = True
                            break
                    else:
                        for false in ('false','False','no','No'):
                            if val == false:
                                value = False
                                break
                        else:
                            if len(val.split(',')) > 1:
                                value = val.split(',')
                            else:
                                value = val
            config[section][key] = value

    cli_parser = argparse.ArgumentParser(description=
            'A script to create a graph of the events and persons of the bible.')
    cli_parser.add_argument('--x-resolution', help='Vertical resolution of the output image',
            default=config['Output File']['x_resolution'], type=int)
    cli_parser.add_argument('--y-resolution', help='Horizontal resolution of the output image',
            default=config['Output File']['y_resolution'], type=int)
    cli_parser.add_argument('--output-type', help='Set the output file type',
            default=config['Output File']['file_type'])
    cli_parser.add_argument('--output-name', help='Set the name of the output file',
            default=config['Output File']['file_name'])
    cli_parser.add_argument('--prophets', help='Do not show prophets in output',
            action='store_false', default=config['Output']['prophets'])
    cli_parser.add_argument('--kings', help='Do not show kings in output',
            action='store_false', default=config['Output']['kings'])
    cli_parser.add_argument('--books', help='Do not show books in output',
            action='store_false', default=config['Output']['books'])
    cli_parser.add_argument('--family-tree', help='Do not show family tree in output',
            action='store_false', default=config['Output']['family_tree'])
    cli_args = vars(cli_parser.parse_args())

    presets = {}
    for section in config:
        presets[section] = {}
        for key, val in config[section].items():
            if key in cli_args.keys():
                presets[section][key] = cli_args[key]
            else:
                presets[section][key] = val

    return presets

def main():
    presets = read_config('config.cfg')
    for data_file_name in presets['File Paths']['data_files']:
        data[data_file_name[0:-4]] = read_data(presets['File Paths']['data_path']+data_file_name)
    print(data)

main()
