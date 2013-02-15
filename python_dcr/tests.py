import magic
import os
import unittest
from dcr import DCRFile


class TestDCR(unittest.TestCase):

    def setUp(self):
        self.f = DCRFile('example/data.dcr')

    def tearDown(self):
        if os.path.exists(self.f.filename_index):
            os.remove(self.f.filename_index)
        if os.path.exists(self.f.filename_compressed):
            os.remove(self.f.filename_compressed)
        if os.path.exists(self.f.filename_index_tabix):
            os.remove(self.f.filename_index_tabix)

    def test_filenames(self):
        self.assertEqual(self.f.filename, 'example/data.dcr')
        self.assertEqual(self.f.favourite_method, 'compressed')
        # file extensions
        self.assertEqual(self.f.extension_compressed, '.gz')
        self.assertEqual(self.f.extension_index, '.dcri')
        self.assertEqual(self.f.extension_index_tabix, '.tbi')
        self.assertEqual(self.f.filename_compressed,
                         self.f.filename + self.f.extension_compressed)
        self.assertEqual(self.f.filename_index,
                         self.f.filename + self.f.extension_index)
        self.assertEqual(self.f.filename_index_tabix,
                         self.f.filename +
                                self.f.extension_compressed +
                                self.f.extension_index_tabix)

    def test_check_files(self):
        self.f.check_related_files()
        self.assertEqual(self.f.favourite_method, 'text')

    def test_status(self):
        status = self.f.get_status()
        self.assertTrue(status['filename_exists'])
        self.assertFalse(status['filename_compressed_exists'])
        self.assertFalse(status['filename_index_exists'])
        self.assertFalse(status['filename_index_tabix_exists'])

    def test_write_index_and_read_header(self):
        self.assertTrue(self.f.write_index())
        self.assertTrue(os.path.exists(self.f.filename_index))
        self.assertTrue(self.f.read_header())
        header = self.f.header
        self.assertEqual(header['values'], 'int')
        self.assertEqual(header['chunk'], 1000)
        self.assertEqual(header['separator'], ' ')
        self.assertEqual(header['conv'], int)
        self.assertEqual(header['null_value'], 0)

    def test_read_index(self):
        self.f.write_index()
        self.assertTrue(self.f.read_index())
        self.assertEquals(self.f.index, {'chr1': {'line': 2, 'tot': 10045},
                                         'chr2': {'line': 13, 'tot': 10}})

    def test_compress(self):
        self.f.write_index()
        self.assertTrue(self.f.compress())
        self.assertTrue(os.path.exists(self.f.filename_compressed))
        self.assertTrue(os.path.exists(self.f.filename_index_tabix))

    def test_fetch_text(self):
        self.f.write_index()
        self.f.read_header()
        self.f.read_index()
        self.assertEqual(self.f.fetch_text('chr1', 1, 10),
                         [0, 0, 0, 4, 5, 6, 7, 8, 9, 10])

    def test_check_compressed_file(self):
        self.f.write_index()
        self.f.read_header()
        self.f.read_index()
        self.f.compress()
        self.assertEquals(magic.from_file(self.f.filename_compressed,
                                          mime=True),
                                          'application/x-gzip')

    def test_fetch_tabix(self):
        self.f.write_index()
        self.f.read_header()
        self.f.read_index()
        self.f.compress()
        self.assertEqual(self.f.fetch_tabix('chr1', 1, 10),
                         [0, 0, 0, 4, 5, 6, 7, 8, 9, 10])


if __name__ == "__main__":
    unittest.main()
