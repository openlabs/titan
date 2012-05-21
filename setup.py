# -*- coding: utf-8 -*-
"""
    setup


    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from setuptools import setup

setup(
    name = "Titan",
    version = "0.1",
    description = __doc__,

    author = 'Openlabs Technologies & Consulting (P) Limited',
    website = 'http://openlabs.co.in/',
    email = 'info@openlabs.co.in',

    packages = [
        "titan",
        "titan.projects",
    ],
    package_dir = {
        "titan": ".",
        "titan.projects": 'projects',
    },
    install_requires = [
        'monstor',
    ],
    scripts = [
        'bin/titand',
    ],
    package_data = {
        "titan": [
            'templates/*.html',
            'templates/user/*.html',
            'templates/projects/*.html',
            'static/css/*.less',
            'static/css/*.css',
            'static/images/*',
            'static/js/*.js',
        ]
    },
    zip_safe = False,
)
