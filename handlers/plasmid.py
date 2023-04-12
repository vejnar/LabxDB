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

class PlasmidBaseHandler(base.BaseHandler):
    name = 'plasmid'
    schema = 'plasmid'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Plasmid', 'url': 'plasmid', 'column_id': 'item_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'item_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Plasmid ID', 'tooltip': ''},
                     'plasmid_number': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Plasmid number', 'tooltip': ''},
                     'number_suffix': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Suffix', 'tooltip': ''},
                     'name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Name', 'tooltip': 'Unique plasmid name'},
                     'author': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Author', 'tooltip': 'First name of author'},
                     'description': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Description', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'sequence': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': True, 'label': 'Sequence', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'sequence_insert': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Insert', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'map_img': {'search_type': 'data', 'gui_type': 'file', 'accept':'image/png', 'required': True, 'label': 'Map', 'tooltip': 'Image of plasmid map (PNG format)', 'maxsize':786000},
                     'map_filename': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'pattern': '[A-Za-z0-9._-]+', 'label': 'File name', 'tooltip': 'Name of Snapgene, ApE (...) file', 'button': {'label': 'Filename', 'click': 'plasmid_filename'}},
                     'antibiotic': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Antibiotic', 'tooltip': ''},
                     'linearize_sense': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Linearize', 'tooltip': 'Linearize sense'},
                     'promoter_sense': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Promoter', 'tooltip': 'Promoter sense'},
                     'vector': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Vector', 'tooltip': ''},
                     'cloning_strategy': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Cloning', 'tooltip': 'Cloning strategy', 'class': 'seq-text'},
                     'glycerol_stock': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Glycerol', 'tooltip': 'Glycerol stock'},
                     'missing': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Missing', 'tooltip': 'Missing'},
                     'date_insert': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Date', 'tooltip': 'Plasmid creation date', 'button': {'label': 'Today', 'click': 'plasmid_today'}, 'default': 'init_date'}}]
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

@routes.view('/plasmid')
class PlasmidDefaultHandler(generic.GenericDefaultHandler, PlasmidBaseHandler):
    default_url = 'plasmid/table'

@routes.view('/plasmid/table')
class PlasmidHandler(generic.GenericHandler, PlasmidBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'plasmid_number', 'DESC', 'Plasmid number']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'plasmid_number'}, {'name':'number_suffix'}, {'name':'name'}, {'name':'author'}, {'name':'description'}, {'name':'antibiotic'}, {'name':'linearize_sense'}, {'name':'promoter_sense'}, {'name':'vector'}, {'name':'cloning_strategy'}, {'name':'sequence'}, {'name':'sequence_insert'}, {'name':'map_img', 'gui_type':'tooltip_img'}, {'name':'map_filename'}, {'name':'glycerol_stock'}, {'name':'missing'}, {'name':'date_insert'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {PlasmidBaseHandler.schema}.item {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/plasmid/new')
class PlasmidNewHandler(generic.GenericQueriesHandler, PlasmidBaseHandler):
    tpl = 'generic_edit.jinja'

    form = [{'label':'Plasmid', 'columns':[{'name':'name'}, {'name':'author'}, {'name':'map_filename'}]},
            {'label':None, 'columns':[{'name':'description'}, {'name':'cloning_strategy'}]},
            {'label':'Sequence', 'columns':[{'name':'sequence'}, {'name':'sequence_insert'}]},
            {'label':'Details', 'columns':[{'name':'antibiotic'}, {'name':'linearize_sense'}, {'name':'promoter_sense'}, {'name':'vector'}, {'name':'glycerol_stock'}, {'name':'missing'}, {'name':'date_insert'}]},
            {'label':None, 'columns':[{'name':'map_img'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {PlasmidBaseHandler.schema}.item ({{columns}}) VALUES ({{query_values}});"]

    def get_map_filename(self, plasmid_number, map_filename):
        if map_filename is None:
            return None
        elif map_filename.startswith('_') or map_filename.startswith('-') or map_filename.startswith(' '):
            return f'{plasmid_number}{map_filename}'
        else:
            return f'{plasmid_number}_{map_filename}'

    async def post(self):
        # Get data
        data = await self.request.json()
        self.logger.debug(f'POST in: {data}')

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(f"LOCK TABLE {PlasmidBaseHandler.schema}.item IN EXCLUSIVE MODE;")

                    # Get next plasmid number
                    max_plasmid_number = await con.fetchval(f"SELECT MAX(plasmid_number) FROM {PlasmidBaseHandler.schema}.item;")
                    if max_plasmid_number is None:
                        plasmid_number = 1
                    else:
                        plasmid_number = max_plasmid_number + 1

                    # Add plasmid number & Update map_filename
                    plasmid_numbers = []
                    for idata in range(len(data)):
                        data[idata]['plasmid_number'] = plasmid_number
                        data[idata]['map_filename'] = self.get_map_filename(plasmid_number, data[idata]['map_filename'])
                        plasmid_numbers.append(plasmid_number)
                        plasmid_number += 1

                    # Get queries
                    queries = self.get_queries(data)
                    # Run queries
                    for query, values in queries:
                        self.logger.debug(f'POST query: {query}')
                        # Add item
                        await con.execute(query, *values)

                    self.logger.debug(f'POST plasmid_numbers: {plasmid_numbers}')
                    return aiohttp.web.Response(body=json.dumps({'plasmid_numbers': plasmid_numbers}), content_type='application/json', headers={'Query-status': 'OK'})

        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

@routes.view('/plasmid/edit/{record_id}')
class PlasmidEditHandler(generic.GenericRecordHandler, PlasmidBaseHandler):
    tpl = 'generic_edit.jinja'

    form = PlasmidNewHandler.form
    form_json = PlasmidNewHandler.form_json

    update_queries = [f"UPDATE {PlasmidBaseHandler.schema}.item SET {{update_query}} WHERE item_id={{record_id}};"]

@routes.view('/plasmid/get/{record_id}')
class PlasmidGetHandler(generic.GenericGetHandler, PlasmidBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {PlasmidBaseHandler.schema}.item WHERE item_id={{record_id}}) r;"]

@routes.view('/plasmid/remove/{record_id}')
class PlasmidRemoveHandler(generic.GenericRemoveHandler, PlasmidBaseHandler):
    queries = [f"DELETE FROM {PlasmidBaseHandler.schema}.item WHERE item_id={{record_id}};"]

@routes.view('/plasmid/batch')
class PlasmidBatchHandler(PlasmidNewHandler):
    tpl = 'generic_edit.jinja'
    form_path = 'js/batchform.js'
    form_class = 'BatchForm'

@routes.view('/plasmid/option')
class PlasmidOptionHandler(generic.GenericHandler, PlasmidBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'plasmid/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {PlasmidBaseHandler.schema}.option {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/plasmid/option/new')
class PlasmidOptionNewHandler(generic.GenericQueriesHandler, PlasmidBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = PlasmidOptionHandler.level_infos
    level_infos_json = PlasmidOptionHandler.level_infos_json

    column_infos = PlasmidOptionHandler.column_infos
    column_infos_json = PlasmidOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {PlasmidBaseHandler.schema}.option ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/plasmid/option/edit/{record_id}')
class PlasmidOptionEditHandler(generic.GenericRecordHandler, PlasmidBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = PlasmidOptionHandler.level_infos
    level_infos_json = PlasmidOptionHandler.level_infos_json

    column_infos = PlasmidOptionHandler.column_infos
    column_infos_json = PlasmidOptionHandler.column_infos_json

    form = PlasmidOptionNewHandler.form
    form_json = PlasmidOptionNewHandler.form_json

    update_queries = [f"UPDATE {PlasmidBaseHandler.schema}.option SET {{update_query}} WHERE option_id={{record_id}};"]

@routes.view('/plasmid/option/get/{record_id}')
class PlasmidOptionGetHandler(generic.GenericGetHandler, PlasmidBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {PlasmidBaseHandler.schema}.option WHERE option_id={{record_id}}) r;"]

@routes.view('/plasmid/option/remove/{record_id}')
class PlasmidOptionRemoveHandler(generic.GenericRemoveHandler, PlasmidBaseHandler):
    queries = [f"DELETE FROM {PlasmidBaseHandler.schema}.option WHERE option_id={{record_id}};"]
