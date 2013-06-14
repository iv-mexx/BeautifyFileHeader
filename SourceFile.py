#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#   @author     Markus Chmelar
#   @date       2013-06-14
#   @version    1
# ------------------------------------------------------------------------------

'''
This class represents a source file and provides the functionality to beautify
its file-header
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
# Regular Expressions
import re
# Creating and using Temporal File
import tempfile
# Date
import datetime
# Filesystem Operations
import shutil

class SourceFile(object):
    """Represents a SourceFile and provides the functionality to beautify its
    file header"""

    # Regular Expressions
    COMMENT = re.compile(
        # Line start
        '^\w*'
        # Comment
        # TODO: RE change so that /**, /* and * starts of comments are possible
        '//(?P<comment>.*)'
        # # End of line
        '\w*'
    )
    AUTHOR_DATE = re.compile(
        # TODO: Match Date more variable
        '.*Created by (?P<author>.+) on (?P<date>..[\.|/]..[\.|/]..)'
    )
    AUTHOR = re.compile(
        '@author (?P<author>.+)'
    )

    def __init__(self, file_path, company=None, authors=set()):
        '''
        Test Regular Expressions

        >>> SourceFile.COMMENT.match('//    Comment').group('comment')
        '    Comment'
        >>> AUTHOR_COMMENT = 'Created by Markus Chmelar on 02.07.12.'
        >>> match = SourceFile.AUTHOR_DATE.match(AUTHOR_COMMENT)
        >>> match.group('author')
        'Markus Chmelar'
        >>> match.group('date')
        '02.07.12'
        '''
        super(SourceFile, self).__init__()
        self.file_path = file_path
        self.information = {}
        self.information['filename'] = os.path.split(file_path)[1]
        logging.debug(authors)
        self.information['author'] = authors
        if company is not None:
            self.information['company'] = company

    def process_comment_line(self, line):
        '''
        Processes a comment line and saves information that is needed later

        Doctests:
            >>> f = SourceFile('.')
            >>> f.process_comment_line('//')
            >>> f.process_comment_line('//  TestFlight.h')
            >>> f.process_comment_line('//  libTestFlight')
            >>> f.process_comment_line('//')
            >>> f.process_comment_line('//  Created by Jonathan Janzen on 06/11/11.')
            >>> f.process_comment_line('//  Copyright 2011 TestFlight. All rights reserved.')
            >>> f.information
            {'date': '06/11/11', 'author': set(['Jonathan Janzen']), 'filename': '.'}

            >>> g = SourceFile('Test')
            >>> g.process_comment_line('//')
            >>> g.process_comment_line('//  main.m')
            >>> g.process_comment_line('//  Polynom')
            >>> g.process_comment_line('//')
            >>> g.process_comment_line('//  Created by Markus Chmelar on 02.07.12.')
            >>> g.process_comment_line('//  Copyright (c) 2012 TU Wien. All rights reserved.')
            >>> g.process_comment_line('//')

            >>> h = SourceFile('H')
            >>> h.process_comment_line('//')
            >>> h.process_comment_line('//  IVCGAdditions.h')
            >>> h.process_comment_line('//  Polynom')
            >>> h.process_comment_line('//')
            >>> h.process_comment_line('//  Created by Sepp Chmelar on 22.02.13.')
            >>> h.process_comment_line('//  Copyright (c) 2013 TU Wien. All rights reserved.')
            >>> h.process_comment_line('//')
            >>> h.process_comment_line('')
            >>> h.process_comment_line('#ifndef Polynom_IVCGAdditions_h')
            >>> h.process_comment_line('#define Polynom_IVCGAdditions_h')
        '''
        author_date_match = SourceFile.AUTHOR_DATE.match(line)
        if author_date_match is not None:
            self.information['author'].add(author_date_match.group('author'))
            self.information['date'] = author_date_match.group('date')
        author_match = SourceFile.AUTHOR.match(line)
        if author_match is not None:
            self.information['author'].add(author_match.group('author'))

    def create_header(self):
        '''
        Returns the new Header
        '''
        header = '/**\n'
        header += ' *   @file       {}\n'.format(self.information['filename'])
        for author in self.information['author']:
            header += ' *   @author     {}\n'.format(author)
        if 'date' in self.information.keys():
            header += ' *   @date       {}\n'.format(self.information['date'])
        if 'company' in self.information.keys():
            header += ' *   @copyright       {}\n'.format(self.information['company'])
        header += ' *\n'
        if 'company' in self.information.keys():
            header += ' *   Copyright (c) {} {}. All rights reserved.\n'.format(
                                                    datetime.date.today().year,
                                                    self.information['company'])
        header += ' */\n'
        return header

    def process_file(self):
        '''
        Scans the file, finds the file-header and updates it

        >>> f = SourceFile('TestInput/main.m')
        >>> f.process_file()
        '''
        # Create temp file
        temp_folder_path = tempfile.mkdtemp()
        temp_file_path = '{}/{}'.format(temp_folder_path,
                                        self.information['filename'])

        logging.debug('Processing Source-File {} with Temp-File {}'.format(
                                                                self.file_path,
                                                                temp_file_path))

        dest_file = open(temp_file_path, 'w')

        # Search for the file header and read contained information
        for line in open(self.file_path):
            comment = SourceFile.COMMENT.match(line)
            if comment is None:
                break
            self.process_comment_line(line)

        # Write a new Header
        
        logging.debug('Information: {}'.format(self.information))

        header = self.create_header()
        dest_file.write(header)

        logging.debug('Header Parsing complete')
        logging.debug('Header: {}'.format(header))

        # Every following line only has to be copied
        comment_ended = False
        for line in open(self.file_path):
            if not comment_ended:
                comment = SourceFile.COMMENT.match(line)
            if comment is None:
                comment_ended = True
            if comment_ended:
                dest_file.write(line)

        # Close Files
        dest_file.close()

        # #Remove original file
        # remove(file_path)
        # #Move new file
        # shutil.move(temp_file_path, file_path)

        # Delete Temp-Directory
        shutil.rmtree(temp_folder_path)


def main():
    ''' Just create a logger and run the doctests '''
    # Create Logger
    logging.basicConfig(
        format='%(message)s',
        level=logging.DEBUG
    )
    doctest.testmod()
    return 0


if __name__ == '__main__':
    sys.exit(main())