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
"""Unit tests for the percentile.PercentileConverter plugin."""


import unittest

import iris
import iris.cube
from iris.coords import DimCoord
from iris.tests import IrisTest
import numpy as np

from improver.percentile import PercentileConverter


def _make_cube():
    """Make a test cube."""
    data = np.arange(36).reshape(3, 3, 4)
    cube = iris.cube.Cube(data, "air_pressure_at_sea_level", units="Pa")
    cube.add_dim_coord(DimCoord([0, 1, 2], 'realization', units=1), 0)
    cube.add_dim_coord(DimCoord([-45, 10, 25], 'latitude', units='degrees'), 1)
    cube.add_dim_coord(
        DimCoord([50, 100, 120, 180], 'longitude', units='degrees'), 2)
    return cube


class TestPercentiles(IrisTest):

    """Test the creation of percentiles by the plugin."""

    def test_basic(self):
        """Create and test percentiles."""
        plugin = PercentileConverter('realization')
        percentiles_result = plugin.process(_make_cube())
        self.assertIsInstance(percentiles_result, iris.cube.Cube)
        coord_names = [c.name() for c in percentiles_result.coords()]
        print percentiles_result, type(percentiles_result)
        name = 'percentile_over_realization'
        self.assertIn(name, coord_names)
        percentiles_coord = percentiles_result.coord(name)
        percentiles = [5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95]
        self.assertArrayEqual(percentiles_coord.points, percentiles)
        self.assertArrayAlmostEqual(percentiles_result[:3, 0, 0].data,
                                    [1.2, 2.4, 4.8])


if __name__ == '__main__':
    unittest.main()