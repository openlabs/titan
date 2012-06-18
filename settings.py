# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

SETTINGS = {
    'installed_apps': [
        'monstor.contrib.auth',
        'titan.projects',
    ],
    'cookie_secret': 'N7qxweo0malDySdP',
    'template_path': resource_filename('titan', 'templates'),
    'login_url': '/login'
}
