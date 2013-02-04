import linecache
import os
import sys
import time

import pysam

'''
1. Create a DCRFile with index:

import dcr
f = dcr.DCRFile(filename)
f.write_index()
====================================

2. Compress a DCRFile with tabix

f.compress()
====================================

3. Create Tabix index

f.write_index_tabix()
====================================

4. Read index and validate header content

f.read_index()
'''


class DCRFile():
    # Paths and checks
    filename = ''
    __filename_exists = False
    filename_compressed = ''
    __filename_compressed_exists = False
    filename_index = ''
    __filename_index_exists = False
    filename_index_tabix = ''
    __filename_index_tabix_exists = False
    # DCR header and index, in memory
    header = {}
    index = {}
    __keep_index = True
    favourite_method = 'compressed'
    # file extensions
    extension_compressed = '.gz'
    extension_index = '.dcri'
    extension_index_tabix = '.tbi'

    def __init__(self, filename, **kwargs):
        self.filename = filename
        filename_compressed = filename
        if not filename.endswith(self.extension_compressed):
            filename_compressed += '.gz'
        self.filename_compressed = kwargs.get('filename_compressed',
                                              filename_compressed)
        filename_index = filename + self.extension_index
        self.filename_index = kwargs.get('filename_index',
                                              filename_index)
        filename_index_tabix = filename_compressed + self.extension_index_tabix
        self.filename_index_tabix = kwargs.get('filename_index_tabix',
                                              filename_index_tabix)
        check_files = kwargs.get('check_files', True)
        if check_files:
            self.check_related_files()
        elif kwargs.get('trust', False):
            self.trust()
        if kwargs.get('fast', False):
            self.__keep_index = False
        self.__keep_index = kwargs.get('keep_index', False)
        if self.__filename_index_exists:
            self.read_index()
        self.favourite_method = kwargs.get('favourite_method', 'compressed')

    def check_related_files(self):
        self.__filename_exists = os.path.exists(self.filename)
        self.__filename_compressed_exists = os.path.exists(
                self.filename_compressed)
        self.__filename_index_exists = os.path.exists(self.filename_index)
        self.__filename_index_tabix_exists = os.path.exists(
                self.filename_index_tabix)
        if not self.__filename_compressed_exists:
            self.favourite_method = 'text'

    def trust(self):
        self.__filename_exists = True
        self.__filename_compressed_exists = True
        self.__filename_index_exists = True
        self.__filename_index_tabix_exists = True

    def print_status(self):
        print "filename_exists: %s" % self.__filename_exists
        print "filename_compressed_exists: %s" % \
                self.__filename_compressed_exists
        print "filename_index_exists: %s" % self.__filename_index_exists
        print "filename_index_tabix_exists: %s" % \
                self.__filename_index_tabix_exists

    def validate_header(self):
        self.header.setdefault('chunk', 1000)
        self.header['chunk'] = int(self.header['chunk'])
        self.header.setdefault('values', 'int')
        if self.header['values'] == 'int':
            self.header['conv'] = int
        elif self.header['values'] == 'float':
            self.header['conv'] = float
        else:
            self.header['conv'] = None
        self.header.setdefault('separator', ' ')
        if self.header['separator'] == 'space':
            self.header['separator'] = ' '
        return True

    def set_header_values(self, header_values):
        if isinstance(header_values, str):
            if header_values.startswith('#'):
                header_values = header_values[1:]
            for couple in header_values.split(' '):
                self.header[couple.split('=')[0]] = couple.split('=')[1]
            self.validate_header()
            return True
        elif isinstance(header_values, dict):
            self.header.update(header_values)
            self.validate_header()
            return True
        else:
            sys.stderr.write(
                    'Unexpected type for header values: %s\n' %
                    type(header_values))
            return False

    def compress_tabix(self, **kwargs):
        force = kwargs.get('force', False)
        timing = kwargs.get('timing', False)
        t1 = time.time()
        if self.__filename_compressed_exists and not force:
            sys.stderr.write("%s exists\n" % self.filename_compressed)
            return False
        else:
            try:
                pysam.tabix_compress(self.filename, self.filename_compressed,
                                     force=force)
                self.__filename_compressed_exists = True
                t2 = time.time()
                if timing:
                    sys.stderr.write('Total time: %s\n' % (t2 - t1))
                return True
            except:
                sys.stderr.write('Unexpected error during compression: %s\n' %
                                 sys.exc_info()[1])
                return False

    def write_index_tabix(self, **kwargs):
        force = kwargs.get('force', False)
        timing = kwargs.get('timing', False)

        t1 = time.time()

        if self.__filename_index_tabix_exists and not force:
            sys.stderr.write("%s exists\n" % self.filename_index_tabix)
            return False
        else:
            try:
                pysam.tabix_index(self.filename_compressed,
                                  seq_col=0, start_col=1, end_col=2,
                                  force=force)
                self.__filename_index_tabix_exists = True
                t2 = time.time()
                if timing:
                    sys.stderr.write('Total time: %s\n' % (t2 - t1))
                return True
            except:
                sys.stderr.write(
                        'Unexpected error during indexing (tabix): %s\n' %
                        sys.exc_info()[0])
                return False

    def compress(self, **kwargs):
        timing = kwargs.get('timing', False)
        force = kwargs.get('force', False)

        t1 = time.time()

        self.compress_tabix(force=force)
        self.write_index_tabix(force=force)

        t2 = time.time()
        if timing:
            sys.stderr.write('Total time: %s' % (t2 - t1))

    def write_index(self, **kwargs):
        force = kwargs.get('force', False)
        timing = kwargs.get('timing', False)

        t1 = time.time()
        if self.__filename_index_exists and not force:
            sys.stderr.write("%s exists\n" % self.filename_index)
            return False
        try:
            fh = open(self.filename, 'r')
            ih = open(self.filename_index, 'w')
            # Write header
            header_values = fh.readline().split('\t')[3].strip()
            ih.write('#' + header_values)
            self.set_hedaer_values(header_values)
            # Write content
            chr_name = ''
            line = 1
            for dcr_line in fh:
                line += 1
                dcr_data = dcr_line.split('\t')
                if dcr_data[0] != chr_name:
                    chr_name = dcr_data[0]
                    ih.write("%s:%s\n" % (chr_name, line))
                    if self.__keep_index:
                        self.index[chr_name] = line
            fh.close()
            ih.close()
            self.__filename_index_exists = True

            t2 = time.time()
            if timing:
                sys.stderr.write('Total time: %s\n' % (t2 - t1))
            return True
        except:
            sys.stderr.write(
                    'Unexpected error during indexing (DCR): %s\n' %
                    sys.exc_info()[1])
            return False

    def read_header(self):
        if self.__filename_index_exists:
            try:
                ih = open(self.filename_index)
                self.set_header_values(ih.readline().strip())
                ih.close()
                return True
            except:
                sys.stderr.write(
                        'Unexpected error while reading header: %s\n' %
                        sys.exc_info()[1])
                return False
        else:
            sys.stderr.write('Index does not exists.\n')
            return False

    def read_index(self, ih_open=None, set_header=True):
        header_line = ''
        if self.__filename_index_exists:
            try:
                if not ih_open:
                    ih = open(self.filename_index)
                    header_line = ih.readline().strip()
                else:
                    ih = ih_open
                if set_header:
                    self.set_header_values(header_line)
                for line in ih:
                    line = line.strip()
                    if line != '':
                        line = line.split(':')
                        self.index[line[0]] = int(line[1])
                if not ih_open:
                    ih.close()
                return True
            except:
                sys.stderr.write(
                        'Unexpected error while reading index: %s\n' %
                        sys.exc_info()[1])
                return False
        else:
            sys.stderr.write('Index does not exists.\n')
            return False

    def fetch_text(self, reference=None, start=None, end=None, **kwargs):
        lines_values = kwargs.get('lines_values', [])
        fetch_start_line = kwargs.get('fetch_start_line', True)
        timing = kwargs.get('timing', False)
        chunk_size = self.header['chunk']

        t1 = time.time()

        if not self.__filename_exists or \
                not self.__filename_index_exists:
            sys.stderr.write(
                    "Check the existence of text file and index files.\n")
            return False

        ret_values = []
        if not lines_values:
            # Avoid referencing
            lines_values = []
            start_line = self.index[reference]
            line_start = start_line + ((start - 1) // chunk_size)
            line_end = start_line + (end // chunk_size)
            for l in range(line_start, line_end + 1):
                lines_values.append(
                        linecache.getline(self.filename, l).strip())

        line_end = len(lines_values)
        for l in range(0, line_end):
            line = lines_values[l]
            values = line.split(self.header['separator'])
            values[0] = values[0].split('\t')[3]
            a = None
            b = None
            if l == 0:
                a = start % chunk_size - 1
            if l == line_end - 1:
                b = end % chunk_size
            values_range = values[a:b]
            if self.header['conv']:
                ret_values += map(self.header['conv'], values_range)
            else:
                ret_values += values_range

        t2 = time.time()
        if timing:
            sys.stderr.write('Total time: %s' % (t2 - t1))
        return ret_values

    def fetch_tabix(self, reference, start, end, **kwargs):
        timing = kwargs.get('timing', False)

        t1 = time.time()
        if not self.__filename_compressed_exists or \
                not self.__filename_index_exists or \
                not self.__filename_index_tabix_exists:
            sys.stderr.write(
                    "Check the existence of compressed and indexes files.\n")
            return False
        f = pysam.Tabixfile(self.filename_compressed)
        try:
            values = [r for r in f.fetch(reference=reference,
                                         start=start, end=end)]
            f.close()
            ret_values = self.fetch_text(reference, start, end,
                                        lines_values=values,
                                        fetch_start_line=False)
            t2 = time.time()
            if timing:
                sys.stderr.write('Total time: %s' % (t2 - t1))
            return ret_values
        except:
            f.close()
            sys.stderr.write(
                    'Unexpected error while fetching values: %s\n' %
                    sys.exc_info()[1])
            return False
        if not values:
            print "Empty reference"
            return []

    def fetch(self, reference=None, start=None, end=None, **kwargs):
        if self.__filename_exists and self.favourite_method == 'text':
            return self.fetch_text(reference, start, end, **kwargs)
        elif self.__filename_index_tabix_exists and \
                self.favourite_method == 'compressed':
            return self.fetch_tabix(reference, start, end, **kwargs)
        else:
            sys.stderr.write("There is no index.\n")
            return False
