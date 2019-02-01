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
"""Common option utilities for improver CLIs."""

from argparse import ArgumentParser
from improver.profile import profile_hook_enable


class ArgParser(ArgumentParser):
    """Argument parser for improver CLIs.

    The main purpose of this class is to make it easier to create CLIs which
    have arguments which are selected from centralized collections.

    To fulfil these requirements, we define 2 class level dictionaries,
    ArgParser.CENTRALIZED_ARGUMENTS, and ArgParser.COMPULSORY_ARGUMENTS.

    For these dictionaries, each element has:
        - a key, which is a string representing the argument name - used
          internally to refer to a particular argument (which, in the case of
          the CENTRALIZED_ARUGMENTS may be selected from when creating an
          instance of the ArgParser)
        - a value, which is a list containing 2 elements:
            1. a list of strings containing the different flags which are
               associated with the argument (ie.: the first argument to the
               add_arguments() method, e.g: ['--profile', '-p'])
            2. a dictionary containing all of the kwargs which are passed
               to the add_argument() method (e.g:
               {'action': 'store_true', 'default': False, 'help': ... })

    The CENTRALIZED_ARGUMENTS will be selected from, as necessary, for each
    of the CLIs that we create, and the COMPULSORY_ARGUMENTS will be
    automatically added to all CLIs (with no option to exclude them).

    ArgParser.DEFAULT_CENTRALIZED_ARG_NAMES defines the centralized arguments
    which are to be included by default when creating instances of this
    class (i.e: when nothing is explictly passed
    into the constructor). This is a tuple containing keys associated with the
    ArgParser.CENTRALIZED_ARGUMENTS dictionary.
    """

    # Ideally, all CLIs should select something from this dictionary:
    # NB: --help included by default with ArgumentParser
    CENTRALIZED_ARGUMENTS = {
        'alpha_x': (
            '--alpha_x',
            {'metavar': 'ALPHA_X_FACTOR_OR_FILEPATH',
             'default': 0.8,
             'help': 'A single alpha factor (0 < alpha_x < 1) to be applied '
                     'to every grid square in the x direction when applying '
                     'the recursive filter (on by default for square '
                     'kernels), or a path to a NetCDF file specifying the '
                     'equivalent for each grid square. The alpha parameter '
                     '(0 < alpha < 1) controls what proportion of the '
                     'probability is passed onto the next grid-square in the '
                     'x and y directions.'}
        ),
        'alpha_y': (
            '--alpha_y',
            {'metavar': 'ALPHA_Y_FACTOR_OR_FILEPATH',
             'default': 0.8,
             'help': 'A single alpha factor (0 < alpha_y < 1) to be applied '
                     'to every grid square in the y direction when applying '
                     'the recursive filter (on by default for square '
                     'kernels), or a path to a NetCDF file specifying the '
                     'equivalent for each grid square. The alpha parameter '
                     '(0 < alpha < 1) controls what proportion of the '
                     'probability is passed onto the next grid-square in the '
                     'x and y directions.'}
        ),
        'coord_for_masking': (
            '--coord_for_masking',
            {'metavar': 'COORD_FOR_MASKING',
             'help': 'Coordinate to iterate over when applying a mask to the '
                     'neighbourhood processing.'}
        ),
        'coords_to_collapse': (
            '--coordinates',
            {'metavar': 'COORDINATES_TO_COLLAPSE',
             'nargs': '+',
             'help': 'Coordinate or coordinates over which to collapse data '
                     'and calculate percentiles; e.g. "realization" or '
                     '"latitude longitude". This argument must be provided '
                     'when collapsing a coordinate or coordinates to create '
                     'percentiles, but is redundant when converting '
                     'probabilities to percentiles and may be omitted. This '
                     'coordinate(s) will be removed and replaced by a '
                     'percentile coordinate.'}
        ),
        'degrees_as_complex': (
            '--degrees_as_complex',
            {'action': 'store_true',
             'default': False,
             'help': 'Set this flag to process angles, e.g. wind directions, '
                     'as complex numbers. Not compatible with circular '
                     'or circular weighted kernels or recursive filter.'}
        ),
        'ecc_bounds_warning': (
            '--ecc_bounds_warning',
            {'action': 'store_true',
             'default': False,
             'help': 'If True, where calculated percentiles are outside the '
                     'ECC bounds range, raise a warning rather than an '
                     'exception.'}
        ),
        'halo_radius': (
            '--halo_radius',
            {'default': None,
             'metavar': 'HALO_RADIUS',
             'type': float,
             'help': 'radius in metres of excess halo to clip. '
                     'Used where a larger grid was defined than the standard '
                     'grid and we want to clip the grid back to the standard '
                     'grid e.g. for global data regridded to UK area. '
                     'Default=None'}
        ),
        'input_filepath': (
            'input_filepath',
            {'metavar': 'INPUT_FILE',
             'help': 'A path to an input NetCDF file to be processed'}),
        'input_mask_collapse_weights_filepath': (
            '--input_mask_collapse_weights_filepath',
            {'metavar': 'INPUT_MASK_WEIGHTS_FILE',
             'default': None,
             'help': 'A path to an weights NetCDF file containing the weights '
                     'which are used for collapsing the dimension gained '
                     'through masking. If not given, the mask dimension will '
                     'not be collapsed.'}
        ),
        'input_mask_filepath': (
            '--input_mask_filepath',
            {'metavar': 'INPUT_MASK_FILE',
             'help': 'A path to an input mask NetCDF file to be used to mask '
                     'the input file. This is currently only supported for '
                     'square neighbourhoods. The data should contain 1 for '
                     'usable points and 0 for discarded points, e.g. a '
                     'land-mask.'}
        ),
        'input_landsea_mask_filepath': (
            '--input_landsea_mask_filepath',
            {'metavar': 'LANDSEA_FILE',
             'help': 'A path to an input logical mask NetCDF file to be used '
                     'to distinguish land (True) from sea (False).'}
        ),
        'iterations': (
            '--iterations',
            {'metavar': 'ITERATIONS',
             'default': 1,
             'type': int,
             'help': 'Number of times to apply the filter, default=1 '
                     '(typically < 5).'}
        ),
        'kernel': (
            '--kernel',
            {'metavar': 'NEIGHBOURHOOD_KERNEL',
             'choices': ['circular', 'circular_weighted', 'square'],
             'default': 'square',
             'help': 'The shape of the neighbourhood to apply in '
                     'neighbourhood processing. Options: "circular", '
                     '"circular_weighted", "square" (default). The '
                     'circular_weighted kernel differs from the circular by '
                     'having a weighting that decreases with radial distance. '
                     'Only the square kernel supports the full range of '
                     'options like masking, complex number processing, and '
                     'sum or fraction.'}
        ),
        'no_collapse_mask': (
            '--no-collapse-mask',
            {'action': 'store_true',
             'help': 'Do not collapse the dimension from the mask '
                     'coordinate.'}
        ),
        'no_of_percentiles': (
            '--no-of-percentiles',
            {'default': None,
             'type': int,
             'metavar': 'NUMBER_OF_PERCENTILES',
             'help': 'Optional definition of the number of percentiles '
                     'to be generated, these distributed regularly with the '
                     'aim of dividing into blocks of equal probability.'}
        ),
        'no_recursive_filter': (
            '--no-recursive-filter',
            {'action': 'store_true',
             'default': False,
             'help': 'Do not apply the recursive filter, when using square '
                     'neighbourhood kernel.'}
        ),
        'output_filepath': (
            'output_filepath',
            {'metavar': 'OUTPUT_FILE',
             'help': 'The output path for the processed NetCDF'}
        ),
        'percentiles': (
            '--percentiles',
            {'default': None,
             'metavar': 'PERCENTILES',
             'nargs': '+',
             'type': float,
             'help': 'Optional definition of percentiles at which to '
                     'calculate data, e.g. --percentiles 0 33.3 66.6 100'}
        ),
        'radius': (
            '--radius',
            {'metavar': 'RADIUS_OR_RADII',
             'type': 'self.parse_float_list_type',
             'help': 'The radius (in m) for neighbourhood processing.'
                     'Multiple radii can be given, comma separated, to '
                     'correspond with lead times in --radii-lead-times.'}
        ),
        'radius_required': (
            '--radius',
            {'metavar': 'RADIUS_OR_RADII',
             'type': 'self.parse_float_list_type',
             'required': True,
             'help': 'The radius (in m) for neighbourhood processing.'
                     'Multiple radii can be given, comma separated, to '
                     'correspond with lead times in --radii-lead-times.'}
        ),
        'radii_lead_times': (
            '--radii_lead_times',
            {'metavar': 'LEAD_TIMES',
             'type': 'self.parse_lead_time_list_type',
             'help': 'Comma separated list of lead times at which each radius '
                     'given in --radius is valid. Lead times should be given '
                     'in PTxH where x is an integer number of hours - for '
                     'example, PT12H or PT144H. A --radii-lead-times value '
                     'of "PT0H,PT12H,PT36H" with --radius value of '
                     '"8000,32000,44000" would mean that a file with a '
                     'forecast period lead time of 0 hours would use a '
                     'radius of 8km, a file with a forecast period lead time '
                     'of 12 hours would use a radius of 32km, and a lead '
                     'time of 36 hours would use a radius of 44km, with all '
                     'other lead time values within and outside those bounds '
                     'using a linearly interpolated radius.'}
        ),
        'sum_or_fraction': (
            '--sum_or_fraction',
            {'default': 'fraction',
             'choices': ['sum', 'fraction'],
             'help': 'The neighbourhood output can either be in the form of '
                     'a sum of the neighbourhood, or a fraction calculated '
                     'by dividing the sum of the neighbourhood by the '
                     'neighbourhood area. "fraction" is the default option.'}
        ),
    }

    # *All* CLIs will use the options here (no option to disable them):
    COMPULSORY_ARGUMENTS = {
        'profile': (
            '--profile',
            {'action': 'store_true',
             'help': 'Switch on profiling information.'}),
        'profile_file': (
            '--profile_file',
            {'metavar': 'PROFILE_FILE',
             'help': 'Dump profiling info to a file. Implies --profile.'})
    }

    # We can override including these, but options common to everything should
    # be in a list here:
    # DEFAULT_CENTRALIZED_ARG_NAMES = ('input_file', 'output_file')
    DEFAULT_CENTRALIZED_ARG_NAMES = ()

    def __init__(self, central_arguments=DEFAULT_CENTRALIZED_ARG_NAMES,
                 specific_arguments=None, exclusive_groups=None, **kwargs):
        """Create an ArgParse instance, which is a subclass of
        argparse.ArgumentParser and automatically add all of the arguments.
        (Note: The ArgParse.COMPULSORY_ARGUMENTS are always added.)

        Args:
            central_arguments (list):
                A list containing the centralized arguments we require.
                (Keys of the centralized argument dictionary). By default this
                is set as ArgParse.DEFAULT_CENTRALIZED_ARG_NAMES.
            specific_arguments (list):
                A list of argument specifications required to add arguments
                which are not contained within the centralized argument
                dictionary. The format of these argument specifications should
                be the same as the values in the
                ArgParser.CENTRALIZED_ARGUMENTS dictionary.
                (For more details, see the add_arguments method).
                Default is None, which does not add additional arguments.
            exclusive_groups (list of lists):
                A list of items which are sets or lists of exclusive arguments
                following the argparse add_mutually_exclusive_group
                functionality.
            kwargs (dictionary):
                Additional keyword arguments which are passed to the superclass
                constructor (argparse.ArgumentParser), e.g: the `description`
                of the ArgumentParser.
        """

        # Allow either central_arguments or specific_arguments to be None
        # (or empty lists)
        if central_arguments is None:
            central_arguments = []
        if specific_arguments is None:
            specific_arguments = []

        if exclusive_groups is None:
            exclusive_groups = []

        # argspecs of the compulsory arguments (no switch here)
        compulsory_arguments = list(ArgParser.COMPULSORY_ARGUMENTS.values())

        # get argspecs of the central arguments from the list of keys passed in
        central_arguments = [ArgParser.CENTRALIZED_ARGUMENTS[arg_name] for
                             arg_name in central_arguments]

        for index, group in enumerate(exclusive_groups):
            new_group = [ArgParser.CENTRALIZED_ARGUMENTS.get(_) for _ in
                         group if isinstance(_, str)]
            exclusive_groups[index] = new_group

        # create instance of ArgumentParser (pass along kwargs)
        super(ArgParser, self).__init__(**kwargs)

        # all arguments
        cli_arguments = (compulsory_arguments + central_arguments +
                         specific_arguments)

        # automatically add all of the arguments
        self.add_arguments(cli_arguments, exclusive_groups)
        # Done. Now we can get the arguments with self.parse_args()

    def add_arguments(self, argspec_list, exclusive_groups):
        """Adds a list of arguments to the ArgumentParser.

        The input argspec_list is a list of argument specifications, where each
        element (argument specification) is a tuple/list of length 2.
        The first element of an argument specification is a string or a list
        of strings which are the name/flags used to add the argument.
        The second element of the argument spec shall be a dictionary
        containing the keyword arguments which are passed into the
        add_argument() method.

        Args:
            argspec_list (list or string):
                A list or string containing the specifications required to add
                the arguments (see above)
            exclusive_groups (list of lists):
                A list of lists of argspec-like items. Each list of argspec
                items corresponds to an argparse add_mutually_exclusive_group
                functionality.

        Raises:
            AttributeError:
                Notifies the user if any of the argument specifications has
                the wrong length (not 2).
        """
        argspec_groups = {}
        for exclusive_group in exclusive_groups:
            group = self.add_mutually_exclusive_group()
            for argspec_flags, argspec_kwargs in exclusive_group:
                if isinstance(argspec_flags, str):
                    argspec_flags = [argspec_flags]
                argspec_groups[argspec_flags[0]] = group
        print("argspec groups", argspec_groups)
        for argspec in argspec_list:
            if len(argspec) != 2:
                raise AttributeError(
                    "The argument specification has an unexpected length. "
                    "Each argument specification should be a 2-tuple, of a "
                    "list (of strings) and a dictionary.")
            argflags, argkwargs = argspec
            if isinstance(argflags, str):
                argflags = [argflags]
            argtype = argkwargs.get('type')
            if isinstance(argtype, str) and argtype.startswith('self.'):
                argtype = argtype.replace('self.', '')
                argkwargs['type'] = getattr(self, argtype,
                                            argkwargs['type'])
            # Add the argument to either a mutually exclusive group, or just
            # self.
            target = argspec_groups.get(argflags[0], self)
            print("argspec", argflags[0], "target", target)
            target.add_argument(*argflags, **argkwargs)

    def parse_args(self, args=None, namespace=None):
        """Wrap in order to implement some compulsory behaviour."""
        args = super(ArgParser, self).parse_args(args=args,
                                                 namespace=namespace)
        if hasattr(args, 'profile') and (args.profile or args.profile_file):
            profile_hook_enable(dump_filename=args.profile_file)
        return args

    def wrong_args_error(self, args, method):
        """Raise a parser error.

        Some CLI scripts have multiple methods of carrying out an action, with
        each method having different arguments. This method provides a
        standard error to be used when incompatible method-argument
        combinations are passed in - ie: when there are mutually exclusive
        groups of arguments.

        Args:
            args (string):
                The incompatible arguments
            method (string):
                The method with which the arguments are incompatible

        Raises:
            parser.error:
                To notify user of incompatible method-argument
                combinations.
        """
        msg = 'Method: {} does not accept arguments: {}'
        self.error(msg.format(method, args))

    @staticmethod
    def parse_float_list_type(value):
        """Parse a comma separated list of floats."""
        try:
            return [float(_) for _ in value.split(",")]
        except ValueError:
            raise argparse.ArgumentTypeError

    @staticmethod
    def parse_lead_time_list_type(value):
        """Parse a comma separated list of PTxH, x integer number of hours.

        For example, PT1H or PT1H,PT2H,PT12H.

        """
        import re
        lead_times = []
        for item in value.split(","):
            match = re.match(r"PT(\d+)H$", value)
            if match is None:
                raise argparse.ArgumentTypeError
            lead_times.append(float(match.groups()[0]))
        return lead_times

def safe_eval(command, module, allowed):
    """
    A wrapper for the python eval() function that enforces the use of a list of
    allowable commands and excludes python builtin functions. This enables the
    use of an eval statement to convert user string input into a function or
    method without it being readily possible to trigger malicious code.

    Args:
        command (string):
            A string identifying the function/method/object that is to be
            returned from the provided module.
        module (module):
            The python module from within which the function/method/object is
            to be found.
        allowed (list):
            A list of the functions/methods/objects that the user is allowed to
            request.
    Returns:
        function/method/object:
            The desired function, method, or object.
    Raises:
        TypeError if the requested module component is not allowed or does not
        exist.
    """
    no_builtins = {"__builtins__": None}
    safe_dict = {k: module.__dict__.get(k, None) for k in allowed}

    try:
        result = eval('{}'.format(command), no_builtins, safe_dict)
    except TypeError:
        raise TypeError(
            'Function/method/object "{}" not available in module {}.'.format(
                command, module.__name__))
    return result
