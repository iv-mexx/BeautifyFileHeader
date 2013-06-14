#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#   @author     Markus Chmelar
#   @date       2013-06-14
#   @version    1
# ------------------------------------------------------------------------------

'''
This script beautifies the file-headers of source files in a given path.
'''

# System Specific parameters and functions
import sys
# Operation Systems and Path Operations
import os
# Commandline Options parser
import optparse
# Logging
import logging
# Doc-Tests
import doctest
# JSON
import json
# Math
import math
# SourceFile
from SourceFile import SourceFile


def find_sources(folder_path,
                 extensions=['h', 'c', 'm', 'mm'],
                 ignore_patterns=None):
    '''Finds all source-files in the path that fit the extensions and
    ignore-patterns and returns their paths

    Keyword arguments:

        folder_path
            The path to the folder, all files in this folder will recursively
            be searched

        extensions
            Specifies which file extensions should be searched
            defaults to [h, c, m, mm]

        ignore_patterns
            If this parameter is different to None, files which path match the
            ignore pattern will be ignored

    Returns:

        Array with paths to all files that have to be used with genstrings

    Examples:

        >>> find_sources('TestInput')
        ['TestInput/main.m', 'TestInput/3rdParty/TestFlight.h', 'TestInput/Sources/IVCGAdditions.h', 'TestInput/Sources/Subfolder/LocalizationHandlerUtil.h', 'TestInput/Sources/Subfolder/LocalizationHandlerUtil.m']

        >>> find_sources('TestInput', ['m'])
        ['TestInput/main.m', 'TestInput/Sources/Subfolder/LocalizationHandlerUtil.m']

        >>> find_sources('TestInput', ['h'], ['3rdParty'])
        ['TestInput/Sources/IVCGAdditions.h', 'TestInput/Sources/Subfolder/LocalizationHandlerUtil.h']

        >>> find_sources('TestInput', ignore_patterns=['3rdParty'])
        ['TestInput/main.m', 'TestInput/Sources/IVCGAdditions.h', 'TestInput/Sources/Subfolder/LocalizationHandlerUtil.h', 'TestInput/Sources/Subfolder/LocalizationHandlerUtil.m']
    '''
    code_file_paths = []

    for dir_path, dir_names, file_names in os.walk(folder_path):
        ignorePath = False
        if ignore_patterns is not None:
            for ignore_pattern in ignore_patterns:
                if ignore_pattern in dir_path:
                    logging.debug('IGNORED Path: {}'.format(dir_path))
                    ignorePath = True
        if ignorePath is False:
            logging.debug('DirPath: {}'.format(dir_path))
            for file_name in file_names:
                extension = file_name.rpartition('.')[2]
                if extension in extensions:
                    code_file_path = os.path.join(dir_path, file_name)
                    code_file_paths.append(code_file_path)
    logging.info('Found %d files', len(code_file_paths))
    return code_file_paths


def run(file_paths):
    '''
    Runs the Beautifier on all given files
    '''
    for file_path in file_paths:
        sf = SourceFile(file_path)
        sf.process_file()


def main():
    ''' Parse the command line and execute the programm with the parameters '''

    parser = optparse.OptionParser(
        'usage: %prog [options] [input file] [output file]'
    )
    parser.add_option(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Show debug messages'
    )
    parser.add_option(
        '',
        '--unittests',
        action='store_true',
        dest='unittests',
        default=False,
        help='Run unit tests (debug)'
    )
    parser.add_option(
        '--ignore',
        action='append',
        dest='ignore_patterns',
        default=None,
        help='Ignore Paths that match the patterns'
    )
    parser.add_option(
        '--extension',
        action='append',
        dest='extensions',
        default=['c', 'h', 'm'],
        help='File-Extensions that should be scanned'
    )

    (options, args) = parser.parse_args()

    # Create Logger
    logging.basicConfig(
        format='%(message)s',
        level=options.verbose and logging.DEBUG or logging.INFO
    )

    # Run Unittests/Doctests
    if options.unittests:
        doctest.testmod()
        return

    file_paths = find_sources('.', options.extensions, options.ignore_patterns)
    run(file_paths)

    return 0


if __name__ == '__main__':
    sys.exit(main())
