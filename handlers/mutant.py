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

class MutantBaseHandler(base.BaseHandler):
    name = 'mutant'
    schema = 'mutant'

    levels = [0]
    levels_json = json.dumps(levels)

    level_infos = [{'label': 'Gene', 'url': 'mutant/gene', 'column_id': 'gene_id'},
                   {'label': 'Allele', 'url': 'mutant/allele', 'column_id': 'allele_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'gene_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Gene ID', 'tooltip': ''},
                     'date_insert': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Insert date', 'tooltip': ''},
                     'last_modif': {'search_type': 'equal_date', 'gui_type': 'text', 'required': False, 'pattern': '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]', 'label': 'Last modif', 'tooltip': ''},
                     'gene_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Gene', 'tooltip': 'Gene name(s) (comma separated)'},
                     'mutant_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Mutant', 'tooltip': 'Mutant name'},
                     'ensembl_id': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Ensembl', 'tooltip': 'ENSEMBL Gene IDs (comma separated)'},
                     'author_initials': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Author', 'tooltip': 'Initials of author(s) (comma separated)'},
                     'maintainer_initials': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Maintainer', 'tooltip': 'Initials of maintainer(s) (comma separated)'},
                     'terminated': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Terminated', 'tooltip': 'All mutant fish terminated?'},
                     'note': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Note', 'tooltip': '', 'class': 'seq-text', 'maxlength': '10000'},
                     'interest': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Interest', 'tooltip': 'Interest in gene?'},
                     'injected': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Injected', 'tooltip': ''},
                     'f1_embryo': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'F1 emb', 'tooltip': 'Embryos of positive F0 raised?'},
                     'f1_hetero': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'F1 het', 'tooltip': 'Positive F1 heterozygous adults genotyped?'},
                     'f2_homo': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'F2 hom', 'tooltip': 'Positive F2 homozygous adults genotyped?'},
                     'phenotype_zygotic': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Phen. Z', 'tooltip': ''},
                     'phenotype_mz': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Phen. MZ', 'tooltip': ''},
                     'target_strategy': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Strategy', 'tooltip': ''},
                     'edit_enzyme': {'search_type': 'ilike', 'gui_type': 'select_option_none', 'required': False, 'label': 'Edit enzyme', 'tooltip': ''},
                     'grna_seq_tested': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'gRNA tested', 'tooltip': 'Tested gRNA(s) with oligo ID (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'grna_seq_working': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'gRNA working', 'tooltip': 'Working gRNA(s) with oligo ID (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'target_seq': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Target seq', 'tooltip': 'Genomic target sequences with PAM (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'template_oligo': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Template oligo', 'tooltip': 'Template ssOligos with oligo ID (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'template_plasmid': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'Template plasmid', 'tooltip': 'ID of template plasmids (comma separated)'},
                     'oligo_f0_fw': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Oligo F0 fw', 'tooltip': 'F0 genotyping oligos forward with oligo ID (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'oligo_f0_rv': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Oligo F0 rv', 'tooltip': 'F0 genotyping oligos reverse with oligo ID (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'genomic_wt_seq': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Genomic WT seq', 'tooltip': 'Genomic WT sequence amplified with oligos (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'zfin_ref': {'search_type': 'ilike', 'gui_type': 'text', 'required': False, 'label': 'ZFIN ref', 'tooltip': 'Reference (ID) of fish line at ZFIN'}},
                    {'allele_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Allele ID', 'tooltip': ''},
                     'gene_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Gene ID', 'tooltip': ''},
                     'name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Name', 'tooltip': ''},
                     'seq': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Seq', 'tooltip': 'Allele sequence amplified with oligos (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'genotyping_oligo': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Genotyping oligo', 'tooltip': 'Genotyping oligos with ID (FASTA)', 'class': 'seq-text', 'maxlength': '10000'},
                     'genotyping_strategy': {'search_type': 'ilike', 'gui_type': 'textarea', 'required': False, 'label': 'Genotyping strategy', 'tooltip': 'Genotyping strategy (PCR Ta, PCR cycles, other)', 'class': 'seq-text', 'maxlength': '10000'},
                     'commercial': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Commercial', 'tooltip': ''},
                     'terminated': {'search_type': 'equal_bool', 'gui_type': 'select_bool_none', 'required': False, 'label': 'Terminated', 'tooltip': ''}}]
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

@routes.view('/mutant')
class MutantDefaultHandler(generic.GenericDefaultHandler, MutantBaseHandler):
    default_url = 'mutant/gene'

@routes.view('/mutant/gene')
class MutantGeneHandler(generic.GenericHandler, MutantBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [0]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'gene_name', 'ASC', 'Gene']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'gene_name'}, {'name':'mutant_name'}, {'name':'ensembl_id'}, {'name':'author_initials'}, {'name':'maintainer_initials'}, {'name':'interest'}, {'name':'terminated'}, {'name':'f1_embryo'}, {'name':'f1_hetero'}, {'name':'f2_homo'}, {'name':'phenotype_zygotic'}, {'name':'phenotype_mz'}, {'name':'target_strategy'}, {'name':'zfin_ref'}]]
    columns_json = json.dumps(columns)

    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.gene {search_query_level0} {sort_query_level0} LIMIT {limit}) r;"%MutantBaseHandler.schema]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/mutant/allele')
class MutantAlleleHandler(generic.GenericHandler, MutantBaseHandler):
    tpl = 'generic_table.jinja'

    levels = [1]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[1, 'name', 'ASC', 'Name']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[], [{'name':'name'}, {'name':'genotyping_strategy'}, {'name':'commercial'}, {'name':'terminated'}]]
    columns_json = json.dumps(columns)

    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.allele {search_query_level0} {sort_query_level0} LIMIT {limit}) r;"%MutantBaseHandler.schema]
    queries_search_prefixes = [['', ' WHERE ']]

@routes.view('/mutant/tree')
class MutantTreeHandler(generic.GenericHandler, MutantBaseHandler):
    tpl = 'generic_tree.jinja'
    board_path = 'js/mutant/board.js'
    board_class = 'MutantTreeBlock'

    levels = [0, 1]
    levels_json = json.dumps(levels)

    default_sort_criterions = [[0, 'gene_name', 'ASC', 'Gene'], [1, 'name', 'ASC', 'Name']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)
    default_limits = [['All', 'ALL', False], ['10', '10', False], ['100', '100', True], ['500', '500', False]]
    default_limits_json = json.dumps(default_limits)

    columns = [[{'name':'gene_name'}, {'name':'mutant_name'}, {'name':'date_insert'}, {'name':'last_modif'}, {'name':'ensembl_id'}, {'name':'author_initials'}, {'name':'maintainer_initials'}, {'name':'zfin_ref'}, {'name':'terminated'}, {'name':'note'}, {'name':'interest'}, {'name':'injected'}, {'name':'f1_embryo'}, {'name':'f1_hetero'}, {'name':'f2_homo'}, {'name':'phenotype_zygotic'}, {'name':'phenotype_mz'}, {'name':'target_strategy'}, {'name':'edit_enzyme'}, {'name':'grna_seq_tested'}, {'name':'grna_seq_working'}, {'name':'target_seq'}, {'name':'template_oligo'}, {'name':'template_plasmid'}, {'name':'oligo_f0_fw'}, {'name':'oligo_f0_rv'}, {'name':'genomic_wt_seq'}],
               [{'name':'name'}, {'name':'seq'}, {'name':'genotyping_oligo'}, {'name':'genotyping_strategy'}, {'name':'commercial'}, {'name':'terminated'}]]
    columns_json = json.dumps(columns)
    column_titles = [['gene_name'], ['name']]
    column_titles_json = json.dumps(column_titles)

    queries = ["""SELECT COALESCE(array_to_json(array_agg(row_to_json(g))), '[]')
                    FROM (
                        SELECT * FROM (
                            SELECT g.*, (
                                SELECT array_to_json(array_agg(row_to_json(a)))
                                FROM (
                                    SELECT a.*
                                    FROM %s.allele AS a
                                    WHERE gene_id = g.gene_id {search_query_level1} {sort_query_level1}
                                ) a
                            ) AS children
                        FROM %s.gene AS g
                        {search_query_level0} {sort_query_level0}
                        ) ga {not_null_children_level0} LIMIT {limit}
                    ) g;"""%(MutantBaseHandler.schema, MutantBaseHandler.schema)]
    queries_search_prefixes = [[' WHERE ', ' AND ']]

@routes.view('/mutant/gene/new')
class MutantGeneNewHandler(generic.GenericQueriesHandler, MutantBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [0]
    levels_json = json.dumps(levels)
    
    form = [{'label':'Gene', 'columns':[{'name':'gene_name'}, {'name':'mutant_name'}, {'name':'ensembl_id'}, {'name':'author_initials'}, {'name':'maintainer_initials'}, {'name':'zfin_ref'}, {'name':'note'}]},
            {'label':'Status', 'columns':[{'name':'terminated'}, {'name':'interest'}, {'name':'injected'}, {'name':'f1_embryo'}, {'name':'f1_hetero'}, {'name':'f2_homo'}, {'name':'phenotype_zygotic'}, {'name':'phenotype_mz'}]},
            {'label':'Targeting', 'columns':[{'name':'target_strategy'}, {'name':'edit_enzyme'}, {'name':'grna_seq_tested'}, {'name':'grna_seq_working'}, {'name':'target_seq'}, {'name':'template_oligo'}, {'name':'template_plasmid'}]},
            {'label':'Genotyping', 'columns':[{'name':'oligo_f0_fw'}, {'name':'oligo_f0_rv'}, {'name':'genomic_wt_seq'}]}]
    form_json = json.dumps(form)

    insert_queries = ["INSERT INTO %s.gene ({columns}) VALUES ({query_values});"%MutantBaseHandler.schema]

@routes.view('/mutant/gene/edit/{record_id}')
class MutantGeneEditHandler(generic.GenericRecordHandler, MutantBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [0]
    levels_json = json.dumps(levels)

    form = MutantGeneNewHandler.form
    form_json = MutantGeneNewHandler.form_json

    update_queries = ["UPDATE %s.gene SET {update_query} WHERE gene_id={record_id};"%MutantBaseHandler.schema]

@routes.view('/mutant/gene/get/{record_id}')
class MutantGeneGetHandler(generic.GenericGetHandler, MutantBaseHandler):
    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.gene WHERE gene_id={record_id}) r;"%MutantBaseHandler.schema]

@routes.view('/mutant/gene/remove/{record_id}')
class MutantGeneRemoveHandler(generic.GenericRemoveHandler, MutantBaseHandler):
    queries = ["DELETE FROM %s.gene WHERE gene_id={record_id};"%MutantBaseHandler.schema]

@routes.view('/mutant/allele/new')
class MutantAlleleNewHandler(generic.GenericQueriesHandler, MutantBaseHandler):
    tpl = 'generic_edit.jinja'
    form_path = 'js/mutant/form.js'
    form_class = 'MutantTableForm'

    levels = [1]
    levels_json = json.dumps(levels)

    form = [{'label':'Allele', 'columns':[{'name':'gene_id'}, {'name':'name'}, {'name':'commercial'}, {'name':'terminated'}]},
            {'label':None, 'columns':[{'name':'seq'}, {'name':'genotyping_oligo'}, {'name':'genotyping_strategy'}]}]
    form_json = json.dumps(form)

    insert_queries = ["INSERT INTO %s.allele ({columns}) VALUES ({query_values});"%MutantBaseHandler.schema]

@routes.view('/mutant/allele/edit/{record_id}')
class MutantAlleleEditHandler(generic.GenericRecordHandler, MutantBaseHandler):
    tpl = 'generic_edit.jinja'

    levels = [1]
    levels_json = json.dumps(levels)

    form = MutantAlleleNewHandler.form
    form_json = MutantAlleleNewHandler.form_json

    update_queries = ["UPDATE %s.allele SET {update_query} WHERE allele_id={record_id};"%MutantBaseHandler.schema]

@routes.view('/mutant/allele/get/{record_id}')
class MutantAlleleGetHandler(generic.GenericGetHandler, MutantBaseHandler):
    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.allele WHERE allele_id={record_id}) r;"%MutantBaseHandler.schema]

@routes.view('/mutant/allele/remove/{record_id}')
class MutantAlleleRemoveHandler(generic.GenericRemoveHandler, MutantBaseHandler):
    queries = ["DELETE FROM %s.allele WHERE allele_id={record_id};"%MutantBaseHandler.schema]

@routes.view('/mutant/option')
class MutantOptionHandler(generic.GenericHandler, MutantBaseHandler):
    tpl = 'generic_table.jinja'

    level_infos = [{'label': 'Option', 'url': 'mutant/option', 'column_id': 'option_id'}]
    level_infos_json = json.dumps(level_infos)

    column_infos = [{'option_id': {'search_type': 'equal_number', 'gui_type': 'text', 'required': True, 'label': 'Option ID', 'tooltip': ''},
                     'group_name': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Group name', 'tooltip': ''},
                     'option': {'search_type': 'ilike', 'gui_type': 'text', 'required': True, 'label': 'Option', 'tooltip': ''}}]
    column_infos_json = json.dumps(column_infos)

    default_sort_criterions = [[0, 'group_name', 'ASC', 'Group'], [0, 'option', 'ASC', 'Option']]
    default_sort_criterions_json = json.dumps(default_sort_criterions)

    columns = [[{'name':'group_name'}, {'name':'option'}]]
    columns_json = json.dumps(columns)

    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.option {search_query_level0} {sort_query_level0} LIMIT {limit}) r;"%MutantBaseHandler.schema]
    queries_search_prefixes = [[' WHERE ']]

@routes.view('/mutant/option/new')
class MutantOptionNewHandler(generic.GenericQueriesHandler, MutantBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = MutantOptionHandler.level_infos
    level_infos_json = MutantOptionHandler.level_infos_json

    column_infos = MutantOptionHandler.column_infos
    column_infos_json = MutantOptionHandler.column_infos_json

    form = [{'label':'Option', 'columns':[{'name':'group_name'}, {'name':'option'}]}]
    form_json = json.dumps(form)

    insert_queries = ["INSERT INTO %s.option ({columns}) VALUES ({query_values});"%MutantBaseHandler.schema]

@routes.view('/mutant/option/edit/{record_id}')
class MutantOptionEditHandler(generic.GenericRecordHandler, MutantBaseHandler):
    tpl = 'generic_edit.jinja'

    level_infos = MutantOptionHandler.level_infos
    level_infos_json = MutantOptionHandler.level_infos_json

    column_infos = MutantOptionHandler.column_infos
    column_infos_json = MutantOptionHandler.column_infos_json

    form = MutantOptionNewHandler.form
    form_json = MutantOptionNewHandler.form_json

    update_queries = ["UPDATE %s.option SET {update_query} WHERE option_id={record_id};"%MutantBaseHandler.schema]

@routes.view('/mutant/option/get/{record_id}')
class MutantOptionGetHandler(generic.GenericGetHandler, MutantBaseHandler):
    queries = ["SELECT COALESCE(array_to_json(array_agg(row_to_json(r))), '[]') FROM (SELECT * FROM %s.option WHERE option_id={record_id}) r;"%MutantBaseHandler.schema]

@routes.view('/mutant/option/remove/{record_id}')
class MutantOptionRemoveHandler(generic.GenericRemoveHandler, MutantBaseHandler):
    queries = ["DELETE FROM %s.option WHERE option_id={record_id};"%MutantBaseHandler.schema]
