#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Copyright (C) 2018-2022 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import argparse
import collections
import os
import subprocess
import sys

def format_from_dict(tpl, d):
    return tpl.format_map(collections.defaultdict(str, d))


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(description='Format and execute SQL queries from template.')
    parser.add_argument('-d', '--db', dest='db', action='store', help='Database')
    parser.add_argument('-s', '--skip', dest='skip', action='store_true', help='Skip confirmation')
    parser.add_argument('-a', '--arg', dest='tpl_args', action='append', default=[], help='Template argument')
    parser.add_argument('-u', '--user', dest='db_user', action='store', help='Database user')
    parser.add_argument(dest='tpl_path', action='store', help='Template')
    args = parser.parse_args(argv[1:])

    # Prepare query
    query = format_from_dict(open(args.tpl_path).read(), dict([a.split(',') for a in args.tpl_args]))
    print(query)

    # Execute query
    if args.skip or input('Execute? (y/n) ') == 'y':
        cmd = ['psql']
        if args.db_user is not None:
            cmd.append('-U')
            cmd.append(args.db_user)
        if args.db is not None:
            cmd.append(args.db)
        p = subprocess.run(cmd, check=True, input=query, text=True)

if __name__ == '__main__':
    sys.exit(main())
