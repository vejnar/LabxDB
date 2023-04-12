#-*- coding: utf-8 -*-

#
# Copyright © 2018 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import logging

import aiohttp.web

class BaseHandler(aiohttp.web.View):
    '''BaseHandler.'''
    logger = logging.getLogger()

    @property
    def pool(self):
        return self.request.app['pool']

    @property
    def base_url(self):
        # Use the header (set by proxy) if present
        try:
            base_url = self.request.headers['X-Base-URL']
        except KeyError:
            base_url = ''
        return base_url
