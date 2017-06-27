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
""" Tests to support utilities."""

import unittest

from cf_units import Unit
import iris
from iris.cube import Cube
from iris.coords import AuxCoord, CellMethod, DimCoord
from iris.exceptions import InvalidCubeError
from iris.tests import IrisTest
import numpy as np
from numpy import ma

from improver.utilities.spatial import (
    DiscreteDifferenceBetweenAdjacentGridSquares)


def set_up_cube(data, phenomenon_standard_name, phenomenon_units,
                realizations=np.array([0]), timesteps=1,
                y_dimension_length=3, x_dimension_length=3):
    """Create a cube containing multiple realizations."""
    cube = Cube(data, standard_name=phenomenon_standard_name,
                units=phenomenon_units)
    cube.add_aux_coord(AuxCoord(realizations, 'realization',
                                units='1'))
    time_origin = "hours since 1970-01-01 00:00:00"
    calendar = "gregorian"
    tunit = Unit(time_origin, calendar)
    cube.add_aux_coord(AuxCoord(np.linspace(402192.5, 402292.5, timesteps),
                                "time", units=tunit))
    cube.add_dim_coord(DimCoord(np.linspace(0, 10000, y_dimension_length),
                                'projection_y_coordinate', units='m'), 0)
    cube.add_dim_coord(DimCoord(np.linspace(0, 10000, x_dimension_length),
                                'projection_x_coordinate', units='m'), 1)
    return cube


class Test_create_discrete_difference_cube(IrisTest):

    """Test the create_discrete_difference_cube method."""

    def setUp(self):
        """Set up cube."""
        data = np.array([[1, 2, 3],
                         [2, 4, 6],
                         [5, 10, 15]])
        self.cube = set_up_cube(data, "wind_speed", "m s-1")
        self.plugin = DiscreteDifferenceBetweenAdjacentGridSquares()

    def test_y_dimension(self):
        """Test discrete differences calculated along the y dimension."""
        input_array = np.array([[1, 2, 3],
                                [3, 6, 9]])
        result = self.plugin.create_discrete_difference_cube(
            self.cube, "projection_y_coordinate", input_array)
        self.assertIsInstance(result, Cube)
        self.assertArrayAlmostEqual(result.data, input_array)

    def test_x_dimension(self):
        """Test discrete differences calculated along the x dimension."""
        input_array = np.array([[1, 1],
                                [2, 2],
                                [5, 5]])
        result = self.plugin.create_discrete_difference_cube(
            self.cube, "projection_x_coordinate", input_array)
        self.assertIsInstance(result, Cube)
        self.assertArrayAlmostEqual(result.data, input_array)

    def test_metadata(self):
        """Test that the result has the expected metadata."""
        input_array = np.array([[1, 2, 3],
                                [3, 6, 9]])
        cell_method = CellMethod(
            "discrete_difference", coords=["projection_y_coordinate"])
        result = self.plugin.create_discrete_difference_cube(
            self.cube, "projection_y_coordinate", input_array)
        self.assertEqual(
            result.cell_methods[0], cell_method)
        self.assertEqual(
            result.attributes["direction_of_discrete_difference"],
            "forward_difference")

    def test_othercoords(self):
        """Test that other coords are transferred properly"""
        input_array = np.array([[1, 2, 3],
                                [3, 6, 9]])
        time_coord = self.cube.coord('time')
        proj_x_coord = self.cube.coord(axis='x')
        result = self.plugin.create_discrete_difference_cube(
            self.cube, "projection_y_coordinate", input_array)
        self.assertEqual(result.coord(axis='x'), proj_x_coord)
        self.assertEqual(result.coord('time'), time_coord)


class Test_calculate_discrete_difference(IrisTest):

    """Test the calculate_discrete_difference method."""

    def setUp(self):
        """Set up cube."""
        data = np.array([[1, 2, 3],
                         [2, 4, 6],
                         [5, 10, 15]])
        self.cube = set_up_cube(data, "wind_speed", "m s-1")
        self.plugin = DiscreteDifferenceBetweenAdjacentGridSquares()

    def test_x_dimension(self):
        """Test discrete differences calculated along the x dimension."""
        expected = np.array([[1, 1],
                             [2, 2],
                             [5, 5]])
        result = self.plugin.calculate_discrete_difference(self.cube, "x")
        self.assertIsInstance(result, Cube)
        self.assertArrayAlmostEqual(result.data, expected)

    def test_y_dimension(self):
        """Test discrete differences calculated along the y dimension."""
        expected = np.array([[1, 2, 3],
                             [3, 6, 9]])
        result = self.plugin.calculate_discrete_difference(self.cube, "y")
        self.assertIsInstance(result, Cube)
        self.assertArrayAlmostEqual(result.data, expected)

    def test_missing_data(self):
        """Test that the result is as expected when data is missing."""
        data = np.array([[1, 2, 3],
                         [np.nan, 4, 6],
                         [5, 10, 15]])
        cube = set_up_cube(data, "wind_speed", "m s-1")
        expected = np.array([[np.nan, 2, 3],
                             [np.nan, 6, 9]])
        result = self.plugin.calculate_discrete_difference(cube, "y")
        self.assertIsInstance(result, Cube)
        self.assertArrayAlmostEqual(result.data, expected)

    def test_masked_data(self):
        """Test that the result is as expected when data is masked."""
        data = ma.array([[1, 2, 3],
                         [2, 4, 6],
                         [5, 10, 15]],
                        mask=[[0, 0, 0],
                              [1, 0, 0],
                              [0, 0, 0]])
        cube = set_up_cube(data, "wind_speed", "m s-1")
        expected = ma.array([[1, 2, 3],
                             [3, 6, 9]],
                            mask=[[1, 0, 0],
                                  [1, 0, 0]])
        result = self.plugin.calculate_discrete_difference(cube, "y")
        self.assertIsInstance(result, Cube)
        self.assertArrayEqual(result.data, expected)
        self.assertArrayEqual(result.data.mask, expected.mask)


class Test_process(IrisTest):

    """Test the process method."""

    def setUp(self):
        """Set up cube."""
        data = np.array([[1, 2, 3],
                         [2, 4, 6],
                         [5, 10, 15]])
        self.cube = set_up_cube(data, "wind_speed", "m s-1")
        self.plugin = DiscreteDifferenceBetweenAdjacentGridSquares()

    def test_basic(self):
        """Test that discrete differences are calculated along both the x and
        y dimensions and returned as separate cubes."""
        expected_x = np.array([[1, 1],
                              [2, 2],
                              [5, 5]])
        expected_y = np.array([[1, 2, 3],
                               [3, 6, 9]])
        result = self.plugin.process(self.cube)
        self.assertIsInstance(result[0], Cube)
        self.assertArrayAlmostEqual(result[0].data, expected_x)
        self.assertIsInstance(result[1], Cube)
        self.assertArrayAlmostEqual(result[1].data, expected_y)

    def test_invalid_cube_error(self):
        """Test that the correct exception is raised when the input cube has
        too many dimensions."""
        self.cube = iris.util.new_axis(self.cube, "realization")
        msg = "The input cube must have two dimensions"
        with self.assertRaisesRegexp(InvalidCubeError, msg):
            self.plugin.process(self.cube)


if __name__ == '__main__':
    unittest.main()
