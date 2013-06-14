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
    COMPANY = re.compile(
        '.*Copyright(?P<c> \(c\).|.)(?P<year>....) (?P<company>[a-zA-Z ]+)\..*'
    )

    def __init__(self, file_path, company=None, authors=[]):
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
        >>> COMPANY = 'Copyright 2011 TestFlight. All rights reserved.'
        >>> match = SourceFile.COMPANY.match(COMPANY)
        >>> match.group('company')
        'TestFlight'
        >>> match.group('year')
        '2011'
        >>> COMPANY = '  Copyright (c) 2012 TU Wien. All rights reserved.'
        >>> match = SourceFile.COMPANY.match(COMPANY)
        >>> match.group('company')
        'TU Wien'
        >>> match.group('year')
        '2012'
        '''
        super(SourceFile, self).__init__()
        self.file_path = file_path
        self.information = {}
        self.information['filename'] = os.path.split(file_path)[1]
        self.information['author'] = set(authors)
        self.overwrite_authors = len(authors) is not 0
        self.overwrite_company = company is not None
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
            {'date': '06/11/11', 'company': 'TestFlight', 'author': set(['Jonathan Janzen']), 'year': '2011', 'filename': '.'}

            >>> g = SourceFile('Test')
            >>> g.process_comment_line('//')
            >>> g.process_comment_line('//  main.m')
            >>> g.process_comment_line('//  Polynom')
            >>> g.process_comment_line('//')
            >>> g.process_comment_line('//  Created by Markus Chmelar on 02.07.12.')
            >>> g.process_comment_line('//  Copyright (c) 2012 TU Wien. All rights reserved.')
            >>> g.process_comment_line('//')
            >>> g.information
            {'date': '02.07.12', 'company': 'TU Wien', 'author': set(['Markus Chmelar']), 'year': '2012', 'filename': 'Test'}

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
            >>> h.information
            {'date': '22.02.13', 'company': 'TU Wien', 'author': set(['Sepp Chmelar']), 'year': '2013', 'filename': 'H'}

            >>> i = SourceFile('H', company='Test')
            >>> i.process_comment_line('//')
            >>> i.process_comment_line('//  IVCGAdditions.h')
            >>> i.process_comment_line('//  Polynom')
            >>> i.process_comment_line('//')
            >>> i.process_comment_line('//  Created by Sepp Chmelar on 22.02.13.')
            >>> i.process_comment_line('//  Copyright (c) 2013 TU Wien. All rights reserved.')
            >>> i.process_comment_line('//')
            >>> i.process_comment_line('')
            >>> i.process_comment_line('#ifndef Polynom_IVCGAdditions_h')
            >>> i.process_comment_line('#define Polynom_IVCGAdditions_h')
            >>> i.information
            {'date': '22.02.13', 'company': 'Test', 'author': set(['Sepp Chmelar']), 'year': '2013', 'filename': 'H'}

            >>> j = SourceFile('H', authors=['a1', 'a2'])
            >>> j.process_comment_line('//')
            >>> j.process_comment_line('//  IVCGAdditions.h')
            >>> j.process_comment_line('//  Polynom')
            >>> j.process_comment_line('//')
            >>> j.process_comment_line('//  Created by Sepp Chmelar on 22.02.13.')
            >>> j.process_comment_line('//  Copyright (c) 2013 TU Wien. All rights reserved.')
            >>> j.process_comment_line('//')
            >>> j.process_comment_line('')
            >>> j.process_comment_line('#ifndef Polynom_IVCGAdditions_h')
            >>> j.process_comment_line('#define Polynom_IVCGAdditions_h')
            >>> j.information
            {'date': '22.02.13', 'company': 'TU Wien', 'author': set(['a1', 'a2']), 'year': '2013', 'filename': 'H'}
        '''
        author_date_match = SourceFile.AUTHOR_DATE.match(line)
        if author_date_match is not None:
            if self.overwrite_authors is False:
                self.information['author'].add(author_date_match.group('author'))
            self.information['date'] = author_date_match.group('date')
        author_match = SourceFile.AUTHOR.match(line)
        if author_match is not None and self.overwrite_authors is False:
            self.information['author'].add(author_match.group('author'))
        company_match = SourceFile.COMPANY.match(line)
        if company_match is not None:
            self.information['year'] = company_match.group('year')
            if self.overwrite_company is False:
                self.information['company'] = company_match.group('company')

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

        if 'year' in self.information.keys():
            year = self.information['year']
        else:
            year = datetime.date.today().year

        if 'company' in self.information.keys():
            header += ' *   Copyright (c) {} {}. All rights reserved.\n'.format(
                                                    year,
                                                    self.information['company'])
        header += ' */\n'
        return header

    def process_file(self):
        '''
        Scans the file, finds the file-header and updates it
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

        #Remove original file
        # os.remove(self.file_path)
        #Move new file
        shutil.move(temp_file_path, self.file_path)

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
