"""
PyPI setup file
"""

from setuptools import setup


setup(
    name = 'mediaman',
    packages = ['mediaman'],
    version = '0.0.1',
    author='Matt Cotton',
    author_email='matthewcotton.cs@gmail.com',
    url='https://github.com/MattCCS/MediaMan',

    description='MediaMan backs up arbitrary media files to arbitrary cloud services!',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    classifiers=["Programming Language :: Python :: 3"],

    entry_points={
        'scripts': [
            'mm=mm',
        ],
    },
)

