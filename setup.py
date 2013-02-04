from distutils.core import setup

setup(
    name='iga-python-dcr',
    version='0.0.1',
    description="Python access to DCR files",
    author='Vittorio Zamboni',
    author_email='zamboni@appliedgenomics.org',
    license='MIT',
    url='http://bitbucket.org/iga/python-dcr',
    packages=[
        'python_dcr',
    ],
    install_requires=[
        'Cython==0.18',
        'pysam==0.7.4',
    ]
)
