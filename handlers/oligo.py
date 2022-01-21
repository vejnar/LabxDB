#-*- coding: utf-8 -*-

#
# Copyright (C) 2018-2022 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import json

import aiohttp.web
import asyncpg

from . import base
from . import generic

routes = aiohttp.web.RouteTableDef()

class OligoBaseHandler(base.BaseHandler):
    name = 'oligo'
    schema = 'oligo'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Oligo', 'url': 'oligo', 'column_id': 'item_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'item_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Oligo ID', 'tooltip': ''},
                     'oligo_number': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Oligo number', 'tooltip': ''},
                     'number_suffix': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Suffix', 'tooltip': ''},
                     'name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Name', 'tooltip': 'Unique oligo name'},
                     'description': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Description', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'sequence': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Sequence', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'author': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': True, 'label': 'Author', 'tooltip': 'First name of author'},
                     'date_insert': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Date', 'tooltip': 'Oligo creation date', 'button': {'label': 'Today', 'click': 'oligo_today'}, 'default':'init_date'},
                     'date_order': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Order', 'tooltip': '', 'button': {'label': 'Order today', 'click': 'oligo_today_status'}},
                     'status': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Status', 'tooltip': '', 'default':'init_status'}}]
    column_infos_json = json.dumps(column_infos)

    column_titles = []
    column_titles_json = json.dumps(column_titles)

    default_search_criterions = []
    default_search_criterions_json = json.dumps(default_search_criterions)

    default_sort_criterions = []
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    default_limits = [['All', 'ALL', False], ['10', '10', False], ['100', '100', True], ['500', '500', False]]
    default_limits_json = json.dumps(default_limits)

    columns = []
    columns_json = json.dumps(columns)

    form = []
    form_json = json.dumps(form)

    board_path = 'js/table.js'
    board_class = 'Table'
    form_path = 'js/tableform.js'
    form_class = 'TableForm'

@routes.view('/oligo')
class OligoDefaultHandler(generic.GenericDefaultHandler, OligoBaseHandler):
    default_url = 'oligo/table'

@routes.view('/oligo/table')
class OligoHandler(generic.GenericHandler, OligoBaseHandler):
    tpl = 'generic_table.jinja'
    board_path = 'js/oligo/board.js'
    board_class = 'OligoTable'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'oligo_number', 'DESC', 'Oligo number']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'oligo_number'}, {'name':'number_suffix'}, {'name':'name'}, {'name':'description'}, {'name':'sequence'}, {'name':'author'}, {'name':'date_insert'}, {'name':'date_order'}, {'name':'status'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {OligoBaseHandler.schema}.item {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/oligo/new')
class OligoNewHandler(generic.GenericQueriesHandler, OligoBaseHandler):
    tpl = 'generic_edit.jinja'

    form = [{'label':'Oligo', 'columns':[{'name':'name'}, {'name':'author'}, {'name':'date_insert'}, {'name':'status'}, {'name':'date_order'}]},
            {'label':None, 'columns':[{'name':'description'}, {'name':'sequence'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {OligoBaseHandler.schema}.item ({{columns}}) VALUES ({{query_values}});"]

    def get_oligo_name(self, oligo_number, name):
        if name.startswith('_') or name.startswith('-') or name.startswith(' '):
            return f'{oligo_number}{name}'
        else:
            return f'{oligo_number}_{name}'

    async def post(self):
        # Get data
        data = await self.request.json()
        self.logger.debug(f'POST in: {data}')

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(f"LOCK TABLE {OligoBaseHandler.schema}.item IN EXCLUSIVE MODE;")

                    # Get next oligo number
                    max_oligo_number = await con.fetchval(f"SELECT MAX(oligo_number) FROM {OligoBaseHandler.schema}.item;")
                    if max_oligo_number is None:
                        oligo_number = 1
                    else:
                        oligo_number = max_oligo_number + 1

                    # Add oligo number & Update name
                    oligo_numbers = []
                    for idata in range(len(data)):
                        data[idata]['oligo_number'] = oligo_number
                        data[idata]['name'] = self.get_oligo_name(oligo_number, data[idata]['name'])
                        oligo_numbers.append(oligo_number)
                        oligo_number += 1

                    # Get queries
                    queries = self.get_queries(data)
                    # Run queries
                    for query, values in queries:
                        self.logger.debug(f'POST query: {query}')
                        # Add item
                        await con.execute(query, *values)

                    self.logger.debug(f'POST oligo_numbers: {oligo_numbers}')
                    return aiohttp.web.Response(body=json.dumps({'oligo_numbers': oligo_numbers}), content_type='application/json', headers={'Query-status': 'OK'})

        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error)})

@routes.view('/oligo/edit/{record_id}')
class OligoEditHandler(generic.GenericRecordHandler, OligoBaseHandler):
    tpl = 'generic_edit.jinja'

    form = OligoNewHandler.form
    form_json = OligoNewHandler.form_json

    update_queries = [f"UPDATE {OligoBaseHandler.schema}.item SET {{update_query}} WHERE item_id={{record_id}};"]

@routes.view('/oligo/get/{record_id}')
class OligoGetHandler(generic.GenericGetHandler, OligoBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {OligoBaseHandler.schema}.item WHERE item_id={{record_id}}) r;"]

@routes.view('/oligo/remove/{record_id}')
class OligoRemoveHandler(generic.GenericRemoveHandler, OligoBaseHandler):
    queries = [f"DELETE FROM {OligoBaseHandler.schema}.item WHERE item_id={{record_id}};"]

@routes.view('/oligo/batch')
class OligoBatchHandler(OligoNewHandler):
    tpl = 'generic_edit.jinja'
    form_path = 'js/batchform.js'
    form_class = 'BatchForm'

@routes.view('/oligo/option')
class OligoOptionHandler(generic.GenericHandler, OligoBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'oligo/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {OligoBaseHandler.schema}.option {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/oligo/option/new')
class OligoOptionNewHandler(generic.GenericQueriesHandler, OligoBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = OligoOptionHandler.level_infos
    level_infos_json = OligoOptionHandler.level_infos_json

    column_infos = OligoOptionHandler.column_infos
    column_infos_json = OligoOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {OligoBaseHandler.schema}.option ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/oligo/option/edit/{record_id}')
class OligoOptionEditHandler(generic.GenericRecordHandler, OligoBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = OligoOptionHandler.level_infos
    level_infos_json = OligoOptionHandler.level_infos_json

    column_infos = OligoOptionHandler.column_infos
    column_infos_json = OligoOptionHandler.column_infos_json

    form = OligoOptionNewHandler.form
    form_json = OligoOptionNewHandler.form_json

    update_queries = [f"UPDATE {OligoBaseHandler.schema}.option SET {{update_query}} WHERE option_id={{record_id}};"]

@routes.view('/oligo/option/get/{record_id}')
class OligoOptionGetHandler(generic.GenericGetHandler, OligoBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {OligoBaseHandler.schema}.option WHERE option_id={{record_id}}) r;"]

@routes.view('/oligo/option/remove/{record_id}')
class OligoOptionRemoveHandler(generic.GenericRemoveHandler, OligoBaseHandler):
    queries = [f"DELETE FROM {OligoBaseHandler.schema}.option WHERE option_id={{record_id}};"]
