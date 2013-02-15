'''
Ver B
produces:
data.dcr
1. __header    1    2    chunk=1000 separator=space values=int
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


def convert_wig_to_dcr(wig, dcr, chunk_size=1000, **kwargs):
    separator = kwargs.get('separator', ' ')
    types = kwargs.get('types', 'int')
    null_value = kwargs.get('null_value', 0)

    conv = str
    if types == 'int':
        conv = int
    elif types == 'float':
        conv = float

    ih = open(wig)
    oh = open(dcr, 'w')
    ohi = open(dcr + '.dcri', 'w')

    # Current line plus 1: skip the header
    lines = 2

    split_text = separator
    if separator == ' ':
        split_text = 'space'

    oh.write('__header\t1\t2\tchunk=%s separator=%s values=%s' %
             (chunk_size, split_text, types))
    ohi.write('#chunk=%s separator=%s values=%s\n' %
              (chunk_size, split_text, types))

    chrom = ''
    chrom_lines = 1
    chunk_values = []
    info = {}

    for line in ih:
        line = line.strip()
        if line != '' and not line.startswith('track'):
            if 'chrom' in line:
                if chunk_values:
                    info = collect_info(info, line, conv)
                    chrom_lines, chunk_values, lines, info = \
                            process_value(chrom_lines, chunk_values,
                                          lines, info, oh)
                if 'chrom' in info:
                    write_index(info, ohi)

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
                chrom_lines = 1
                chunk_values = []
                info.update({
                        'mean': null_value,
                        'min': null_value,
                        'max': null_value,
                        'total': 0,
                        'totals': 0,
                        'writed': 0,
                        'first_line': lines})

                start = int(info['start'])
                if start > 0:
                    for i in range(1, start):
                        info = collect_info(info, null_value, conv)
                        chrom_lines, chunk_values, lines, info = \
                                process_value(chrom_lines, chunk_values,
                                              lines, info, oh)
            else:
                chunk_values.append(line)
                info = collect_info(info, line, conv)
                chrom_lines, chunk_values, lines, info = \
                        process_value(chrom_lines, chunk_values,
                                      lines, info, oh)
    if chunk_values:
        info = collect_info(info, line, conv)
        chrom_lines, chunk_values, lines, info = \
                process_value(chrom_lines, chunk_values,
                              lines, info, oh)
    if 'chrom' in info:
        write_index(info, ohi)

    ih.close()
    oh.close()
    ohi.close()


def collect_info(info, line, conv):
    num = conv(line)
    if num < info['min']:
        info['min'] = num
    if num > info['max']:
        info['max'] = num
    info['totals'] += 1
    info['total'] += num
    info['writed'] += 1
    return info


def process_value(chrom_lines, chunk_values, lines, info, oh):
    if info['writed'] % chunk_size == 0:
        first_num = (chrom_lines - 1) * chunk_size + 1
        last_num = (chrom_lines) * chunk_size
        oh.write('\n%s\t%s\t%s\t' % (info['chrom'], first_num, last_num))
        for value in chunk_values[:-1]:
            oh.write('%s ' % value)
        lines += 1
        oh.write('%s' % chunk_values[-1])
        info['writed'] = 0
        chunk_values = []
        chrom_lines += 1
    return chrom_lines, chunk_values, lines, info


def write_index(info, ohi):
    ohi.write('%s:%s:tot=%s;min=%s;max=%s;mean=%.4f\n' %
              (info['chrom'], info['first_line'],
               info['totals'], info['min'], info['max'],
               info['total'] / float(info['totals'])))

if __name__ == "__main__":
    chunk_size = 1000
    separator = ' '

    try:
        wig = sys.argv[1]
        dcr = sys.argv[2]
    except:
        print 'Usage: \n\tpython convert_wig_to_dcr.py <wig> <dcr> ' + \
                '[<types> <null_value]'

    try:
        types = sys.argv[3]
        null_value = sys.argv[4]
        if types == 'int':
            null_value = int(null_value)
        if types == 'float':
            null_value = float(null_value)
    except:
        types = 'int'
        null_value = 0

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
