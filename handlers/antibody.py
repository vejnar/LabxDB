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

class AntibodyBaseHandler(base.BaseHandler):
    name = 'antibody'
    schema = 'antibody'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Antibody', 'url': 'antibody', 'column_id': 'item_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'item_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Antibody ID', 'tooltip': ''},
                     'antibody_id': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'pattern': '([0-9]+|[A-Z]+)', 'label': 'Antibody ID', 'tooltip': 'ID name depends on storage temperature (Number for -20C; alphabet for 4C)'},
                     'name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Antibody Name', 'tooltip': 'Please include all alternative names/abbreviations to facilitate searching'},
                     'storage_temp': {'search_type': 'equal_number', 'gui_type': 'select_option_none', 'required': True, 'pattern': '[0-9]+', 'label': 'Temp.', 'tooltip': 'Storage temperature'},
                     'host_animal': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': True, 'label': 'Host', 'tooltip': 'Host animal'},
                     'size_confirmed': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Size Confirmed', 'tooltip': 'Confirmed size in zebrafish'},
                     'wb_confirmed': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'WB Confirmed Dilution', 'tooltip': 'Dilution for WB that is confirmed in lab', 'class': 'seq-text', 'maxlength': '10000'},
                     'icc_if_confirmed': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'IF/ICC Confirmed Dilution', 'tooltip': 'Dilution for IF/ICC that is confirmed in lab', 'class': 'seq-text', 'maxlength': '10000'},
                     'ip_confirmed': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'IP Confirmed Dilution', 'tooltip': 'Dilution for IP that is confirmed in lab', 'class': 'seq-text', 'maxlength': '10000'},
                     'app_confirmed': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Other Application Confirmed', 'tooltip': 'Dilution for other applications that is confirmed in lab', 'class': 'seq-text', 'maxlength': '10000'},
                     'practical_notes': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Practical Notes', 'tooltip': 'Other practical notes', 'class': 'seq-text', 'maxlength': '10000'},
                     'clonal': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': True, 'label': 'Clonal', 'tooltip': 'Monoclonal or Polyclonal'},
                     'mol_weight': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Molecular Weight', 'tooltip': 'Molecular weight of the antigen'},
                     'app_suggested': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Suggested Applications', 'tooltip': 'Suggested applications by the manufacturer', 'class': 'seq-text', 'maxlength': '10000'},
                     'size_suggested': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Suggested Size', 'tooltip': 'Suggested size by the manufacturer'},
                     'manufacturer': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Manufacturer', 'tooltip': ''},
                     'manufacturer_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Manufacturer Reference', 'tooltip': ''},
                     'concentration': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Concentration', 'tooltip': 'As labeled on the tube or online'},
                     'date_received': {'search_type': 'equal_date', 'gui_type': 'text', 'required': True, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Date Received', 'tooltip': '', 'button': {'label': 'Today', 'click': 'received_today'}, 'default':'init_date'},
                     'lot_num': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Lot Number', 'tooltip': 'Put the latest one on top, do not delete old records'},
                     'custom_antibody': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': True, 'label': 'Custom Antibody', 'tooltip': 'Custom antibody?', 'default':'init_custom'}}]
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

@routes.view('/antibody')
class AntibodyDefaultHandler(generic.GenericDefaultHandler, AntibodyBaseHandler):
    default_url = 'antibody/table'

@routes.view('/antibody/table')
class AntibodyHandler(generic.GenericHandler, AntibodyBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'storage_temp', 'ASC', 'Temp.'], [0, "lpad(antibody_id,10,'0')", 'DESC', 'ID']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'antibody_id'}, {'name':'name'}, {'name':'storage_temp'}, {'name':'host_animal'}, {'name':'size_confirmed'}, {'name':'wb_confirmed'}, {'name':'icc_if_confirmed'}, {'name':'ip_confirmed'}, {'name':'app_confirmed'}, {'name':'practical_notes'}, {'name':'clonal'}, {'name':'mol_weight'}, {'name':'app_suggested'}, {'name':'size_suggested'}, {'name':'manufacturer'}, {'name':'manufacturer_ref'}, {'name':'concentration'}, {'name':'date_received'}, {'name':'lot_num'}, {'name':'custom_antibody'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {AntibodyBaseHandler.schema}.item {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/antibody/new')
class AntibodyNewHandler(generic.GenericQueriesHandler, AntibodyBaseHandler):
    tpl = 'generic_edit.jinja'

    form = [{'label':'Antibody', 'columns':[{'name':'antibody_id'}, {'name':'name'}, {'name':'storage_temp'}, {'name':'host_animal'}, {'name':'clonal'}, {'name':'mol_weight'}, {'name':'size_confirmed'}]},
            {'label':'Confirmed Applications', 'columns':[{'name':'wb_confirmed'}, {'name':'icc_if_confirmed'}, {'name':'ip_confirmed'}, {'name':'app_confirmed'}, {'name':'practical_notes'}]},
            {'label':'Suggested Usage', 'columns':[{'name':'app_suggested'}]},
            {'label':None, 'columns':[{'name':'size_suggested'}]},
            {'label':'Manufacturer', 'columns':[{'name':'manufacturer'}, {'name':'manufacturer_ref'}, {'name':'concentration'}, {'name':'date_received'}, {'name':'lot_num'}, {'name':'custom_antibody'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {AntibodyBaseHandler.schema}.item ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/antibody/edit/{record_id}')
class AntibodyEditHandler(generic.GenericRecordHandler, AntibodyBaseHandler):
    tpl = 'generic_edit.jinja'

    form = AntibodyNewHandler.form
    form_json = AntibodyNewHandler.form_json

    update_queries = [f"UPDATE {AntibodyBaseHandler.schema}.item SET {{update_query}} WHERE item_id={{record_id}};"]

@routes.view('/antibody/get/{record_id}')
class AntibodyGetHandler(generic.GenericGetHandler, AntibodyBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {AntibodyBaseHandler.schema}.item WHERE item_id={{record_id}}) r;"]

@routes.view('/antibody/remove/{record_id}')
class AntibodyRemoveHandler(generic.GenericRemoveHandler, AntibodyBaseHandler):
    queries = [f"DELETE FROM {AntibodyBaseHandler.schema}.item WHERE item_id={{record_id}};"]

@routes.view('/antibody/option')
class AntibodyOptionHandler(generic.GenericHandler, AntibodyBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'antibody/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {AntibodyBaseHandler.schema}.option {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/antibody/option/new')
class AntibodyOptionNewHandler(generic.GenericQueriesHandler, AntibodyBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = AntibodyOptionHandler.level_infos
    level_infos_json = AntibodyOptionHandler.level_infos_json

    column_infos = AntibodyOptionHandler.column_infos
    column_infos_json = AntibodyOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {AntibodyBaseHandler.schema}.option ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/antibody/option/edit/{record_id}')
class AntibodyOptionEditHandler(generic.GenericRecordHandler, AntibodyBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = AntibodyOptionHandler.level_infos
    level_infos_json = AntibodyOptionHandler.level_infos_json

    column_infos = AntibodyOptionHandler.column_infos
    column_infos_json = AntibodyOptionHandler.column_infos_json

    form = AntibodyOptionNewHandler.form
    form_json = AntibodyOptionNewHandler.form_json

    update_queries = [f"UPDATE {AntibodyBaseHandler.schema}.option SET {{update_query}} WHERE option_id={{record_id}};"]

@routes.view('/antibody/option/get/{record_id}')
class AntibodyOptionGetHandler(generic.GenericGetHandler, AntibodyBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {AntibodyBaseHandler.schema}.option WHERE option_id={{record_id}}) r;"]

@routes.view('/antibody/option/remove/{record_id}')
class AntibodyOptionRemoveHandler(generic.GenericRemoveHandler, AntibodyBaseHandler):
    queries = [f"DELETE FROM {AntibodyBaseHandler.schema}.option WHERE option_id={{record_id}};"]
