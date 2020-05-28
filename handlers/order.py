#-*- coding: utf-8 -*-

#
# Copyright (C) 2018-2020 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import json

import aiohttp.web

from . import base
from . import generic

routes = aiohttp.web.RouteTableDef()

class OrderBaseHandler(base.BaseHandler):
    name = 'order'
    schema = 'purchase'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Order', 'url': 'order', 'column_id': 'item_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'item_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Order ID', 'tooltip': ''},
                     'item': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Item', 'tooltip': ''},
                     'item_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Item ref', 'tooltip': 'Item reference or Catalog number'},
                     'item_size': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Size', 'tooltip': ''},
                     'provider': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Provider', 'tooltip': 'Where to order?'},
                     'provider_stockroom': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': True, 'label': 'Skr', 'tooltip': 'Is this item available in the stockroom?'},
                     'quantity': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'label': 'Qty', 'tooltip': ''},
                     'unit_price': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'label': 'Price', 'tooltip': 'Price per unit'},
                     'total_price': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'label': 'Total', 'tooltip': '', 'button': {'label': 'Update total', 'click': 'order_total'}},
                     'status': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': True, 'label': 'Status', 'tooltip': '', 'default':'init_status'},
                     'recipient': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': True, 'label': 'Recipient', 'tooltip': ''},
                     'date_insert': {'search_type': 'equal_date', 'gui_type': 'text', 'required': True, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Date', 'tooltip': 'Order creation date', 'button': {'label': 'Today', 'click': 'order_today'}, 'default':'init_date'},
                     'date_order': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Order', 'tooltip': '', 'button': {'label': 'Today', 'click': 'order_today_status'}},
                     'manufacturer': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Manufacturer', 'tooltip': ''},
                     'manufacturer_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Manufacturer ref', 'tooltip': ''},
                     'funding': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Funding', 'tooltip': ''}}]
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

@routes.view('/order')
class OrderDefaultHandler(generic.GenericDefaultHandler, OrderBaseHandler):
    default_url = 'order/table'

@routes.view('/order/table')
class OrderHandler(generic.GenericHandler, OrderBaseHandler):
    tpl = 'generic_table.jinja'
    board_path = 'js/order/board.js'
    board_class = 'OrderTable'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'date_order', 'DESC', 'Order'], [0, 'provider_stockroom', 'ASC', 'Skr'], [0, 'provider', 'ASC', 'Provider']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'item'}, {'name':'item_ref'}, {'name':'item_size'}, {'name':'provider'}, {'name':'provider_stockroom'}, {'name':'unit_price'}, {'name':'quantity'}, {'name':'total_price'}, {'name':'status'}, {'name':'recipient'}, {'name':'date_insert'}, {'name':'date_order'}, {'name':'manufacturer'}, {'name':'manufacturer_ref'}, {'name':'funding'}]]
    columns_json = json.dumps(columns)

    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.item {search_query_level0} {sort_query_level0} LIMIT {limit}) r;"%OrderBaseHandler.schema]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/order/new')
class OrderNewHandler(generic.GenericQueriesHandler, OrderBaseHandler):
    tpl = 'generic_edit.jinja'

    form = [{'label':'Order', 'columns':[{'name':'item'}, {'name':'item_ref'}, {'name':'item_size'}, {'name':'date_insert'}, {'name':'recipient'}, {'name':'funding'}]},
            {'label':None, 'columns':[{'name':'unit_price'}, {'name':'quantity'}, {'name':'total_price'}]},
            {'label':'Status', 'columns':[{'name':'status'}, {'name':'date_order'}]},
            {'label':'Provider', 'columns':[{'name':'provider'}, {'name':'provider_stockroom'}, {'name':'manufacturer'}, {'name':'manufacturer_ref'}]}]
    form_json = json.dumps(form)

    insert_queries = ["INSERT INTO %s.item ({columns}) VALUES ({query_values});"%OrderBaseHandler.schema]

@routes.view('/order/edit/{record_id}')
class OrderEditHandler(generic.GenericRecordHandler, OrderBaseHandler):
    tpl = 'generic_edit.jinja'
    form_class = 'TableForm'

    form = OrderNewHandler.form
    form_json = OrderNewHandler.form_json

    update_queries = ["UPDATE %s.item SET {update_query} WHERE item_id={record_id};"%OrderBaseHandler.schema]

@routes.view('/order/get/{record_id}')
class OrderGetHandler(generic.GenericGetHandler, OrderBaseHandler):
    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.item WHERE item_id={record_id}) r;"%OrderBaseHandler.schema]

@routes.view('/order/remove/{record_id}')
class OrderRemoveHandler(generic.GenericRemoveHandler, OrderBaseHandler):
    queries = ["DELETE FROM %s.item WHERE item_id={record_id};"%OrderBaseHandler.schema]

@routes.view('/order/option')
class OrderOptionHandler(generic.GenericHandler, OrderBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'order/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.option {search_query_level0} {sort_query_level0} LIMIT {limit}) r;"%OrderBaseHandler.schema]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/order/option/new')
class OrderOptionNewHandler(generic.GenericQueriesHandler, OrderBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = OrderOptionHandler.level_infos
    level_infos_json = OrderOptionHandler.level_infos_json

    column_infos = OrderOptionHandler.column_infos
    column_infos_json = OrderOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = ["INSERT INTO %s.option ({columns}) VALUES ({query_values});"%OrderBaseHandler.schema]

@routes.view('/order/option/edit/{record_id}')
class OrderOptionEditHandler(generic.GenericRecordHandler, OrderBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = OrderOptionHandler.level_infos
    level_infos_json = OrderOptionHandler.level_infos_json

    column_infos = OrderOptionHandler.column_infos
    column_infos_json = OrderOptionHandler.column_infos_json

    form = OrderOptionNewHandler.form
    form_json = OrderOptionNewHandler.form_json

    update_queries = ["UPDATE %s.option SET {update_query} WHERE option_id={record_id};"%OrderBaseHandler.schema]

@routes.view('/order/option/get/{record_id}')
class OrderOptionGetHandler(generic.GenericGetHandler, OrderBaseHandler):
    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.option WHERE option_id={record_id}) r;"%OrderBaseHandler.schema]

@routes.view('/order/option/remove/{record_id}')
class OrderOptionRemoveHandler(generic.GenericRemoveHandler, OrderBaseHandler):
    queries = ["DELETE FROM %s.option WHERE option_id={record_id};"%OrderBaseHandler.schema]
