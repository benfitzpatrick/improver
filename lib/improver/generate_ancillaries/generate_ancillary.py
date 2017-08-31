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
"""Module containing ancillary generation utilities for Improver"""

import iris
import numpy as np
from glob import glob


def _make_mask_cube(mask_data, key, coords, topographic_bounds):
    """
    Makes cube from numpy masked array generated from orography fields.

    Parameters
    ----------
    mask_data : numpy masked array
        The numpy array to make a cube from.
    key : string
        Key from THRESHOLD_DICT which describes type of topography band.
    coords : dictionary
        Dictionary of coordinate on the model ancillary file.
    topographic_bounds: list
        List containing the lower and upper thresholds defining the mask

    Returns
    -------
    mask_cube : cube
        Cube containing the mask_data array, with appropriate coordinate
        and attribute information.
    """
    mask_cube = iris.cube.Cube(mask_data, long_name='Topography mask')
    if any([item is None for item in topographic_bounds]):
        msg = ("The topographic bounds variable should have both an "
               "upper and lower limit: "
               "Your topographic_bounds are {}")
        raise TypeError(msg.format(topographic_bounds))
    elif len(topographic_bounds) != 2:
        msg = ("The topographic bounds variable should have only an "
               "upper and lower limit: "
               "Your topographic_bounds variable has length {}")
        raise TypeError(msg.format(len(topographic_bounds)))
    else:
        coord_name = 'topographic_zone'
        central_point = np.mean(topographic_bounds)
        threshold_coord = iris.coords.AuxCoord(central_point,
                                               bounds=topographic_bounds,
                                               long_name=coord_name)
        mask_cube.add_aux_coord(threshold_coord)
    mask_cube.attributes['Topographical Type'] = key.title()
    for coord in coords:
        if coord.name() in ['projection_y_coordinate', 'latitude']:
            mask_cube.add_dim_coord(coord, 0)
        elif coord.name() in ['projection_x_coordinate', 'longitude']:
            mask_cube.add_dim_coord(coord, 1)
        else:
            mask_cube.add_aux_coord(coord)
    mask_cube = iris.util.new_axis(mask_cube, scalar_coord=coord_name)
    return mask_cube


def find_standard_ancil(standard_ancil_glob, msg=None):
    """
    Reads standard ancillary or raises exception.

    Parameters
    -----------
    standard_ancil_glob : string
      Location of input ancillaries

    msg : str
      Optional custom message.

    Returns
    --------
    standard_ancil : cube
        Cube containing standard ancillary data.

    Raises
    -------
    IOError: if input ancillary cannot be found in the directory provided.
    """
    standard_ancil_file = glob(standard_ancil_glob)
    if len(standard_ancil_file) > 0:
        standard_ancil = iris.load_cube(standard_ancil_file[0])
    else:
        if msg is None:
            msg = ('Cannot find input ancillary. Tried directory: '
                   '{}'.format(standard_ancil_glob))
        raise IOError(msg)
    return standard_ancil


class CorrectLandSeaMask(object):
    """
    Round landsea mask to binary values

    Corrects interpolated land sea masks to boolean values of
    False [sea] and True [land].
    """
    def __init__(self):
        pass

    def __repr__(self):
        """Represent the configured plugin instance as a string"""
        result = ('<CorrectLandSeaMask>')
        return result

    @staticmethod
    def process(standard_landmask):
        """Read in the interpolated landmask and round values < 0.5 to False
             and values >=0.5 to True.

        Parameters
        ----------
        standard_landmask:
            input landmask on standard grid.

        Returns
        -------
        standard_landmask : cube
            output landmask of boolean values.
        """
        mask_sea = np.ma.masked_less(standard_landmask.data, 0.5).mask
        standard_landmask.data[mask_sea] = False
        mask_land = np.ma.masked_greater(standard_landmask.data, 0.).mask
        standard_landmask.data[mask_land] = True
        return standard_landmask


class GenerateOrographyBandAncils(object):
    """
    Generate topographic band ancillaries for the standard grids.

    Reads orography files, then generates binary mask
    of land points within the orography band specified.
    """
    def __init__(self):
        pass

    def __repr__(self):
        """Represent the configured plugin instance as a string."""
        result = ('<GenerateOrographyBandAncils>')
        return result

    @staticmethod
    def gen_orography_masks(
            standard_orography, standard_landmask, key, thresholds):
        """
        Function to generate topographical band masks.

        For each threshold defined in 'thresholds', a cube containing a masked
        array will be generated. This array will be masked over sea
        points and will have values of 0 or 1 on land points, depending on
        whether the given point's orography value falls between the thresholds.

        For example, for threshold pair: [1,3] with
        orography: [[0 0 2]    and      sea mask: [[-- -- 2]
                    [1 2 1]                        [1  2  1]
                    [0 1 4]]                       [-- 1  4]]

        the resultant array will be: [[-- -- 1]
                                      [0  1  0]
                                      [-- 0  0]]

        Parameters
        -----------
        standard_orography : cube
            The standard orography.
        standard_landmask : cube
            The landmask generated by gen_landmask.
        key : string
            Key from THRESHOLD_DICT which describes type of topography band.
        thresholds: list
            Upper and/or lower thresholds of the current topographical band.

        Returns
        -------
        mask_cube : cube
            Cube containing topographical band mask.

        Raises
        ------
        KeyError: if the key does not match any in THRESHOLD_DICT.
        """

        def sea_mask(landmask, orog_band):
            """
            Function to mask sea points and substitute the default numpy
            fill value behind this mask_cube.

            Parameters
            ----------
            landmask : numpy array
                The landmask generated by gen_landmask.
            orog_band : numpy array
                The binary array to which the landmask will be applied.
            """
            mask_data = np.ma.masked_where(
                np.logical_not(landmask), orog_band)
            sea_fillvalue = np.ma.default_fill_value(mask_data.data)
            mask_data.data[mask_data.mask] = sea_fillvalue
            return mask_data

        coords = standard_orography.coords()
        if key == 'land':  # regular topographical bands above land
            old_threshold, threshold = thresholds
            orog_band = np.ma.masked_inside(
                standard_orography.data, old_threshold,
                threshold).mask.astype(int)
            if not isinstance(orog_band, np.ndarray):
                orog_band = np.zeros(standard_orography.data.shape).astype(int)
            mask_data = sea_mask(standard_landmask.data, orog_band)
            mask_cube = _make_mask_cube(
                mask_data, key, coords, topographic_bounds=thresholds)
        else:
            msg = 'Unknown threshold_dict key: {}'
            raise KeyError(msg.format(key))
        return mask_cube

    @staticmethod
    def process(orography, landmask, thresholds_dict):
        """Loops over the supplied orographic bands, adding a cube
           for each band to the mask cubelist.

        Parameters
        ----------
        orography : cube
          orography on standard grid.

        landmask : cube
          land mask on standard grid.

        threshold_dict : dictionary
          definition of orography bands required.

        Returns
        -------
        cubelist : cubelist
          list of orographic band mask cubes.
        """
        cubelist = iris.cube.CubeList()
        for dict_key, dict_bound in thresholds_dict.items():
            if len(dict_bound) == 0:
                msg = 'No threshold(s) found for topographic type: {}'
                raise ValueError(msg.format(dict_key))
            for limits in dict_bound:
                oro_band = GenerateOrographyBandAncils.gen_orography_masks(
                    orography, landmask, dict_key, limits)
                cubelist.append(oro_band)
        return cubelist
