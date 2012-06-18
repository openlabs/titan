#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from tornado import ioloop
from tornado.options import options
from monstor.app import make_app

from titan.projects.models import User


settings = {
    'installed_apps': [
        'monstor.contrib.auth',
        'projects',
    ],
    'cookie_secret': 'N7qxweo0malDySdP',
    'template_path': os.path.join(os.getcwd(), 'templates'),
    'user_model': User,
    'login_url': '/login'
}
application = make_app(**settings)

if __name__ == '__main__':
    application.listen(options.port, address=options.address)
    ioloop.IOLoop.instance().start()
