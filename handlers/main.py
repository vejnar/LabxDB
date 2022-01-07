#-*- coding: utf-8 -*-

#
# Copyright (C) 2018-2022 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import aiohttp.web
import aiohttp_jinja2

from . import base

routes = aiohttp.web.RouteTableDef()

@routes.view('/')
class MainHandler(base.BaseHandler):
    @aiohttp_jinja2.template('main.jinja')
    async def get(self):
        return {'title': 'LabxDB', 'base_url': self.base_url}
