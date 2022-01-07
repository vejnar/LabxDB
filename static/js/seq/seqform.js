/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2022 Charles E. Vejnar
*/

import { Form } from '../form.js';
import { createElement, joinURLs, replaceChildren } from '../utils.js'
import { Input } from '../widget/input.js';
import { SelectBool } from '../widget/input_selectbool.js'
import { SelectOption } from '../widget/input_selectoption.js'

export { SeqForm }

class SeqForm extends Form {
    constructor(dom, domModal, domModalWindow, domToolbar, name, form, columns, columnInfos, baseURL, levels, levelInfos, onlyChanges, queryArgs) {
        super()
        this.dom = dom
        this.domModal = domModal
        this.domModalWindow = domModalWindow
        this.domToolbar = domToolbar
        this.name = name
        this.form = form
        this.body = dom.createTBody()
        this.columns = columns
        this.columnInfos = columnInfos
        this.baseURL = baseURL
        this.levels = levels
        this.levelInfos = levelInfos
        this.onlyChanges = onlyChanges
        this.queryArgs = queryArgs
        this.remoteData = undefined
        this.referrer = document.referrer

        this.getOptions()
            .then((form) => form.fillForm(queryArgs))
            .catch(error => alert(error))
    }

    fillForm(queryArgs) {
        let form = this
        return new Promise(function(resolve, reject) {
            if (queryArgs['record_id'] !== undefined) {
                let formData = new FormData()
                formData.set('search_criterion', `0 ${form.levelInfos[0]['column_id']} EQUAL ${queryArgs['record_id']}`)
                formData.set('limit', 'ALL')
                // Add sort criterion
                for (let i=1, leni=form.levelInfos.length; i<leni; i++) {
                    let column = form.levelInfos[i]['column_ref']
                    if (form.levelInfos[i]['column_order'] !== undefined) {
                        column = form.levelInfos[i]['column_order']
                    }
                    if (queryArgs[i] !== undefined && queryArgs[i]['column_order'] !== undefined) {
                        column = queryArgs[i]['column_order']
                    }
                    formData.append('sort_criterion', `${i} ${column} ASC`)
                }

                let xhr = new XMLHttpRequest()
                xhr.open('POST', joinURLs([form.baseURL, form.name, 'tree']), true)
                xhr.responseType = 'json'
                xhr.onload = function() {
                    if (this.status == 200) {
                        let status = this.getResponseHeader('Query-Status')
                        if (status == 'OK') {
                            // Save data
                            form.remoteData = this.response[0]
                            // Init toolbar & form
                            if (!('init_toolbar' in queryArgs) || ('init_toolbar' in queryArgs && queryArgs['init_toolbar'])) {
                                form.initToolbar()
                            }
                            form.domInputs = form.initForm()
                            resolve()
                        } else {
                            reject(Error('Query failed: '+status))
                        }
                    } else {
                        alert('Request failed: '+this.statusText)
                        reject(Error(xhr.statusText))
                    }
                }
                // Send
                xhr.send(formData)
            } else {
                resolve()
            }
        })
    }

    initToolbar() {
        let div = createElement('DIV', 'control', undefined)
        // Add info from level 0
        for (let i=0, leni=this.columns[0].length; i<leni; i++) {
            let info = createElement('DIV', 'title', this.remoteData[this.columns[0][i]['name']])
            div.appendChild(info)
        }
        this.domToolbar.appendChild(div)
        
        // Sort
        let levelAsOptions = []
        let levelSort = 1
        for (let i=0, leni=this.columns[levelSort].length; i<leni; i++) {
            let column = this.columns[1][i]
            levelAsOptions.push({option_id:i, group_name:'sort', optionValue:column['name'], option:this.columnInfos[levelSort][column['name']]['label']})
        }
        // Select sort
        div = createElement('DIV', 'control', undefined)
        let inputSort = new SelectOption({'name':'sort'}, levelAsOptions)
        inputSort.dom.Form = this
        inputSort.dom.Input = inputSort
        inputSort.dom.QueryArgs = this.queryArgs
        inputSort.dom.LevelSort = levelSort
        inputSort.addEventListener('change', function(e) {
            let queryArgs = Object.assign({}, this.QueryArgs)
            queryArgs[this.LevelSort] = {'column_order': this.Input.getValue()}
            queryArgs['init_toolbar'] = false
            this.Form.fillForm(queryArgs)
        })
        div.appendChild(createElement('SPAN', undefined, 'Sort: '))
        div.appendChild(inputSort.dom)
        this.domToolbar.appendChild(div)
        // Buttons
        div = createElement('DIV', 'control', undefined)
        // Cancel
        this.appendCancelButton(div)
        // Submit
        let submitButton = createElement('BUTTON', 'button', 'Submit')
        submitButton.Form = this
        submitButton.onclick = function (e) { this.Form.submitForm('reload') }
        div.appendChild(submitButton)
        // Submit & Exit
        submitButton = createElement('BUTTON', 'button', 'Submit & Exit')
        submitButton.Form = this
        submitButton.onclick = function (e) { this.Form.submitForm() }
        div.appendChild(submitButton)
        
        this.domToolbar.appendChild(div)
    }

    hideTable(domTable) {
        domTable.style.display = 'none'
    }
    
    toggleCopy(domTable, toggle) {
        let domCells = domTable.getElementsByClassName('cell-copy')
        if (typeof toggle == 'undefined') {
            if (domCells[0].style.display == 'none') {
                toggle = 'on'
            } else {
                toggle = 'off'
            }
        }
        for (let i=0, leni=domCells.length; i<leni; i++) {
            if (toggle == 'on') {
                domCells[i].style.display = ''
            } else {
                domCells[i].style.display = 'none'
            }
        }
    }

    copyToAll(level, column, input) {
        let v = input.getValue()
        if (confirm(`Copy ${v} to all ${column['name']} ?`)) {
            for (let i=0, leni=this.domInputs[level].length; i<leni; i++) {
                this.domInputs[level][i].get(column['name']).setValue(v)
            }
        }
    }

    getTable(data, level) {
        let table = document.createElement('TABLE')
        table.className = 'data-table level'+level

        // Header
        let row = document.createElement('TR')
        let el = document.createElement('TH')
        el.colSpan = 3
        let div = createElement('DIV', 'header-div', this.levelInfos[level]['label'])
        // Remove button
        let removeButton = createElement('BUTTON', 'button header-remove-button', '✖')
        removeButton.Form = this
        removeButton.domTable = table
        removeButton.onclick = function (e) { this.Form.hideTable(this.domTable) }
        div.appendChild(removeButton)
        // Expand button
        let expandButton = createElement('BUTTON', 'button header-expand-button', '+')
        expandButton.Form = this
        expandButton.domTable = table
        expandButton.onclick = function (e) { this.Form.toggleCopy(this.domTable) }
        div.appendChild(expandButton)
        el.appendChild(div)
        row.appendChild(el)
        table.appendChild(row)

        // Save Inputs
        let dr = new Map()

        // Add hidden input with record ID
        let columnId = this.levelInfos[level]['column_id']
        let input = new Input({'name':columnId, 'gui_type':'hidden', 'always_export':true})
        input.initValue(data[columnId])
        dr.set(columnId, input)

        // Inputs
        for (let i=0, leni=this.columns[level].length; i<leni; i++) {
            let column = this.columns[level][i]
            let columnInfo = this.columnInfos[level][column['name']]
            let row = document.createElement('TR')
            let cell = document.createElement('TD')
            // Input: label
            cell.textContent = columnInfo['label']
            row.appendChild(cell)
            cell = document.createElement('TD')
            // Input
            columnInfo['name'] = column['name']
            // For option and input: search_type is used to set cast function
            let input
            let button = null
            switch (columnInfo['gui_type']) {
                case 'select_bool_none':
                    input = new SelectBool(columnInfo)
                    break
                case 'select_option_none':
                    input = new SelectOption(columnInfo, this.options)
                    button = this.getAddOption(column)
                    break
                default:
                    input = new Input(columnInfo)
            }
            input.initValue(data[column['name']])
            dr.set(column['name'], input)
            cell.appendChild(input.dom)
            if (button !== null) {
                cell.appendChild(button)
            }
            row.appendChild(cell)
            // Copy-paste buttons
            cell = createElement('TD', 'cell-copy', undefined)
            cell.style.display = 'none'
            let copyButton = createElement('BUTTON', 'button', 'Copy')
            copyButton.Form = this
            copyButton.Level = level
            copyButton.Column = column
            copyButton.Input = input
            copyButton.onclick = function (e) { this.Form.copyToAll(this.Level, this.Column, this.Input) }
            cell.appendChild(copyButton)
            row.appendChild(cell)

            table.appendChild(row)
        }
        return [table, dr]
    }

    initForm() {
        let newForm = document.createDocumentFragment()
        let domInputs = [[], [], [], []]
        let row = document.createElement('TR')
        for (let i=0, leni=this.remoteData['children'].length; i<leni; i++) {
            let cellLeft = document.createElement('TD')
            cellLeft.className = 'main-form main-form-cell'

            // First level cell
            let cellLeftDiv = document.createElement('DIV')
            cellLeftDiv.className = 'form-row'
            let ld = this.getTable(this.remoteData['children'][i], 1)
            cellLeftDiv.appendChild(ld[0])
            domInputs[1].push(ld[1])
            cellLeft.appendChild(cellLeftDiv)
            row.appendChild(cellLeft)

            // Remaining levels cell
            let cellRight = document.createElement('TD')
            cellRight.className = 'main-form main-form-cell'
            if ('children' in this.remoteData['children'][i] && this.remoteData['children'][i]['children'] != null) {
                for (let j=0, lenj=this.remoteData['children'][i]['children'].length; j<lenj; j++) {
                    let cellRightDiv = document.createElement('DIV')
                    cellRightDiv.className = 'form-row'

                    let cell = document.createElement('DIV')
                    cell.className = 'form-cell'
                    let rd = this.getTable(this.remoteData['children'][i]['children'][j], 2)
                    cell.appendChild(rd[0])
                    domInputs[2].push(rd[1])
                    cellRightDiv.appendChild(cell)

                    cell = document.createElement('DIV')
                    cell.className = 'form-cell'
                    if ('children' in this.remoteData['children'][i]['children'][j] && this.remoteData['children'][i]['children'][j]['children'] != null) {
                        for (let k=0, lenk=this.remoteData['children'][i]['children'][j]['children'].length; k<lenk; k++) {
                            let cd = this.getTable(this.remoteData['children'][i]['children'][j]['children'][k], 3)
                            cell.appendChild(cd[0])
                            domInputs[3].push(cd[1])
                        }
                    }
                    cellRightDiv.appendChild(cell)

                    cellRight.appendChild(cellRightDiv)
                }
            }
            row.appendChild(cellRight)
        }
        newForm.appendChild(row)
        // Add everything
        replaceChildren(this.body, newForm)

        return domInputs
    }

    prepareData() {
        let data = []
        for (let ilevel=0, lenilevel=this.domInputs.length; ilevel<lenilevel; ilevel++) {
            data.push([])
            for (let iform=0, leniform=this.domInputs[ilevel].length; iform<leniform; iform++) {
                let record = {}
                for (let [column, input] of this.domInputs[ilevel][iform]) {
                    if (this.onlyChanges == false || input.alwaysExport || input.hasChanged()) {
                        record[column] = input.getValue()
                    }
                }
                // More than just the recordID
                if (Object.keys(record).length > 1) {
                    data[ilevel].push(record)
                }
            }
        }
        return data
    }
}
