from distutils.core import setup

setup(
    name='iga-python-dcr',
    version='0.5.0',
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
        'nose==1.2.1,
        'python-magic==0.4.3',
        'pysam==0.7.4',
    ]
)
