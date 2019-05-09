#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017-2019 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Script to run the feels like temperature plugin."""

from improver.argparser import ArgParser
from improver.utilities.load import load_cube
from improver.utilities.save import save_netcdf
from improver.feels_like_temperature import calculate_feels_like_temperature


def main(argv=None):
    """ Load in the arguments for feels like temperature and ensure they are
    set correctly. Then calculate the feels like temperature using the data
    in the input cubes."""
    parser = ArgParser(
        description="This calculates the feels like temperature using a "
                    "combination of the wind chill index and Steadman's "
                    "apparent temperature equation.")
    parser.add_argument("temperature", metavar="TEMPERATURE",
                        help="Path to a NetCDF file of air temperatures at "
                        "screen level.")
    parser.add_argument("wind_speed", metavar="WIND_SPEED",
                        help="Path to the NetCDF file of wind speed at 10m.")
    parser.add_argument("relative_humidity", metavar="RELATIVE_HUMIDITY",
                        help="Path to the NetCDF file of relative humidity "
                        "at screen level.")
    parser.add_argument("pressure", metavar="PRESSURE",
                        help="Path to a NetCDF file of mean sea level "
                        "pressure.")
    parser.add_argument("output_filepath", metavar="OUTPUT_FILE",
                        help="The output path for the processed NetCDF")

    args = parser.parse_args(args=argv)

    temperature = load_cube(args.temperature)
    wind_speed = load_cube(args.wind_speed)
    relative_humidity = load_cube(args.relative_humidity)
    pressure = load_cube(args.pressure)

    result = calculate_feels_like_temperature(temperature, wind_speed,
                                              relative_humidity, pressure)
    save_netcdf(result, args.output_filepath)


if __name__ == "__main__":
    main()
