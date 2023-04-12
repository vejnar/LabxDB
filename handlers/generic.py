#-*- coding: utf-8 -*-

#
# Copyright © 2018 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import asyncio
import collections
import datetime
import json

import aiohttp.web
import aiohttp_jinja2
import asyncpg

from . import base

# ----------------------------------
# Helpers

def join_results(results):
    return '[' + ','.join(results) + ']'

def record2dict(results):
    new = []
    for r in results:
        if r == None:
            new.append(None)
        else:
            new.append(dict(r))
    return new

# ----------------------------------
# User input helpers

def isdate(text):
    try:
        datetime.datetime.strptime(text, '%Y-%m-%d')
    except ValueError:
        return False
    return True

def isbool(text):
    if text.lower() == 'true' or text.lower() == 't' or text.lower() == 'yes' or text.lower() == 'y' or text.lower() == 'false' or text.lower() == 'f' or text.lower() == 'no' or text.lower() == 'n':
        return True
    return False

# ----------------------------------
# Handlers

class GenericDefaultHandler(base.BaseHandler):
    async def get(self):
        raise aiohttp.web.HTTPTemporaryRedirect('/'.join([self.base_url, self.default_url]))

class GenericHandler(base.BaseHandler):
    def get_search_queries(self, search_criterions, search_prefixes, search_gate):
        # Parse
        crits = {}
        for c in search_criterions:
            i = c.find(' ')
            j = c.find(' ', i + 1)
            k = c.find(' ', j + 1)
            level = int(c[:i])
            column = c[i+1:j]
            search_type = c[j+1:k]
            text = c[k+1:]
            if level in crits:
                crits[level].append([column, search_type, text])
            else:
                crits[level] = [[column, search_type, text]]
        # Prepare
        search_queries = []
        for level, crit in crits.items():
            qys = []
            for column, search_type, text in crit:
                if column == 'ALL':
                    columns = [c['name'] for c in self.columns[level]]
                else:
                    columns = [column]
                for qcol in columns:
                    if text == 'NULL':
                        qys.append(qcol + ' IS NULL')
                    else:
                        st = self.column_infos[level][qcol]['search_type']
                        if st == 'ilike':
                            if search_type == 'EQUAL':
                                qys.append(qcol + ' = \'' + text + '\'')
                            elif search_type == 'FUZZY':
                                qys.append(qcol + ' ILIKE \'%' + text + '%\'')
                        elif st == 'equal_number' and text.replace('.', '', 1).isdigit():
                            qys.append(qcol + ' = ' + text)
                        elif st == 'equal_bool' and isbool(text):
                            qys.append(qcol + ' = \'' + text + '\'')
                        elif st == 'equal_date' and isdate(text):
                            qys.append(qcol + ' = \'' + text + '\'')
            if len(qys) > 0:
                search_queries.append([f'search_query_level{level}', search_prefixes[level] + '(' + (' ' + search_gate + ' ').join(qys) + ')'])
                for i in range(0, level):
                    search_queries.append([f'not_null_children_level{i}', 'WHERE children IS NOT NULL'])
        return search_queries

    def get_sort_queries(self, sort_criterions):
        # Default
        sort_queries = ['']
        if len(sort_criterions) > 0:
            sort_criterions = [c.split(' ') for c in sort_criterions]
        # Prepare
        crits = {}
        for c in sort_criterions:
            if c[0] in crits:
                crits[c[0]].append(c)
            else:
                crits[c[0]] = [c]
        return [['sort_query_level'+level, 'ORDER BY ' + ' , '.join([c[1] + ' ' + c[2] for c in crit])] for level, crit in crits.items()]

    def parse_query_args(self, args, default):
        if args is None:
            return default
        else:
            q = []
            for a in args:
                l = a.split(' ')
                q.append(l[:3] + [' '.join(l[3:])])
            return json.dumps(q)

    def select_query_arg(self, arg, default, default_json):
        if arg is None:
            return default_json
        else:
            return json.dumps([[d[0], d[1], d[1]==arg] for d in default])

    async def get(self):
        query_args = self.request.query
        return aiohttp_jinja2.render_template(self.tpl, self.request, {'name': self.name,
                                                                       'base_url': self.base_url,
                                                                       'board_path': self.board_path,
                                                                       'board_class': self.board_class,
                                                                       'levels': self.levels_json,
                                                                       'level_infos': self.level_infos_json,
                                                                       'columns': self.columns_json,
                                                                       'column_titles': self.column_titles_json,
                                                                       'column_infos': self.column_infos_json,
                                                                       'search_criterions': self.parse_query_args(query_args.getall('search_criterion', None), self.default_search_criterions_json),
                                                                       'sort_criterions': self.parse_query_args(query_args.getall('sort_criterion', None), self.default_sort_criterions_json),
                                                                       'limits': self.select_query_arg(query_args.get('limit', None), self.default_limits, self.default_limits_json)})

    async def post(self):
        data = await self.request.post()
        self.logger.debug(f'POST in: {data}')

        # Execute queries
        try:
            tasks = []
            for iquery, query in enumerate(self.queries):
                # Prepare query
                search_queries = self.get_search_queries(data.getall('search_criterion', []), self.queries_search_prefixes[iquery], data.get('search_gate', 'OR'))
                sort_queries = self.get_sort_queries(data.getall('sort_criterion', []))
                limit_query = [['limit', data['limit']]]
                # Assemble final query
                fquery = query.format_map(collections.defaultdict(str, dict(search_queries + sort_queries + limit_query)))
                self.logger.debug(f'POST query: {fquery}')
                # Add query to tasks
                tasks.append(self.pool.fetchval(fquery))
            results = await asyncio.gather(*tasks)
        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

        self.logger.debug(f'POST out: {results[0]}')
        return aiohttp.web.Response(body=results[0], content_type='application/json', headers={'Query-status': 'OK'})

class GenericQueriesHandler(base.BaseHandler):
    def get_queries(self, data):
        queries = []
        for idata in range(len(data)):
            columns = []
            query_values = []
            values = []
            i = 1
            for column, v in data[idata].items():
                columns.append(column)
                query_values.append(f'${i}')
                values.append(v)
                i += 1
            if len(columns) > 0:
                for query in self.insert_queries:
                    queries.append([query.format(columns=','.join(columns), query_values=','.join(query_values)), values])
        return queries

    async def get(self):
        query_args = dict(self.request.query.items())
        return aiohttp_jinja2.render_template(self.tpl, self.request, {'name': self.name,
                                                                       'base_url': self.base_url,
                                                                       'levels': self.levels_json,
                                                                       'level_infos': self.level_infos_json,
                                                                       'columns': self.columns_json,
                                                                       'column_infos': self.column_infos_json,
                                                                       'form_path': self.form_path,
                                                                       'form_class': self.form_class,
                                                                       'form': self.form_json,
                                                                       'only_changes': 'false',
                                                                       'query_args': query_args})

    async def post(self):
        # Get data
        data = await self.request.json()
        self.logger.debug(f'POST in: {data}')
        # Execute queries
        try:
            tasks = []
            for query, values in self.get_queries(data):
                tasks.append(self.pool.fetchrow(query, *values))
                self.logger.debug(f'POST query: {query}')
            results = await asyncio.gather(*tasks)
        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

        self.logger.debug(f'POST out: {results}')
        return aiohttp.web.Response(body=json.dumps(record2dict(results)), content_type='application/json', headers={'Query-status': 'OK'})

class GenericRecordHandler(base.BaseHandler):
    def get_queries(self, data, record_id):
        queries = []
        for idata in range(len(data)):
            columns = []
            values = []
            i = 1
            for k, v in data[idata].items():
                columns.append(f'{k}=${i}')
                values.append(v)
                i += 1
            if len(columns) > 0:
                for query in self.update_queries:
                    queries.append([query.format(update_query=','.join(columns), record_id=record_id), values])
        return queries

    async def get(self):
        query_args = {'record_id': self.request.match_info['record_id'], 'count': 1}
        return aiohttp_jinja2.render_template(self.tpl, self.request, {'name': self.name,
                                                                       'base_url': self.base_url,
                                                                       'levels': self.levels_json,
                                                                       'level_infos': self.level_infos_json,
                                                                       'columns': self.columns_json,
                                                                       'column_infos': self.column_infos_json,
                                                                       'form_path': self.form_path,
                                                                       'form_class': self.form_class,
                                                                       'form': self.form_json,
                                                                       'only_changes': 'true',
                                                                       'query_args': query_args})

    async def post(self):
        # Get record ID & data
        record_id = self.request.match_info['record_id']
        data = await self.request.json()
        self.logger.debug(f'POST in: {data}')
        # Execute queries
        if len(data) > 0:
            try:
                tasks = []
                for query, values in self.get_queries(data, record_id):
                    self.logger.debug(f'POST query: {query}')
                    tasks.append(self.pool.fetchrow(query, *values))
                results = await asyncio.gather(*tasks)
            except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
                self.logger.error(error)
                return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

        self.logger.debug(f'POST out: {results}')
        return aiohttp.web.Response(body=json.dumps(record2dict(results)), content_type='application/json', headers={'Query-status': 'OK'})

class GenericGetHandler(base.BaseHandler):
    async def get(self):
        # Get record ID
        record_id = self.request.match_info['record_id']
        # Execute queries
        try:
            tasks = []
            for query in self.queries:
                self.logger.debug(query.format(record_id = record_id))
                tasks.append(self.pool.fetchval(query.format(record_id = record_id)))
            results = await asyncio.gather(*tasks)
        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

        self.logger.debug(f'GET out: {results}')
        return aiohttp.web.Response(body=join_results(results), content_type='application/json', headers={'Query-status': 'OK'})

class GenericRemoveHandler(base.BaseHandler):
    async def get(self):
        # Get record ID
        record_id = self.request.match_info['record_id']
        # Execute queries
        try:
            tasks = []
            for query in self.queries:
                self.logger.debug(query.format(record_id = record_id))
                tasks.append(self.pool.fetchval(query.format(record_id = record_id)))
            results = await asyncio.gather(*tasks)
        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

        return aiohttp.web.Response(text='OK', headers={'Query-status': 'OK'})
