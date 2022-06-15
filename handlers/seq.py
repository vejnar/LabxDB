#-*- coding: utf-8 -*-

#
# Copyright (C) 2018-2022 Charles E. Vejnar
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
#

import asyncio
import json

import aiohttp.web
import asyncpg

from . import base
from . import generic

routes = aiohttp.web.RouteTableDef()

class SeqBaseHandler(base.BaseHandler):
    name = 'seq'
    schema = 'seq'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Project', 'url': 'seq/project', 'column_ref': 'project_ref', 'column_id': 'project_id'},
                   {'label': 'Sample', 'url': 'seq/sample', 'column_ref': 'sample_ref', 'column_id': 'sample_id'},
                   {'label': 'Replicate', 'url': 'seq/replicate', 'column_ref': 'replicate_ref', 'column_order': 'replicate_order', 'column_id': 'replicate_id'},
                   {'label': 'Run', 'url': 'seq/run', 'column_ref': 'run_ref', 'column_order': 'run_order', 'column_id': 'run_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'project_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Project ID', 'tooltip': ''},
                     'project_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Project', 'tooltip': ''},
                     'project_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'pattern': '[a-z][a-z0-9_]+', 'label': 'Project name', 'tooltip': ''},
                     'label_short': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Short label', 'tooltip': ''},
                     'label_long': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Long label', 'tooltip': ''},
                     'scientist': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Scientist', 'tooltip': ''},
                     'external_scientist': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'External scientist', 'tooltip': ''},
                     'sra_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'SRA ref', 'tooltip': ''}},
                    {'sample_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Sample ID', 'tooltip': ''},
                     'sample_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Sample', 'tooltip': ''},
                     'project_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Project', 'tooltip': ''},
                     'label_short': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Short label', 'tooltip': ''},
                     'label_long': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Long label', 'tooltip': ''},
                     'species': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Species', 'tooltip': ''},
                     'strain_maternal': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Maternal strain', 'tooltip': ''},
                     'strain_paternal': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Paternal strain', 'tooltip': ''},
                     'genotype': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Genotype', 'tooltip': ''},
                     'ploidy': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Ploidy', 'tooltip': ''},
                     'age_hpf': {'search_type': 'equal_number', 'gui_type': 'select_option_none', 'required': False, 'label': 'Age (hpf)', 'tooltip': ''},
                     'stage': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Stage', 'tooltip': ''},
                     'tissue': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Tissue', 'tooltip': ''},
                     'condition': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Condition', 'tooltip': ''},
                     'treatment': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Treatment', 'tooltip': ''},
                     'selection': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Selection', 'tooltip': ''},
                     'molecule': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Molecule', 'tooltip': ''},
                     'library_protocol': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Library protocol', 'tooltip': ''},
                     'adapter_5p': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Adapter 5\'', 'tooltip': ''},
                     'adapter_3p': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Adapter 3\'', 'tooltip': ''},
                     'track_priority': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'pattern': '[0-9]+', 'label': 'Track priority', 'tooltip': ''},
                     'track_color': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Track color', 'tooltip': ''},
                     'sra_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'SRA ref', 'tooltip': ''},
                     'notes': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Notes', 'tooltip': ''}},
                    {'replicate_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Replicate ID', 'tooltip': ''},
                     'replicate_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Replicate', 'tooltip': ''},
                     'replicate_order': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'pattern': '[0-9]+', 'label': 'Replicate order', 'tooltip': ''},
                     'sample_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Sample', 'tooltip': ''},
                     'label_short': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Label', 'tooltip': ''},
                     'label_long': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Long label', 'tooltip': ''},
                     'sra_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'SRA ref', 'tooltip': ''},
                     'publication_ref': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Publication ref', 'tooltip': ''},
                     'notes': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Notes', 'tooltip': ''}},
                    {'run_id':  {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Run ID', 'tooltip': ''},
                     'run_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Run', 'tooltip': ''},
                     'run_order': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'pattern': '[0-9]+', 'label': 'Run order', 'tooltip': ''},
                     'replicate_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Replicate ref', 'tooltip': ''},
                     'tube_label': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Tube label', 'tooltip': ''},
                     'barcode': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Barcode', 'tooltip': ''},
                     'second_barcode': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'pattern': '[A-Z]+', 'label': 'Second barcode', 'tooltip': ''},
                     'request_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Request', 'tooltip': ''},
                     'request_date': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Request date', 'tooltip': ''},
                     'failed': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Failed', 'tooltip': ''},
                     'flowcell': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Flowcell', 'tooltip': ''},
                     'platform': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Platform', 'tooltip': ''},
                     'quality_scores': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Quality scores', 'tooltip': ''},
                     'directional': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Directional', 'tooltip': ''},
                     'paired': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Paired', 'tooltip': ''},
                     'r1_strand': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Read1 strand', 'tooltip': ''},
                     'spots': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'pattern': '[0-9]+', 'label': 'Spots', 'tooltip': 'Number of spots'},
                     'max_read_length': {'search_type': 'equal_number', 'gui_type': 'text', 'required': False, 'pattern': '[0-9]+', 'label': 'Max read length', 'tooltip': ''},
                     'sra_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'SRA ref', 'tooltip': ''},
                     'notes': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Notes', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    column_titles = []
    column_titles_json = json.dumps(column_titles)

    default_search_criterions = []
    default_search_criterions_json = json.dumps(default_search_criterions)

    default_sort_criterions = []
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    default_limits = [['All', 'ALL', False], ['10', '10', False], ['100', '100', False], ['500', '500', True]]
    default_limits_json = json.dumps(default_limits)

    columns = []
    columns_json = json.dumps(columns)

    form = []
    form_json = json.dumps(form)

    board_path = 'js/table.js'
    board_class = 'Table'
    form_path = 'js/tableform.js'
    form_class = 'TableForm'

@routes.view('/seq')
class SeqDefaultHandler(generic.GenericDefaultHandler, SeqBaseHandler):
    default_url = 'seq/project'

@routes.view('/seq/project')
class SeqProjectHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_table.jinja'
    board_path = 'js/seq/board.js'
    board_class = 'SeqProjectTable'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'sra_ref', 'DESC', 'SRA ref'], [0, 'project_ref', 'DESC', 'Project']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'project_ref'}, {'name':'project_name'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'scientist'}, {'name':'external_scientist'}, {'name':'sra_ref'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.project {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/seq/sample')
class SeqSampleHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [1]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[1, 'sample_ref', 'ASC', 'Sample']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[], [{'name':'sample_ref'}, {'name':'project_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'molecule'}, {'name':'genotype'}, {'name':'age_hpf'}, {'name':'stage'}, {'name':'condition'}, {'name':'treatment'}, {'name':'species'}, {'name':'strain_maternal'}, {'name':'strain_paternal'}, {'name':'ploidy'}, {'name':'tissue'}, {'name':'selection'}, {'name':'library_protocol'}, {'name':'adapter_5p'}, {'name':'adapter_3p'}, {'name':'track_priority'}, {'name':'track_color'}, {'name':'sra_ref'}, {'name':'notes'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.sample {{search_query_level1}} {{sort_query_level1}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [['', ' WHERE ']]

@routes.view('/seq/replicate')
class SeqReplicateHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [2]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[2, 'replicate_ref', 'ASC', 'Replicate']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[], [], [{'name':'replicate_ref'}, {'name':'replicate_order'}, {'name':'sample_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'sra_ref'}, {'name':'publication_ref'}, {'name':'notes'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.replicate {{search_query_level2}} {{sort_query_level2}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [['', '', ' WHERE ']]

@routes.view('/seq/run')
class SeqRunHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [3]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[3, 'run_ref', 'ASC', 'Run']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[], [], [], [{'name':'run_ref'}, {'name':'run_order'}, {'name':'replicate_ref'}, {'name':'tube_label'}, {'name':'barcode'}, {'name':'second_barcode'}, {'name':'request_ref'}, {'name':'request_date'}, {'name':'failed'}, {'name':'flowcell'}, {'name':'platform'}, {'name':'quality_scores'}, {'name':'directional'}, {'name':'paired'}, {'name':'r1_strand'}, {'name':'spots'}, {'name':'max_read_length'}, {'name':'sra_ref'}, {'name':'notes'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.run {{search_query_level3}} {{sort_query_level3}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [['', '', '', ' WHERE ']]

@routes.view('/seq/tree')
class SeqTreeHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_tree.jinja'
    board_path = 'js/treeblock.js'
    board_class = 'TreeBlock'

    levels = [0, 1, 2, 3]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'external_scientist', 'DESC', 'Ext. Scientist'], [0, 'project_ref', 'DESC', 'Project'], [1, 'sample_ref', 'ASC', 'Sample'], [2, 'replicate_order', 'ASC', 'Replicate']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)
    default_limits = [['All', 'ALL', False], ['10', '10', True], ['100', '100', False], ['500', '500', False]]
    default_limits_json = json.dumps(default_limits)

    columns = [[{'name':'project_ref'}, {'name':'project_name'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'scientist'}, {'name':'external_scientist'}, {'name':'sra_ref'}],
               [{'name':'sample_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'molecule'}, {'name':'genotype'}, {'name':'age_hpf'}, {'name':'stage'}, {'name':'condition'}, {'name':'treatment'}, {'name':'species'}, {'name':'strain_maternal'}, {'name':'strain_paternal'}, {'name':'ploidy'}, {'name':'tissue'}, {'name':'selection'}, {'name':'library_protocol'}, {'name':'adapter_5p'}, {'name':'adapter_3p'}, {'name':'track_priority'}, {'name':'track_color'}, {'name':'sra_ref'}, {'name':'notes'}],
               [{'name':'replicate_ref'}, {'name':'replicate_order'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'sra_ref'}, {'name':'publication_ref'}, {'name':'notes'}],
               [{'name':'run_ref'}, {'name':'run_order'}, {'name':'tube_label'}, {'name':'barcode'}, {'name':'second_barcode'}, {'name':'request_ref'}, {'name':'request_date'}, {'name':'failed'}, {'name':'flowcell'}, {'name':'platform'}, {'name':'quality_scores'}, {'name':'directional'}, {'name':'paired'}, {'name':'r1_strand'}, {'name':'spots'}, {'name':'max_read_length'}, {'name':'sra_ref'}, {'name':'notes'}]]
    columns_json = json.dumps(columns)
    column_titles = [['project_ref', 'label_short'], ['sample_ref', 'label_short'], ['replicate_ref', 'label_short'], ['run_ref']]
    column_titles_json = json.dumps(column_titles)

    queries = [f"""SELECT COALESCE(array_to_json(array_agg(row_to_json(p))), '[]')
                    FROM (
                        SELECT * FROM (
                            SELECT p.*, (
                                SELECT array_to_json(array_agg(row_to_json(s)))
                                FROM (
                                    SELECT s.*, (
                                        SELECT array_to_json(array_agg(row_to_json(n)))
                                        FROM (
                                            SELECT n.*, (
                                                SELECT array_to_json(array_agg(row_to_json(r)))
                                                FROM (
                                                    SELECT r.*
                                                    FROM {SeqBaseHandler.schema}.run AS r
                                                    WHERE replicate_ref = n.replicate_ref {{search_query_level3}} {{sort_query_level3}}
                                                ) r
                                            ) AS children
                                            FROM {SeqBaseHandler.schema}.replicate AS n
                                            WHERE sample_ref = s.sample_ref {{search_query_level2}} {{sort_query_level2}}
                                        ) n {{not_null_children_level2}}
                                    ) AS children
                                    FROM {SeqBaseHandler.schema}.sample AS s
                                    WHERE project_ref = p.project_ref {{search_query_level1}} {{sort_query_level1}}
                                    ) s {{not_null_children_level1}}
                                ) AS children
                            FROM {SeqBaseHandler.schema}.project AS p
                            {{search_query_level0}} {{sort_query_level0}}
                            ) pa {{not_null_children_level0}} LIMIT {{limit}}
                        ) p;"""]
    queries_search_prefixes = [[' WHERE ', ' AND ', ' AND ', ' AND ']]

@routes.view('/seq/project/new')
class SeqProjectNewHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [0]
    levels_json = json.dumps(levels)

    form = [{'label':'Project', 'columns':[{'name':'project_ref'}, {'name':'project_name'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'scientist'}, {'name':'external_scientist'}, {'name':'sra_ref'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {SeqBaseHandler.schema}.project ({{columns}}) VALUES ({{query_values}}) RETURNING project_id;"]

@routes.view('/seq/sample/new')
class SeqSampleNewHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [1]
    levels_json = json.dumps(levels)

    form = [{'label':'Sample', 'columns':[{'name':'sample_ref'}, {'name':'project_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'species'}, {'name':'strain_maternal'}, {'name':'strain_paternal'}, {'name':'genotype'}, {'name':'ploidy'}, {'name':'age_hpf'}, {'name':'stage'}, {'name':'tissue'}, {'name':'condition'}, {'name':'treatment'}, {'name':'selection'}, {'name':'molecule'}, {'name':'library_protocol'}, {'name':'adapter_5p'}, {'name':'adapter_3p'}, {'name':'track_priority'}, {'name':'track_color'}, {'name':'sra_ref'}, {'name':'notes'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {SeqBaseHandler.schema}.sample ({{columns}}) VALUES ({{query_values}}) RETURNING sample_id;"]

@routes.view('/seq/replicate/new')
class SeqReplicateNewHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [2]
    levels_json = json.dumps(levels)

    form = [{'label':'Replicate', 'columns':[{'name':'replicate_ref'}, {'name':'replicate_order'}, {'name':'sample_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'sra_ref'}, {'name':'publication_ref'}, {'name':'notes'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {SeqBaseHandler.schema}.replicate ({{columns}}) VALUES ({{query_values}}) RETURNING replicate_id;"]

@routes.view('/seq/run/new')
class SeqRunNewHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [3]
    levels_json = json.dumps(levels)

    form = [{'label':'Run', 'columns':[{'name':'run_ref'}, {'name':'run_order'}, {'name':'replicate_ref'}, {'name':'tube_label'}, {'name':'barcode'}, {'name':'second_barcode'}, {'name':'request_ref'}, {'name':'request_date'}, {'name':'failed'}, {'name':'flowcell'}, {'name':'platform'}, {'name':'quality_scores'}, {'name':'directional'}, {'name':'paired'}, {'name':'r1_strand'}, {'name':'spots'}, {'name':'max_read_length'}, {'name':'sra_ref'}, {'name':'notes'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {SeqBaseHandler.schema}.run ({{columns}}) VALUES ({{query_values}}) RETURNING run_id;"]

@routes.view('/seq/project/edit/{record_id}')
class SeqProjectEditHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [0]
    levels_json = json.dumps(levels)

    form = SeqProjectNewHandler.form
    form_json = SeqProjectNewHandler.form_json

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.project SET {{update_query}} WHERE project_id={{record_id}};"]

@routes.view('/seq/sample/edit/{record_id}')
class SeqSampleEditHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [1]
    levels_json = json.dumps(levels)

    form = SeqSampleNewHandler.form
    form_json = SeqSampleNewHandler.form_json

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.sample SET {{update_query}} WHERE sample_id={{record_id}};"]

@routes.view('/seq/replicate/edit/{record_id}')
class SeqReplicateEditHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [2]
    levels_json = json.dumps(levels)

    form = SeqReplicateNewHandler.form
    form_json = SeqReplicateNewHandler.form_json

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.replicate SET {{update_query}} WHERE replicate_id={{record_id}};"]

@routes.view('/seq/run/edit/{record_id}')
class SeqRunEditHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [3]
    levels_json = json.dumps(levels)

    form = SeqRunNewHandler.form
    form_json = SeqRunNewHandler.form_json

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.run SET {{update_query}} WHERE run_id={{record_id}};"]

@routes.view('/seq/project/get/{record_id}')
class SeqProjectGetHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.project WHERE project_id={{record_id}}) r;"]

@routes.view('/seq/sample/get/{record_id}')
class SeqSampleGetHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.sample WHERE sample_id={{record_id}}) r;"]

@routes.view('/seq/replicate/get/{record_id}')
class SeqReplicateGetHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.replicate WHERE replicate_id={{record_id}}) r;"]

@routes.view('/seq/run/get/{record_id}')
class SeqRunGetHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.run WHERE run_id={{record_id}}) r;"]

@routes.view('/seq/project/get-ref/{record_id}')
class SeqProjectGetRefHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.project WHERE project_ref='{{record_id}}') r;"]

@routes.view('/seq/sample/get-ref/{record_id}')
class SeqSampleGetRefHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.sample WHERE sample_ref='{{record_id}}') r;"]

@routes.view('/seq/replicate/get-ref/{record_id}')
class SeqReplicateGetRefHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.replicate WHERE replicate_ref='{{record_id}}') r;"]

@routes.view('/seq/run/get-ref/{record_id}')
class SeqRunGetRefHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.run WHERE run_ref='{{record_id}}') r;"]

@routes.view('/seq/project/remove/{record_id}')
class SeqProjectRemoveHandler(generic.GenericRemoveHandler, SeqBaseHandler):
    queries = [f"DELETE FROM {SeqBaseHandler.schema}.project WHERE project_id={{record_id}};"]

@routes.view('/seq/sample/remove/{record_id}')
class SeqSampleRemoveHandler(generic.GenericRemoveHandler, SeqBaseHandler):
    queries = [f"DELETE FROM {SeqBaseHandler.schema}.sample WHERE sample_id={{record_id}};"]

@routes.view('/seq/replicate/remove/{record_id}')
class SeqReplicateRemoveHandler(generic.GenericRemoveHandler, SeqBaseHandler):
    queries = [f"DELETE FROM {SeqBaseHandler.schema}.replicate WHERE replicate_id={{record_id}};"]

@routes.view('/seq/run/remove/{record_id}')
class SeqRunRemoveHandler(generic.GenericRemoveHandler, SeqBaseHandler):
    queries = [f"DELETE FROM {SeqBaseHandler.schema}.run WHERE run_id={{record_id}};"]

@routes.view('/seq/assign')
class SeqAssignHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'seq_form.jinja'
    form_path = 'js/seq/assignform.js'
    form_class = 'AssignForm'
    prefix = 'AG'

    levels = [0, 1, 2, 3]
    levels_json = json.dumps(levels)

    columns = [[], [], [], [{'name':'tube_label'}, {'name':'run_ref'}, {'name':'barcode'}, {'name':'flowcell'}]]
    columns_json = json.dumps(columns)

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.run SET replicate_ref=$1, run_order=(SELECT COUNT(*)+1 FROM {SeqBaseHandler.schema}.run WHERE replicate_ref=$1::VARCHAR) WHERE run_ref=$2;",
                      f"UPDATE {SeqBaseHandler.schema}.replicate SET sample_ref=$1, replicate_order=(SELECT COUNT(*)+1 FROM {SeqBaseHandler.schema}.replicate WHERE sample_ref=$1::VARCHAR) WHERE replicate_ref=$2;",
                      f"UPDATE {SeqBaseHandler.schema}.sample SET project_ref=$1 WHERE sample_ref=$2;"]

    def get_next_ref(self, prefix, current_ref):
        if current_ref is None:
            n = 1
        else:
            n = int(current_ref[len(prefix):]) + 1
        if n < 999999:
            return f'{prefix}{n:0>6}'
        else:
            return f'{prefix}{n}'

    async def post(self):
        # Get data
        data = await self.request.json()
        self.logger.debug(f'POST in: {data}')
        # Prefix
        if data['prefix'] is None:
            prefix = self.prefix
        else:
            prefix = data['prefix']

        # Set unused levels (upstream of append) to None
        for l in data['query']:
            state = True
            for c in l:
                if state is False:
                    c[0] = None
                if state and c[0] == 'append':
                    state = False

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(f"LOCK TABLE {SeqBaseHandler.schema}.run IN EXCLUSIVE MODE;")
                    await con.execute(f"LOCK TABLE {SeqBaseHandler.schema}.replicate IN EXCLUSIVE MODE;")
                    await con.execute(f"LOCK TABLE {SeqBaseHandler.schema}.sample IN EXCLUSIVE MODE;")
                    await con.execute(f"LOCK TABLE {SeqBaseHandler.schema}.project IN EXCLUSIVE MODE;")

                    new_refs = [{} for l in range(len(self.level_infos))]
                    for qline in data['query']:

                        # ----------
                        # Level: Run
                        ilevel = 0
                        op, name = qline[ilevel]
                        # Run are always new
                        new_run = True
                        if op == 'new':
                            max_ref = await con.fetchval(f"SELECT MAX(run_ref) FROM {SeqBaseHandler.schema}.run WHERE run_ref LIKE CONCAT('{prefix}', '%');")
                            current_run_ref = self.get_next_ref(prefix+'R', max_ref)
                            await con.execute(f"UPDATE {SeqBaseHandler.schema}.run SET run_ref=$1, run_order=1 WHERE run_ref=$2;", current_run_ref, name)
                            key = ''.join([str(qline[i][1]) for i in range(ilevel, max(self.levels)+1) if qline[i][0] is not None])
                            new_refs[ilevel][key] = {'ref':current_run_ref, 'name':name}
                        elif op == 'keep':
                            current_run_ref = name

                        # ----------------
                        # Level: Replicate
                        ilevel = 1
                        op, name = qline[ilevel]
                        new_replicate = False
                        if op == 'new':
                            key = ''.join([str(qline[i][1]) for i in range(ilevel, max(self.levels)+1) if qline[i][0] is not None])
                            if key in new_refs[ilevel]:
                                current_replicate_ref = new_refs[ilevel][key]['ref']
                            else:
                                max_ref = await con.fetchval(f"SELECT MAX(replicate_ref) FROM {SeqBaseHandler.schema}.replicate WHERE replicate_ref LIKE CONCAT('{prefix}', '%');")
                                current_replicate_ref = self.get_next_ref(prefix+'N', max_ref)
                                serial = await con.fetchval(f"INSERT INTO {SeqBaseHandler.schema}.replicate (replicate_ref,replicate_order,label_short) VALUES ($1, 1, $2) RETURNING replicate_id;", current_replicate_ref, name)
                                new_refs[ilevel][key] = {'ref':current_replicate_ref, 'name':name, 'serial':serial}
                                new_replicate = True
                        elif op == 'append':
                            current_replicate_ref = name
                        # Update level upstream: Run
                        if new_run:
                            await con.execute(self.update_queries[ilevel-1], current_replicate_ref, current_run_ref)

                        # -------------
                        # Level: Sample
                        ilevel = 2
                        op, name = qline[ilevel]
                        new_sample = False
                        if op == 'new':
                            key = ''.join([str(qline[i][1]) for i in range(ilevel, max(self.levels)+1) if qline[i][0] is not None])
                            if key in new_refs[ilevel]:
                                current_sample_ref = new_refs[ilevel][key]['ref']
                            else:
                                max_ref = await con.fetchval(f"SELECT MAX(sample_ref) FROM {SeqBaseHandler.schema}.sample WHERE sample_ref LIKE CONCAT('{prefix}', '%');")
                                current_sample_ref = self.get_next_ref(prefix+'S', max_ref)
                                serial = await con.fetchval(f"INSERT INTO {SeqBaseHandler.schema}.sample (sample_ref,label_short) VALUES ($1, $2) RETURNING sample_id;", current_sample_ref, name)
                                new_refs[ilevel][key] = {'ref':current_sample_ref, 'name':name, 'serial':serial}
                                new_sample = True
                        elif op == 'append':
                            current_sample_ref = name
                        # Update level upstream: Replicate
                        if new_replicate:
                            await con.execute(self.update_queries[ilevel-1], current_sample_ref, current_replicate_ref)

                        # --------------
                        # Level: Project
                        ilevel = 3
                        op, name = qline[ilevel]
                        if op == 'new':
                            key = ''.join([str(qline[i][1]) for i in range(ilevel, max(self.levels)+1) if qline[i][0] is not None])
                            if key in new_refs[ilevel]:
                                current_project_ref = new_refs[ilevel][key]['ref']
                            else:
                                max_ref = await con.fetchval(f"SELECT MAX(project_ref) FROM {SeqBaseHandler.schema}.project WHERE project_ref LIKE CONCAT('{prefix}', '%');")
                                current_project_ref = self.get_next_ref(prefix+'P', max_ref)
                                serial = await con.fetchval(f"INSERT INTO {SeqBaseHandler.schema}.project (project_ref,label_short) VALUES ($1, $2) RETURNING project_id;", current_project_ref, name)
                                new_refs[ilevel][key] = {'ref':current_project_ref, 'name':name, 'serial':serial}
                        elif op == 'append':
                            current_project_ref = name
                        # Update level upstream: Sample
                        if new_sample:
                            await con.execute(self.update_queries[ilevel-1], current_project_ref, current_sample_ref)

                    self.logger.debug(f'POST new_refs: {new_refs}')
                    return aiohttp.web.Response(body=json.dumps({'refs': new_refs}), content_type='application/json', headers={'Query-status': 'OK'})

        except (asyncpg.PostgresWarning, asyncpg.PostgresError) as error:
            self.logger.error(error)
            return aiohttp.web.Response(text=str(error), headers={'Query-status': str(error).replace('\n', ' ')})

@routes.view('/seq/project/fulledit/{record_id}')
class SeqFullProjectHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'seq_form.jinja'
    form_path = 'js/seq/seqform.js'
    form_class = 'SeqForm'

    columns = [[{'name':'project_ref'}, {'name':'label_short'}],
               [{'name':'sample_ref'}, {'name':'project_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'species'}, {'name':'strain_maternal'}, {'name':'strain_paternal'}, {'name':'genotype'}, {'name':'ploidy'}, {'name':'age_hpf'}, {'name':'stage'}, {'name':'tissue'}, {'name':'condition'}, {'name':'treatment'}, {'name':'selection'}, {'name':'molecule'}, {'name':'library_protocol'}, {'name':'adapter_5p'}, {'name':'adapter_3p'}, {'name':'track_priority'}, {'name':'track_color'}, {'name':'sra_ref'}, {'name':'notes'}],
               [{'name':'replicate_ref'}, {'name':'replicate_order'}, {'name':'sample_ref'}, {'name':'label_short'}, {'name':'label_long'}, {'name':'sra_ref'}, {'name':'notes'}],
               [{'name':'run_ref'}, {'name':'run_order'}, {'name':'replicate_ref'}, {'name':'tube_label'}, {'name':'barcode'}, {'name':'second_barcode'}, {'name':'request_ref'}, {'name':'request_date'}, {'name':'failed'}, {'name':'flowcell'}, {'name':'platform'}, {'name':'quality_scores'}, {'name':'directional'}, {'name':'paired'}, {'name':'r1_strand'}, {'name':'spots'}, {'name':'max_read_length'}, {'name':'sra_ref'}, {'name':'notes'}]]
    columns_json = json.dumps(columns)

    update_queries = [SeqProjectEditHandler.update_queries, SeqSampleEditHandler.update_queries, SeqReplicateEditHandler.update_queries, SeqRunEditHandler.update_queries]
    
    def get_queries(self, data, record_id):
        queries = []
        for level in range(len(data)):
            for idata in range(len(data[level])):
                columns = []
                values = []
                i = 1
                for k, v in data[level][idata].items():
                    if k != self.level_infos[level]['column_id']:
                        columns.append(f'{k}=${i}')
                        values.append(v)
                        i += 1
                for query in self.update_queries[level]:
                    queries.append([query.format(update_query=','.join(columns), record_id=data[level][idata][self.level_infos[level]['column_id']]), values])
        return queries

@routes.view('/seq/option')
class SeqOptionHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'seq/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.option {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/seq/option/new')
class SeqOptionNewHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = SeqOptionHandler.level_infos
    level_infos_json = SeqOptionHandler.level_infos_json

    column_infos = SeqOptionHandler.column_infos
    column_infos_json = SeqOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {SeqBaseHandler.schema}.option ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/seq/option/edit/{record_id}')
class SeqOptionEditHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = SeqOptionHandler.level_infos
    level_infos_json = SeqOptionHandler.level_infos_json

    column_infos = SeqOptionHandler.column_infos
    column_infos_json = SeqOptionHandler.column_infos_json

    form = SeqOptionNewHandler.form
    form_json = SeqOptionNewHandler.form_json

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.option SET {{update_query}} WHERE option_id={{record_id}};"]

@routes.view('/seq/option/get/{record_id}')
class SeqOptionGetHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.option WHERE option_id={{record_id}}) r;"]

@routes.view('/seq/option/remove/{record_id}')
class SeqOptionRemoveHandler(generic.GenericRemoveHandler, SeqBaseHandler):
    queries = [f"DELETE FROM {SeqBaseHandler.schema}.option WHERE option_id={{record_id}};"]

@routes.view('/seq/publication')
class SeqPublicationHandler(generic.GenericHandler, SeqBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Publication', 'url': 'seq/publication', 'column_id': 'publication_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'publication_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Publication ID', 'tooltip': ''},
                     'publication_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Publication', 'tooltip': ''},
                     'title': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Title', 'tooltip': ''},
                     'publication_date': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'label': 'Publication date', 'tooltip': ''},
                     'pubmed_id': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Pubmed ID', 'tooltip': ''},
                     'sra_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'SRA ref', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'publication_ref', 'ASC', 'Publication']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'publication_ref'}, {'name':'title'}, {'name':'publication_date'}, {'name':'pubmed_id'}, {'name':'sra_ref'}]]
    columns_json = json.dumps(columns)

    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.publication {{search_query_level0}} {{sort_query_level0}} LIMIT {{limit}}) r;"]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/seq/publication/new')
class SeqPublicationNewHandler(generic.GenericQueriesHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = SeqPublicationHandler.level_infos
    level_infos_json = SeqPublicationHandler.level_infos_json

    column_infos = SeqPublicationHandler.column_infos
    column_infos_json = SeqPublicationHandler.column_infos_json

    form = [{'label':'Publication', 'columns':[{'name':'publication_ref'}, {'name':'title'}, {'name':'publication_date'}, {'name':'pubmed_id'}, {'name':'sra_ref'}]}]
    form_json = json.dumps(form)

    insert_queries = [f"INSERT INTO {SeqBaseHandler.schema}.publication ({{columns}}) VALUES ({{query_values}});"]

@routes.view('/seq/publication/edit/{record_id}')
class SeqPublicationEditHandler(generic.GenericRecordHandler, SeqBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = SeqPublicationHandler.level_infos
    level_infos_json = SeqPublicationHandler.level_infos_json

    column_infos = SeqPublicationHandler.column_infos
    column_infos_json = SeqPublicationHandler.column_infos_json

    form = SeqPublicationNewHandler.form
    form_json = SeqPublicationNewHandler.form_json

    update_queries = [f"UPDATE {SeqBaseHandler.schema}.publication SET {{update_query}} WHERE publication_id={{record_id}};"]

@routes.view('/seq/publication/get/{record_id}')
class SeqPublicationGetHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.publication WHERE publication_id={{record_id}}) r;"]

@routes.view('/seq/publication/remove/{record_id}')
class SeqPublicationRemoveHandler(generic.GenericRemoveHandler, SeqBaseHandler):
    queries = [f"DELETE FROM {SeqBaseHandler.schema}.publication WHERE publication_id={{record_id}};"]

@routes.view('/seq/publication/get-ref/{record_id}')
class SeqPublicationGetRefHandler(generic.GenericGetHandler, SeqBaseHandler):
    queries = [f"SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM {SeqBaseHandler.schema}.publication WHERE publication_ref='{{record_id}}') r;"]
