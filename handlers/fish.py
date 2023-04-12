#-*- coding: utf-8 -*-

#
# Copyright © 2018 Charles E. Vejnar
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

class FishBaseHandler(base.BaseHandler):
    name = 'fish'
    schema = 'fish'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Fish', 'url': 'fish', 'column_id': 'line_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'line_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Fish ID', 'tooltip': ''},
                     'y_number': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Y number', 'tooltip': 'Yale fish line number'},
                     'name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Name', 'tooltip': ''},
                     'genotype': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Genotype', 'tooltip': ''},
                     'date_birth': {'search_type': 'equal_date', 'gui_type': 'text', 'required': True, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'DOB', 'tooltip': 'Date of birth', 'button': {'label': 'Today', 'click': 'fish_today'}, 'default':'init_date'},
                     'father_id': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Father ID', 'tooltip': ''},
                     'father_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Father name', 'tooltip': ''},
                     'mother_id': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Mother ID', 'tooltip': ''},
                     'mother_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Mother name', 'tooltip': ''},
                     'number_fish': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'label': '# fish', 'tooltip': 'Number of fish'},
                     'number_tank': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'label': '# tank', 'tooltip': 'Number of tank'},
                     'author': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': True, 'label': 'Author', 'tooltip': ''},
                     'genotyping': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Genotyping', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'terminated': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Terminated', 'tooltip': ''},
                     'notes': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Notes', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'zfin_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'ZFIN ref', 'tooltip': 'Reference (ID) of fish line at ZFIN'}}]
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

@routes.view('/fish')
class FishDefaultHandler(generic.GenericDefaultHandler, FishBaseHandler):
    default_url = 'fish/table'

@routes.view('/fish/table')
class FishHandler(generic.GenericHandler, FishBaseHandler):
    tpl = 'generic_table.jinja'
    board_path = 'js/fish/board.js'
    board_class = 'FishTable'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'y_number', 'DESC', 'Y number']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'y_number'}, {'name':'name'}, {'name':'genotype'}, {'name':'date_birth'}, {'name':'notes'}, {'name':'father_id'}, {'name':'father_name'}, {'name':'mother_id'}, {'name':'mother_name'}, {'name':'number_fish'}, {'name':'number_tank'}, {'name':'author'}, {'name':'genotyping'}, {'name':'zfin_ref'}, {'name':'terminated'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {FishBaseHandler.schema}.line {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/fish/new')
class FishNewHandler(generic.GenericQueriesHandler, FishBaseHandler):
    tpl = 'generic_edit.jinja'

    form = [{'label':'Fish line', 'columns':[{'name':'name'}, {'name':'date_birth'}, {'name':'author'}, {'name':'terminated'}]},
            {'label':None, 'columns':[{'name':'number_fish'}, {'name':'number_tank'}]},
            {'label':'Description', 'columns':[{'name':'father_id'}, {'name':'father_name'}, {'name':'mother_id'}, {'name':'mother_name'}, {'name':'genotype'}, {'name':'zfin_ref'}]},
            {'label':None, 'columns':[{'name':'genotyping'}, {'name':'notes'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {FishBaseHandler.schema}.line ({{columns}}) VALUES ({{query_values}});"]

    async def post(self):
        # Get data
        data = await self.request.json()
        self.logger.debug(f'POST in: {data}')

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(f"LOCK TABLE {FishBaseHandler.schema}.line IN EXCLUSIVE MODE;")

                    # Get next Y number
                    max_y_number = await con.fetchval(f"SELECT MAX(y_number) FROM {FishBaseHandler.schema}.line;")
                    if max_y_number is None:
                        y_number = 1
                    else:
                        y_number = max_y_number + 1

                    # Add Y number
                    y_numbers = []
                    for idata in range(len(data)):
                        data[idata]['y_number'] = y_number
                        y_numbers.append(y_number)
                        y_number += 1

                    # Get queries
                    queries = self.get_queries(data)
                    # Run queries
                    for query, values in queries:
                        self.logger.debug(f'POST query: {query}')
                        # Add line
                        await con.execute(query, *values)

                    self.logger.debug(f'POST y_numbers: {y_numbers}')
                    return aiohttp.web.Response(body=json.dumps({'y_numbers': y_numbers}), content_type='application/json', headers={'Query-status': 'OK'})

        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

@routes.view('/fish/edit/{record_id}')
class FishEditHandler(generic.GenericRecordHandler, FishBaseHandler):
    tpl = 'generic_edit.jinja'
    form_class = 'TableForm'

    form = FishNewHandler.form
    form_json = FishNewHandler.form_json

    update_queries = [f"UPDATE {FishBaseHandler.schema}.line SET {{update_query}} WHERE line_id={{record_id}};"]

@routes.view('/fish/get/{record_id}')
class FishGetHandler(generic.GenericGetHandler, FishBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {FishBaseHandler.schema}.line WHERE line_id={{record_id}}) r;"]

@routes.view('/fish/remove/{record_id}')
class FishRemoveHandler(generic.GenericRemoveHandler, FishBaseHandler):
    queries = [f"DELETE FROM {FishBaseHandler.schema}.line WHERE line_id={{record_id}};"]

@routes.view('/fish/option')
class FishOptionHandler(generic.GenericHandler, FishBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'fish/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {FishBaseHandler.schema}.option {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/fish/option/new')
class FishOptionNewHandler(generic.GenericQueriesHandler, FishBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = FishOptionHandler.level_infos
    level_infos_json = FishOptionHandler.level_infos_json

    column_infos = FishOptionHandler.column_infos
    column_infos_json = FishOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {FishBaseHandler.schema}.option ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/fish/option/edit/{record_id}')
class FishOptionEditHandler(generic.GenericRecordHandler, FishBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = FishOptionHandler.level_infos
    level_infos_json = FishOptionHandler.level_infos_json

    column_infos = FishOptionHandler.column_infos
    column_infos_json = FishOptionHandler.column_infos_json

    form = FishOptionNewHandler.form
    form_json = FishOptionNewHandler.form_json

    update_queries = [f"UPDATE {FishBaseHandler.schema}.option SET {{update_query}} WHERE option_id={{record_id}};"]

@routes.view('/fish/option/get/{record_id}')
class FishOptionGetHandler(generic.GenericGetHandler, FishBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {FishBaseHandler.schema}.option WHERE option_id={{record_id}}) r;"]

@routes.view('/fish/option/remove/{record_id}')
class FishOptionRemoveHandler(generic.GenericRemoveHandler, FishBaseHandler):
    queries = [f"DELETE FROM {FishBaseHandler.schema}.option WHERE option_id={{record_id}};"]
