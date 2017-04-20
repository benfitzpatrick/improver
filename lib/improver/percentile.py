# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017 Met Office.
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
"""Module containing percentiling classes."""


import iris


class PercentileConverter(object):

    """Plugin for converting from a set of values to a PDF.

    Generate percentiles together with min, max, mean, stdev.

    """

    # The actual percentage points we calculate at.
    PERCENTILES = [5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95]

    def __init__(self, collapse_coord):
        """Create a PDF plugin with a given source plugin.

        Parameters
        ----------
        collapse_coord : str or list of str
            The name of the coordinate(s) to collapse over.

        """
        self.collapse_coord = collapse_coord
        if not isinstance(collapse_coord, (basestring, iris.coords.Coord)):
            raise ValueError('collapse_coord is {!r}, which does not specify '
                             'a single coordinate.'.format(collapse_coord))

    def process_percentiles(self, cube):
        """
        Create a cube containing the percentiles as a new dimension.

        Parameters
        ----------
        cube : iris.cube.Cube instance
            The cube returned by the "upstream" plugin.

        Returns
        -------
        Cube
            A single merged cube of all the cubes produced by each percentile
            collapse.

        """
        return cube.collapsed(self.collapse_coord,
                              iris.analysis.PERCENTILE,
                              percent=self.PERCENTILES)

    def process(self, cube):
        """Generate the percentiles and other info for the source cube.

        What's generated is:
            * 13 percentiles
              (5%, 10%, 20%, 25%, 30%, 40%, 50%, 60%, 70%, 75%, 80%, 90%, 95%),
            * lower and upper bounds, (i.e. min and max) and
            * mean and standard deviation.

        Parameters
        ----------
        cube : iris.cube.Cube instance
            Given the collapse coordinate, convert the set of values
            along that coordinate into a PDF and extract percentiles
            and min, max, mean, stdev.

        Returns
        -------
        List of cubes : iris.cube.CubeList
            A list of cubes collapsed from the source cube, one for all
            percentiles and one for each of the other elements of the PDF.

        """
        pdf_cubes = iris.cube.CubeList()

        percentiles_cube = self.process_percentiles(cube)
        pdf_cubes.append(percentiles_cube)
        pdf_cubes.append(cube.collapsed(self.collapse_coord,
                                        iris.analysis.MIN))
        pdf_cubes.append(cube.collapsed(self.collapse_coord,
                                        iris.analysis.MAX))
        pdf_cubes.append(cube.collapsed(self.collapse_coord,
                                        iris.analysis.MEAN))
        pdf_cubes.append(cube.collapsed(self.collapse_coord,
                                        iris.analysis.STD_DEV))
        return pdf_cubes
