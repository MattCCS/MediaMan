"""
PyPI setup file
"""

from setuptools import setup, find_packages


setup(
    name='mediaman',
    packages=find_packages(exclude='mm'),
    version='0.0.2',
    author='Matt Cotton',
    author_email='matthewcotton.cs@gmail.com',
    url='https://github.com/MattCCS/MediaMan',

    description='MediaMan backs up arbitrary media files to arbitrary cloud services!',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    classifiers=["Programming Language :: Python :: 3"],

    install_requires=[
        'cryptography',
        'PyYAML',
        'xxhash',
    ],

    entry_points={
        'console_scripts': [
            'mm=mediaman.interfaces.cli:main'
        ]
    }
)
