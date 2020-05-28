/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { createElement, joinURLs } from './utils.js'
import { Form } from './form.js'
import { Input } from './widget/input.js'
import { InputImage } from './widget/input_image.js'
import { SelectBool } from './widget/input_selectbool.js'
import { SelectOption } from './widget/input_selectoption.js'
import { Textarea } from './widget/input_textarea.js'

export { TableForm }

class TableForm extends Form {
    constructor(dom, domModal, domModalWindow, name, form, columnInfos, baseURL, levelInfos, onlyChanges, queryArgs, addonStart) {
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
        this.addonStart = addonStart

        if (queryArgs['count'] === undefined) {
            this.count = 1
        } else {
            this.count = queryArgs['count']
        }
        this.remoteData = undefined
        this.referrer = document.referrer
        this.referrerParams = this.parseCriterion(window.location.search)

        this.getOptions()
            .then((form) => form.initFormPromise())
            .then((form) => form.fillForm(queryArgs))
            .catch(error => alert(error))
        this.toggleModal('off')
    }

    initFormPromise() {
        return new Promise(function(resolve, reject) {
            form.initForm()
            resolve(form)
        })
    }

    initForm() {
        let newForm = document.createDocumentFragment()
        let inputs = []
        // Add user form
        for (let iform=0, leniform=this.count; iform<leniform; iform++) {
            let dr = new Map()
            // For each section of the form
            for (let i=0, leni=this.form.length; i<leni; i++) {
                // Head
                let htext = this.form[i]['label']
                if (htext !== null) {
                    let row = document.createElement('TR')
                    row.appendChild(createElement('TH', 'form-head', htext))
                    newForm.appendChild(row)
                }
                // Cell
                let row = document.createElement('TR')
                let cell = document.createElement('TD')
                let rowForm = createElement('DIV', 'record-row-form', undefined)
                // Inputs
                for (let j=0, lenj=this.form[i]['columns'].length; j<lenj; j++) {
                    let column = this.form[i]['columns'][j]
                    let columnInfo = this.columnInfos[column['name']]
                    let rcell = createElement('DIV', 'record-cell-form', undefined)
                    let label = createElement('DIV', 'tooltip', columnInfo['label'])
                    if (columnInfo['tooltip'].length > 0) {
                        label.appendChild(createElement('SPAN', 'tooltiptext', columnInfo['tooltip']))
                    }
                    columnInfo['name'] = column['name']
                    rcell.appendChild(label)
                    rcell.appendChild(document.createElement('BR'))
                    // Input
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
                        case 'textarea':
                            input = new Textarea(columnInfo)
                            break
                        case 'file':
                            if ('accept' in columnInfo && columnInfo['accept'].startsWith('image')) {
                                input = new InputImage(columnInfo)
                            } else {
                                input = new Input(columnInfo)
                            }
                            break
                        default:
                            input = new Input(columnInfo)
                    }
                    dr.set(column['name'], input)
                    rcell.appendChild(input.dom)
                    if (button !== null) {
                        rcell.appendChild(button)
                    }

                    // Default
                    if ('default' in columnInfo) {
                        input.setValue(this.addonStart(columnInfo['default'], input))
                    }
                    // Model-defined button
                    if ('button' in columnInfo) {
                        let userButton = createElement('BUTTON', 'button', columnInfo['button']['label'])
                        userButton.Form = this
                        userButton.onclick = function (e) { this.Form.addonStart(columnInfo['button']['click'], this, e) }
                        rcell.appendChild(userButton)
                    }

                    rowForm.appendChild(rcell)
                }
                // Append
                cell.appendChild(rowForm)
                row.appendChild(cell)
                newForm.appendChild(row)
            }
            inputs.push(dr)
        }
        // Buttons
        let row = document.createElement('TR')
        let cell = document.createElement('TH')
        this.appendControlButton(cell)
        row.appendChild(cell)
        newForm.appendChild(row)
        // Add everything
        this.dom.appendChild(newForm)
        // Save inputs
        this.inputs = inputs
        return inputs
    }

    fillForm(queryArgs) {
        return new Promise(function(resolve, reject) {
            if (queryArgs['record_id'] !== undefined) {
                let xhr = new XMLHttpRequest()
                xhr.open('GET', joinURLs([form.baseURL, form.levelInfos['url'], 'get', queryArgs['record_id']]), true)
                xhr.responseType = 'json'
                xhr.onload = function() {
                    if (this.status == 200) {
                        let status = this.getResponseHeader('Query-Status')
                        if (status == 'OK') {
                            // Save data
                            form.remoteData = this.response[0][0]
                            // Copy-paste from response to form to inputs[0] (i.e. compatible with editing a single record at a time)
                            for (let [column, input] of form.inputs[0]) {
                                input.initValue(this.response[0][0][column])
                            }
                            resolve()
                        } else {
                            reject(Error('Query failed: ' + status))
                        }
                    } else {
                        reject(Error(this.statusText))
                    }
                }
                // Send
                xhr.send('[]')
            } else {
                resolve()
            }
        })
    }

    prepareData() {
        let data = []
        for (let iform=0, leniform=this.count; iform<leniform; iform++) {
            let dr = {}
            for (let [column, input] of this.inputs[iform]) {
                if (input.reportValidity()) {
                    let value = input.getValue()
                    if (this.onlyChanges == false || input.alwaysExport || input.hasChanged()) {
                        dr[column] = value
                    }
                } else {
                    return null
                }
            }
            data.push(dr)
        }
        return data
    }
}
