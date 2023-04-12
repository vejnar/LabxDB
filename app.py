#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# Copyright © 2018 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import argparse
import logging
import os
import sys

import asyncpg
import aiohttp.web
import aiohttp_jinja2
import jinja2

import handlers

ENV_PREFIX = 'LABXDB_'

def get_env_config():
    config = {}
    for k, v in os.environ.items():
        if k.startswith(ENV_PREFIX):
            config[k[len(ENV_PREFIX):].lower()] = v
    return config

def path_exists(p):
    return os.path.exists(os.path.join(os.path.dirname(__file__), 'static', p))

async def init_connection(conn):
    # To encode and decode date as string instead of date object
    await conn.set_type_codec('date', encoder=str, decoder=str, schema='pg_catalog', format='text')

async def init_pool(app):
    app['pool'] = await asyncpg.create_pool(dsn=f"postgres://{app['db_user']}:{app['db_password']}@{app['db_host']}:{app['db_port']}/{app['db_name']}", min_size=int(app['db_conn']), max_size=int(app['db_conn']), init=init_connection)

async def close_pool(app):
    await app['pool'].close()

def setup_routes(app):
    for name in handlers.__all__:
        handler_class = getattr(handlers, name)
        if hasattr(handler_class, 'routes'):
            app.router.add_routes(getattr(handler_class, 'routes'))
    app.router.add_static('/static/', path=app['static_path'], follow_symlinks=True, append_version=True)

def create_app():
    app = aiohttp.web.Application()
    # Config
    app.update(get_env_config())
    # Templates
    jj_env = aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')), autoescape=False)
    jj_env.tests['path_exists'] = path_exists
    # PG pool
    app.on_startup.append(init_pool)
    app.on_cleanup.append(close_pool)
    # Routes
    setup_routes(app)
    return app

def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description='LabxDB app.')
    parser.add_argument('--host', action='store', help='Host')
    parser.add_argument('--port', action='store', default=8090, help='Port', type=int)
    parser.add_argument('--static_path', action='store', default='static', help='Static path')
    parser.add_argument('--debug', action='store_true', default=False, help='Debug')
    parser.add_argument('--db_host', action='store', default='', help='Database host')
    parser.add_argument('--db_port', action='store', type=int, default=5432, help='Database port')
    parser.add_argument('--db_name', action='store', default='', help='Database name')
    parser.add_argument('--db_user', action='store', default='', help='Database user')
    parser.add_argument('--db_password', action='store', default='', help='Database password')
    parser.add_argument('--db_conn', action='store', type=int, default=1, help='Database connection number')
    args = parser.parse_args(argv[1:])

    # Add arguments to environment
    for k, v in vars(args).items():
        os.environ[ENV_PREFIX+k.upper()] = str(v)

    # Logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Application
    app = create_app()
    aiohttp.web.run_app(app, host=args.host, port=args.port)

if __name__ == '__main__':
    sys.exit(main())
