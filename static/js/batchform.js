/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2022 Charles E. Vejnar
*/

import { createElement, removeChildren } from './utils.js'
import { Form } from './form.js'

export { BatchForm }

class BatchForm extends Form {
    constructor(dom, domModal, domModalWindow, name, form, columnInfos, baseURL, levelInfos, onlyChanges, queryArgs) {
        super()
        this.dom = dom
        this.domModal = domModal
        this.domModalWindow = domModalWindow
        this.name = name
        this.form = form
        this.columnInfos = columnInfos
        this.baseURL = baseURL
        this.levelInfos = levelInfos
        this.onlyChanges = onlyChanges
        this.queryArgs = queryArgs
        this.remoteData = undefined
        this.referrer = document.referrer
        this.referrerParams = this.parseCriterion(window.location.search)

        this.setColumns()
        this.initForm()
        this.toggleModal('off')
    }

    setColumns() {
        this.columns = []
        for (let i=0, leni=this.form.length; i<leni; i++) {
            for (let j=0, lenj=this.form[i]['columns'].length; j<lenj; j++) {
                this.columns.push(this.form[i]['columns'][j])
            }
        }
    }

    initForm() {
        let newForm = document.createDocumentFragment()

        // Header
        let row = document.createElement('TR')
        row.appendChild(createElement('TH', 'form-head', 'Batch'))
        newForm.appendChild(row)

        // Data
        row = document.createElement('TR')
        let cell = document.createElement('TD')
        let rowForm = createElement('DIV', 'record-row-form', undefined)
        let rcell = createElement('DIV', 'record-cell-form', undefined)
        let inputQuery = document.createElement('TEXTAREA')
        // Input
        inputQuery.className = 'query-data'
        inputQuery.maxlength = 10000
        rcell.appendChild(inputQuery)
        rowForm.appendChild(rcell)
        // Table
        rcell = createElement('DIV', 'record-cell-form', undefined)
        let table = createElement('TABLE', 'query-table', undefined)
        let header = table.createTHead()
        let drow = header.insertRow(0)
        // Headers
        for (let i=0, leni=this.columns.length; i<leni; i++) {
            drow.appendChild(createElement('TH', undefined, this.columns[i]['name']))
        }
        rcell.appendChild(table)
        rowForm.appendChild(rcell)
        // Append
        cell.appendChild(rowForm)
        row.appendChild(cell)
        newForm.appendChild(row)

        // Format
        row = document.createElement('TR')
        cell = document.createElement('TD')
        rowForm = createElement('DIV', 'record-row-form', undefined)
        rcell = createElement('DIV', 'record-cell-form', undefined)
        // Select
        let inputSep = document.createElement('SELECT')
        // Option
        let option = document.createElement('OPTION')
        option.value = 'TAB'
        option.textContent = 'Tabulation'
        inputSep.appendChild(option)
        // Option
        option = document.createElement('OPTION')
        option.value = 'COMMA'
        option.textContent = 'Comma'
        inputSep.appendChild(option)
        rcell.appendChild(inputSep)
        rowForm.appendChild(rcell)
        // Status
        rcell = createElement('DIV', 'record-cell-form', undefined)
        let status = document.createElement('DIV')
        rcell.appendChild(status)
        rowForm.appendChild(rcell)
        // Append
        cell.appendChild(rowForm)
        row.appendChild(cell)
        newForm.appendChild(row)

        // Buttons
        row = document.createElement('TR')
        cell = document.createElement('TH')
        // Prepare
        let prep = createElement('BUTTON', 'button', 'Parse query')
        prep.tableForm = this
        prep.onclick = function (e) { this.tableForm.parseQuery() }
        cell.appendChild(prep)
        // Submit
        let submit = createElement('BUTTON', 'button', 'Submit')
        submit.tableForm = this
        submit.onclick = function (e) { this.tableForm.submitForm() }
        cell.appendChild(submit)
        // Cancel
        let cancel = document.createElement('A')
        cancel.className = 'button'
        cancel.href = 'javascript:history.back()'
        cancel.textContent = 'Cancel'
        cell.appendChild(cancel)
        row.appendChild(cell)
        newForm.appendChild(row)
        // Add everything
        this.dom.appendChild(newForm)

        // Set dom nodes
        this.domQuery = inputQuery
        this.domTableQuery = table.createTBody()
        this.domSep = inputSep
        this.domStatus = status
    }

    parseQuery() {
        this.data = []
        // Empty main table
        removeChildren(this.domTableQuery)
        // Clean status
        this.domStatus.textContent = ''
        // Separator
        let sep = ''
        if (this.domSep.value == 'COMMA') {
            sep = ','
        } else {
            sep = '\t'
        }
        // Parse user data
        let lines = this.domQuery.value.split('\n')
        for (let i=0, leni=lines.length; i<leni; i++) {
            if (lines[i].length > 0) {
                let fields = lines[i].split(sep)
                if (fields.length == this.columns.length) {
                    let row = document.createElement('TR')
                    let dr = {}
                    for (let j=0, lenj=fields.length; j<lenj; j++) {
                        let cell = document.createElement('TD')
                        if (fields[j] == '') {
                            cell.textContent = 'null'
                            cell.className = 'null-value'
                            fields[j] = null
                        } else {
                            cell.textContent = fields[j]
                        }
                        row.appendChild(cell)
                        dr[this.columns[j]['name']] = fields[j]
                    }
                    this.domTableQuery.appendChild(row)
                    this.data.push(dr)
                } else {
                    this.domStatus.textContent = `Missing column (row ${(i+1)})`
                    removeChildren(this.domTableQuery)
                    this.data = []
                    break
                }
            }
        }
    }

    prepareData() {
        return this.data
    }
}
