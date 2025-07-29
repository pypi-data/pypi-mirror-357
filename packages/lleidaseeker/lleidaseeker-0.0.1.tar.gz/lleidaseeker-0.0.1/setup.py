#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages, Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Meinolf Sellmann",
    author_email='info@insideopt.com',
    python_requires='>=3.6.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux'
    ],
    description="InsideOpt Seeker Centos 7 Linux 36 Distribution",
    install_requires=requirements,
    long_description=readme, 
    long_description_content_type='text/markdown',
    keywords='insideopt, seeker, optimization',
    name='lleidaseeker',
    test_suite='tests',
    version='0.0.1',
    packages=find_packages(include=['lleidaseeker', 'lleidaseeker.*', '*.so']),
    package_data={'lleidaseeker': ['*.so', 'lleidaseeker.py', 'bin/*', 'scripts/*']},
    zip_safe=False,
)
