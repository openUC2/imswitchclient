#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst", "r") as fh:
    history = fh.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Benedict Diederich",
    author_email='benedictdied@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="This is a package that connects ImSwitch's REST API to the rest of the world (e.g. jupyter lab)",
    install_requires=requirements,
    license="MIT license",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='imswitchclient',
    name='imswitchclient',
    packages=find_packages(include=['imswitchclient', 'imswitchclient.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/openuc2/imswitchclient',
    version='0.1.3',
    zip_safe=False,
)
