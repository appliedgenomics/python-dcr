'''
Ver B
produces:
data.dcr
1. __header    1    2    chunk=1000 split=space values=int
2. chr1    1    1000    1 2 3 4 ...
3. chr1    1001 2000    1001 1002 1003 ...
4. chr1    2001 3000    2001 2002 2003 ...
5. chr2    1    1000    1 2 3 4 ...
6. chr2    1001 2000    1001 1002 1003 ...
7. chr2    2001 3000    2001 2002 2003 ...
data.dcri
1. #chunk=1000 split=space values=int
2. chr1:2
3. chr2:5
'''

import sys
import time


def convert_wig_to_dcr(wig, dcr, chunk_size, **kwargs):
    separator = kwargs.get('separator', ' ')
    types = kwargs.get('types', 'int')
    null_value = kwargs.get('null_value', 0)

    ih = open(wig)
    oh = open(dcr, 'w')
    ohi = open(dcr + 'i', 'w')

    # Current line plus 1: skip the header
    lines = 2

    split_text = separator
    if separator == ' ':
        split_text = 'space'

    oh.write('#chunk=%s split=%s values=%s' %
             (chunk_size, split_text, types))
    ohi.write('#chunk=%s split=%s values=%s\n' %
              (chunk_size, split_text, types))

    chrom = ''
    chrom_lines = 1
    chunk_values = []

    for line in ih:
        line = line.strip()
        if line != '':
            if 'chrom' in line:
                if chunk_values:
                    first_num = (chrom_lines - 1) * chunk_size + 1
                    last_num = first_num + len(chunk_values) - 1
                    oh.write('\n%s\t%s\t%s\t' % (chrom, first_num, last_num))
                    for value in chunk_values[:-1]:
                        oh.write('%s ' % value)
                    oh.write('%s' % chunk_values[-1])
                    lines += 1

                ''' Get header '''
                values = line.split(' ')
                info = {}
                for val in values:
                    try:
                        info[val.split('=')[0]] = val.split('=')[1]
                    except:
                        pass
                info.setdefault('start', '1')
                info.setdefault('step', '1')
                info.setdefault('span', '1')
                chrom = info['chrom']
                writed = 0
                chrom_lines = 1
                chunk_values = []

                ohi.write('%s:%s\n' % (chrom, lines))

                start = int(info['start'])
                if start > 0:
                    for i in range(1, start):
                        chunk_values.append(null_value)
                        writed += 1
                        if writed % chunk_size == 0:
                            first_num = (chrom_lines - 1) * chunk_size + 1
                            last_num = (chrom_lines) * chunk_size
                            oh.write('\n%s\t%s\t%s\t' %
                                     (chrom, first_num, last_num))
                            for value in chunk_values[:-1]:
                                oh.write('%s ' % value)
                            oh.write('%s' % chunk_values[-1])
                            lines += 1
                            writed = 0
                            chunk_values = []
                            chrom_lines += 1
            else:
                chunk_values.append(line)
                writed += 1
                if writed % chunk_size == 0:
                    first_num = (chrom_lines - 1) * chunk_size + 1
                    last_num = (chrom_lines) * chunk_size
                    oh.write('\n%s\t%s\t%s\t' % (chrom, first_num, last_num))
                    for value in chunk_values[:-1]:
                        oh.write('%s ' % value)
                    lines += 1
                    oh.write('%s' % chunk_values[-1])
                    writed = 0
                    chunk_values = []
                    chrom_lines += 1
    if chunk_values:
        first_num = (chrom_lines - 1) * chunk_size + 1
        last_num = first_num + len(chunk_values) - 1
        oh.write('\n%s\t%s\t%s\t' % (chrom, first_num, last_num))
        lines += 1
        for value in chunk_values[:-1]:
            oh.write('%s ' % value)
        oh.write('%s' % chunk_values[-1])

    ih.close()
    oh.close()
    ohi.close()


if __name__ == "__main__":
    chunk_size = 1000
    separator = ' '
    types = 'int'
    null_value = 0

    try:
        wig = sys.argv[1]
        dcr = sys.argv[2]
    except:
        print 'Usage: \n\tpython convert_wig_to_dcr.py <wig> <dcr>'

    sys.stderr.write("Version B\n")
    data = {
            'separator': separator,
            'types': types,
            'null_value': null_value,
            }
    t1 = time.time()

    convert_wig_to_dcr(wig, dcr, chunk_size, **data)

    t2 = time.time()
    delta = t2 - t1
    print "Elapsed time: %s" % delta
