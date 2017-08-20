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
import matplotlib.colors as colors
from math import pi as pi

class Graph(object):
    def setup(self, width, height, start_year, end_year, border):
        """Setup the graph with basic preset values."""
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(width, width)
        self.user_space_dim = self.ctx.device_to_user(width, height)
        self.ctx.rectangle(border, border, 1 - border, self.user_space_dim[1] - border)
        self.ctx.clip()
        self.start_year = start_year
        self.end_year = end_year
        self.border = border

    def year_to_user(self, year):
        """Return coordinate in userspace for year."""
        return self.border + (1.0 - 2 * self.border) / (self.end_year -
                self.start_year) * (year - self.start_year)

    def draw_background(self, bg_color, bg_alpha):
        """Draw backgound on canvas"""
        self.ctx.save()
        self.ctx.set_source_rgba(*colors.hex2color(bg_color), bg_alpha)
        self.ctx.paint()
        self.ctx.restore()

    def draw_timeline(self, timeline_color, line_width, resolution, font, font_size):
        """Draw the timeline of the graph on the canvas."""
        dist_top = self.border + font_size + 8 * line_width
        self.ctx.save()
        self.ctx.set_source_rgb(*colors.hex2color(timeline_color))
        self.ctx.set_line_width(line_width)
        self.ctx.select_font_face(font)
        self.ctx.set_font_size(font_size)
        # Start Year
        self.ctx.move_to(self.border, dist_top)
        self.ctx.line_to(1.0 - self.border, dist_top)
        self.ctx.move_to(self.year_to_user(self.start_year) + 0.5 * line_width,
                dist_top - 7 * line_width)
        self.ctx.line_to(self.year_to_user(self.start_year) + 0.5 * line_width,
                dist_top + 7 * line_width)
        # Year markings
        for year in range(int(self.start_year / resolution) * resolution,
                self.end_year, resolution):
            if year % (5 * resolution) == 0:
                line_length = 5
                self.ctx.save()
                text_width = self.ctx.text_extents(str(year))[2]
                # Calculate x position
                x_pos = self.year_to_user(year) - 0.5 * text_width 
                # Move inwards if text extents to far
                if x_pos < self.border:
                    x_pos = x_pos + (self.border - x_pos)
                elif x_pos + text_width > (1 - self.border):
                    x_pos = x_pos + ((1 - self.border) - x_pos)
                self.ctx.move_to(x_pos, self.border + self.ctx.text_extents(str(year))[3])
                self.ctx.show_text(str(year))
                self.ctx.restore()
            else: # Unround years
                line_length = 2.5
            self.ctx.move_to(self.year_to_user(year),
                    dist_top - line_length * line_width)
            self.ctx.line_to(self.year_to_user(year),
                    dist_top + line_length * line_width)
        # End year
        self.ctx.move_to(self.year_to_user(self.end_year) - 0.5 * line_width,
                dist_top - 7 * line_width)
        self.ctx.line_to(self.year_to_user(self.end_year) - 0.5 * line_width,
                dist_top + 7 * line_width)
        self.ctx.stroke()
        self.ctx.restore()

    def draw_events(self, event_data, y_pos, dot_radius, event_color, font, font_size):
        """Draw the events to the canvas."""
        self.ctx.save()
        self.ctx.set_source_rgb(*colors.hex2color(event_color))
        self.ctx.set_line_width(dot_radius * 0.5)
        self.ctx.select_font_face(font)
        self.ctx.set_font_size(font_size)
        for event in event_data:
            try:
                # Draw dot for event
                self.ctx.arc(self.year_to_user(event['Year']), y_pos, dot_radius, 0, 2 * pi)
                self.ctx.stroke()
                # Add text
                self.ctx.move_to(self.year_to_user(event['Year']), y_pos - font_size)
                self.ctx.show_text(event['Name'])
                self.ctx.new_path()
            except TypeError:
                pass
        self.ctx.restore()

    def finish(self):
        """Finish surface"""
        self.surface.finish()

class SVGFile(Graph):
    """Class for a output as .svg file"""
    def __init__(self, filename, width, height, start_year, end_year, border):
        """Initialise surface and output"""
        self.surface = cairo.SVGSurface(filename + '.svg', width, height)
        self.setup(width, height, start_year, end_year, border)


def read_data(data_file_path):
    """Return data given by data_file_path.csv as list object"""
    with open(data_file_path, newline='') as data_file:
        csv_reader = csv.DictReader(data_file, quotechar='"',
                quoting=csv.QUOTE_NONNUMERIC)
        data_list = []
        for row in csv_reader:
            data_list.append(row)
    return data_list 

def read_config(config_file_path):
    """Return presets given by config_file_path or cli."""
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
    cli_parser.add_argument('--x-resolution',
            help='Vertical resolution of the output image',
            default=config['Output File']['x_resolution'], type=int)
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
    """Main function"""
    data = {}
    presets = read_config('config.cfg')
    for data_file_name in presets['File Paths']['data_files']:
        data[data_file_name[0:-4]] = read_data(presets['File Paths']['data_path']
                + data_file_name)

    output = SVGFile(presets['Output File']['file_name'],
            presets['Output File']['x_resolution'],
            presets['Output File']['y_resolution'], presets['Output']['start_year'],
            presets['Output']['end_year'], presets['Output']['border'])
    output.draw_background(presets['Colors']['background'],
            presets['Colors']['background_alpha'])
    output.draw_timeline(presets['Timeline']['color'],
            presets['Timeline']['line_width'], presets['Timeline']['resolution'],
            presets['Timeline']['font'], presets['Timeline']['font_size'])
    output.draw_events(data['events'], presets['Events']['y_pos'],
            presets['Events']['dot_size'], presets['Events']['color'],
            presets['Events']['font'], presets['Events']['font_size'])
    output.finish()

if __name__ == '__main__':
    main()
