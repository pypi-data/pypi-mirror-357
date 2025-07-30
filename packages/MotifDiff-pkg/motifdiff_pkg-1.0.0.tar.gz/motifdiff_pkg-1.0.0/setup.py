from setuptools import setup, find_packages

setup(
    name='MotifDiff-pkg',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
    	'regex',
        'torch',
        'pandas',
        'numpy<2',
        'typer',
        'pysam',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            'getDiff = MotifDiff.MotifDiff:app',
        ],
    },
)

