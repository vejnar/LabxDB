/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright © 2018 Charles E. Vejnar
*/

import { Form } from '../form.js';
import { createElement, joinURLs, removeChildren } from '../utils.js'
import { Input } from '../widget/input.js';

export { AssignForm }

class AssignForm extends Form {
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
        this.colors = [[],
                       ['rgb(51, 226, 69)', 'rgb(16, 161, 33)', 'rgb(181, 245, 186)'],
                       ['rgb(213, 103, 0)', 'rgb(255, 127, 0)', 'rgb(248, 179, 115)'],
                       ['rgb(161, 218, 234)', 'rgb(5, 125, 161)', 'rgb(6, 185, 234)']]

        this.initToolbar()
        this.initHeader()
        this.initFooter()
        this.getRecords()
    }

    initToolbar() {
        // Input
        let div = createElement('DIV', 'control', undefined)
        this.inputSearch = new Input({'name': 'search'})
        div.appendChild(this.inputSearch.dom)
        this.domToolbar.appendChild(div)
        // Search button
        div = createElement('DIV', 'control', undefined)
        let searchButton = createElement('BUTTON', 'button', 'Search')
        searchButton.Form = this
        searchButton.onclick = function (e) { this.Form.getRecords() }
        div.appendChild(searchButton)
        this.domToolbar.appendChild(div)
        // Prefix
        div = createElement('DIV', 'control', undefined)
        this.inputPrefix = new Input({'name': 'prefix', 'size': 4})
        div.appendChild(createElement('SPAN', undefined, 'Prefix: '))
        div.appendChild(this.inputPrefix.dom)
        this.domToolbar.appendChild(div)
        // Input length
        div = createElement('DIV', 'control', undefined)
        div.appendChild(createElement('SPAN', undefined, 'Field length: '))
        // Decrease button
        let decreaseButton = createElement('BUTTON', 'button', '-')
        decreaseButton.Form = this
        decreaseButton.onclick = function (e) { this.Form.setInputsLength(-5) }
        div.appendChild(decreaseButton)
        // Increase button
        let increaseButton = createElement('BUTTON', 'button', '+')
        increaseButton.Form = this
        increaseButton.onclick = function (e) { this.Form.setInputsLength(5) }
        div.appendChild(increaseButton)
        this.domToolbar.appendChild(div)
    }

    initHeader() {
        let header = this.dom.createTHead()
        let row = header.insertRow(0)
        row.appendChild(document.createElement('TH'))
        for (let i=this.levels.length - 1; i>=0; i--) {
            row.appendChild(createElement('TH', undefined, this.levelInfos[i]['label']))
        }
    }

    initFooter() {
        let footer = this.dom.createTFoot()
        let row = footer.insertRow(0)
        let cell = document.createElement('TH')
        cell.colSpan = this.levels.length + 1
        // Sort
        let sortButton = createElement('BUTTON', 'button', 'Check & Sort')
        sortButton.Form = this
        sortButton.onclick = function (e) { this.Form.sortRows(); this.Form.checkForm() }
        cell.appendChild(sortButton)
        // Submit & Cancel
        this.appendControlButton(cell)
        row.appendChild(cell)
        // Add to DOM
        this.dom.appendChild(footer)
    }

    setInputsLength(diffLength) {
        for (let i=0, leni=this.domCells.length; i<leni; i++) {
            for (let j=0, lenj=this.domCells[i].length; j<lenj; j++) {
                let cell = this.domCells[i][j]
                if (cell.domInput !== undefined && cell.domInput.size + diffLength > 0) {
                    cell.domInput.size += diffLength
                }

            }
        }
    }

    getRecords() {
        let formData = new FormData()
        let nLevel = this.levelInfos.length - 1
        formData.set('search_criterion', `${nLevel} ${this.levelInfos[nLevel-1]['column_ref']} EQUAL NULL`)
        if (this.inputSearch.getValue() != null) {
            formData.append('search_criterion', `${nLevel} ${this.levelInfos[nLevel]['column_ref']} FUZZY ${this.inputSearch.getValue()}`)
        }
        formData.set('search_gate', 'AND')
        formData.set('sort_criterion', `${nLevel} ${this.levelInfos[nLevel]['column_ref']} ASC`)
        formData.set('limit', '500')

        // Send data
        let xhr = new XMLHttpRequest()
        xhr.form = this
        xhr.open('POST', joinURLs([this.baseURL, this.levelInfos[3]['url']]), true)
        xhr.responseType = 'json'
        xhr.onload = function() {
            if (this.status == 200) {
                let status = this.getResponseHeader('Query-Status')
                if (status == 'OK') {
                    // Save data
                    this.form.remoteData = this.response
                    // Init form
                    removeChildren(this.form.body)
                    this.form.domCells = this.form.initForm()
                } else {
                    alert('Query failed: '+status)
                }
            } else {
                alert('Request failed: '+this.statusText)
            }
        }
        // Send
        xhr.send(formData)
    }

    duplicateRecord(record, level, suffix) {
        // Create new record without old ID and with new reference
        let newRecord = Object.assign({}, record)
        delete newRecord[this.levelInfos[level]['column_id']]
        newRecord[this.levelInfos[level]['column_ref']] += '_' + suffix
        let data = [newRecord]

        // Send data
        let xhr = new XMLHttpRequest()
        xhr.form = this
        xhr.open('POST', joinURLs([this.baseURL, this.levelInfos[level]['url'], 'new']), true)
        xhr.responseType = 'json'
        xhr.onload = function() {
            if (this.status == 200) {
                let status = this.getResponseHeader('Query-Status')
                if (status == 'OK') {
                    this.form.getRecords()
                } else {
                    if (status.startsWith('duplicate key value violates unique constraint')) {
                        suffix += 1
                        this.form.duplicateRecord(record, level, suffix)
                    } else {
                        alert('Query failed: '+status)
                    }
                }
            } else {
                alert('Request failed: '+this.statusText)
            }
        }
        // Send
        xhr.send(JSON.stringify(data))
    }

    removeRecord(record, level) {
        let recordID = record[this.levelInfos[level]['column_id']]

        // Send data
        let xhr = new XMLHttpRequest()
        xhr.form = this
        xhr.open('GET', joinURLs([this.baseURL, this.levelInfos[level]['url'], 'remove', recordID]), true)
        xhr.responseType = 'json'
        xhr.onload = function() {
            if (this.status == 200) {
                let status = this.getResponseHeader('Query-Status')
                if (status == 'OK') {
                    this.form.getRecords()
                } else {
                    alert('Query failed: '+status)
                }
            } else {
                alert('Request failed: '+this.statusText)
            }
        }
        // Send
        xhr.send('[]')
    }

    initForm() {
        let newForm = document.createDocumentFragment()
        let domCells = []
        for (let i=0, leni=this.remoteData.length; i<leni; i++) {
            domCells[i] = []
            let row = document.createElement('TR')
            // Control
            let control = document.createElement('TD')
            // Control: Duplicate
            let button = createElement('BUTTON', 'button', 'Duplicate')
            button.Form = this
            button.Record = this.remoteData[i]
            button.onclick = function (e) { if (confirm('Duplicate this item?')) { this.Form.duplicateRecord(this.Record, 3, 1) } }
            control.appendChild(button)
            // Control: Remove
            button = createElement('BUTTON', 'button', 'Remove')
            button.Form = this
            button.Record = this.remoteData[i]
            button.onclick = function (e) { if (confirm('Remove this item?')) { this.Form.removeRecord(this.Record, 3) } }
            control.appendChild(button)
            // Add control
            domCells[i].push(control)
            row.appendChild(control)
            // Title
            let info = document.createElement('TD')
            let level = this.levels.length - 1
            for (let j=0, lenj=this.columns[this.levels[level]].length; j<lenj; j++) {
                let className = undefined
                let v = this.remoteData[i][this.columns[level][j]['name']]
                if (j == 0) {
                    className = 'title'
                }
                if (this.columns[level][j]['name'] == this.levelInfos[level]['column_ref']) {
                    info.recordID = v
                }
                info.appendChild(createElement('DIV', className, v))
            }
            domCells[i].push(info)
            row.appendChild(info)
            // Tree cells
            let ycell = 2 // 0 and 1 are control and first level
            for (let j=this.levels.length - 2; j>=0; j--) {
                // Input cell
                let cell = document.createElement('TD')
                cell.className = 'input-cell'
                // Input cell: Select
                let select = document.createElement('SELECT')
                select.x = i
                select.y = ycell
                // Option
                let option = document.createElement('OPTION')
                option.rawValue = true
                option.textContent = 'New'
                select.appendChild(option)
                // Option
                option = document.createElement('OPTION')
                option.rawValue = false
                option.textContent = 'Append'
                select.appendChild(option)
                // Option event
                select.Form = this
                select.onchange = function(e) { this.Form.toggleRow(e.target.value, e.target.x, e.target.y) }
                cell.appendChild(select)
                // Input cell: New name
                let input = document.createElement('INPUT')
                input.type = 'text'
                input.required = true
                input.spellcheck = false
                cell.appendChild(input)
                row.appendChild(cell)
                // Add to cell
                cell.domSelect = select
                cell.domInput = input
                domCells[i].push(cell)
                ycell++
            }
            newForm.appendChild(row)
        }
        // Add everything
        this.body.appendChild(newForm)
        return domCells
    }

    toggleRow(v, x, y) {
        if (v == 'Append') {
            for (let i=y + 1, leni=this.domCells[x].length; i<leni; i++) {
                this.domCells[x][i].style.visibility = 'hidden'
            }
        } else {
            for (let i=y + 1, leni=this.domCells[x].length; i<leni; i++) {
                this.domCells[x][i].style.visibility = 'visible'
                this.domCells[x][i].getElementsByTagName('SELECT')[0].value = 'New'
            }
        }
    }

    sortRows() {
        // Get row(s)
        let store = []
        let valid = false
        mainloop:
            for (let i=0, leni=this.domCells.length; i<leni; i++) {
                let key = ''
                for (let j=this.domCells[i].length - 1; j>=0; j--) {
                    if (this.domCells[i][j].domInput !== undefined && this.domCells[i][j].style.visibility != 'hidden') {
                        key += this.domCells[i][j].domInput.value
                        valid = this.domCells[i][j].domInput.reportValidity()
                        if (valid == false) {
                            break mainloop
                        }
                    }
                }
                store.push([key, this.domCells[i]])
            }
        if (valid == true) {
            // Sort
            store.sort(function(a, b) {
                return a[0] > b[0] ? 1 : a[0] < b[0] ? -1 : 0
            })
            // Place back sorted row(s)
            removeChildren(this.body)
            for (let i=0, leni=store.length; i<leni; i++) {
                let row = this.body.insertRow()
                for (let j=0, lenj=store[i][1].length; j<lenj; j++) {
                    row.appendChild(store[i][1][j])
                    // Reset x
                    if (this.domCells[i][j].domSelect !== undefined) {
                        store[i][1][j].domSelect.x = i
                    }
                }
                // Re-order also domCells
                this.domCells[i] = store[i][1]
            }
            // Color
            let icolor = -1
            let currentValue = ''
            for (let j=2, lenj=this.domCells[0].length; j<lenj; j++) { // 0 and 1 are control and first level
                for (let i=0, leni=this.domCells.length; i<leni; i++) {
                    let cell = this.domCells[i][j]
                    if (cell.domInput !== undefined) {
                        if (cell.domInput.value == '' || cell.domInput.value != currentValue) {
                            currentValue = cell.domInput.value
                            icolor++
                        }
                    }
                    cell.style.borderLeftColor = this.colors[j-1][icolor % this.colors[j-1].length]
                }
                icolor = -1
                currentValue = ''
            }
        }
    }

    getCheckFormPromises() {
        let promises = []
        for (let i=0, leni=this.domCells.length; i<leni; i++) {
            for (let j=0, lenj=this.domCells[i].length; j<lenj; j++) {
                let cell = this.domCells[i][j]
                if (cell.domSelect !== undefined) {
                    if (cell.domInput.value.length == 0) {
                        cell.domInput.reportValidity()
                        promises = ['ABORT']
                        break
                    } else {
                        if (cell.domSelect.value.toLowerCase() == 'append') {
                            promises.push(this.refExists(cell.domInput.value, this.levelInfos.length-j))
                            break
                        }
                    }
                }
            }
        }
        return promises
    }

    refExists(recordRef, level) {
        let form = this
        return new Promise(function(resolve, reject) {
            let formData = new FormData()
            formData.set('search_criterion', `${level} ${form.levelInfos[level]['column_ref']} EQUAL ${recordRef}`)
            formData.set('limit', '5')

            let xhr = new XMLHttpRequest()
            xhr.open('POST', joinURLs([form.baseURL, form.levelInfos[level]['url']]), true)
            xhr.responseType = 'json'
            xhr.onload = function() {
                if (this.status == 200) {
                    let status = this.getResponseHeader('Query-Status')
                    if (status == 'OK') {
                        if (this.response.length == 1) {
                            resolve('OK')
                        } else {
                            resolve(recordRef+' not found')
                        }
                    } else {
                        reject(Error('Query failed: '+status))
                    }
                } else {
                    reject(Error(this.statusText))
                }
            }
            // Send
            xhr.send(formData)
        })
    }

    checkForm() {
        let promises = this.getCheckFormPromises()
        Promise.all(promises).then(function(results) {
            for (let i=0, leni=results.length; i<leni; i++) {
                if (results[i] == 'ABORT') {
                    break
                } else if (results[i] != 'OK') {
                    alert(results[i])
                    break
                }
            }
        }).catch(reason => {
            alert(reason)
        })
    }

    submitForm() {
        // Sort
        this.sortRows()
        // Check
        let promises = this.getCheckFormPromises()
        let form = this
        Promise.all(promises).then(function(results) {
            // Check all reference(s) exists
            let ok = true
            for (let i=0, leni=results.length; i<leni; i++) {
                if (results[i] == 'ABORT') {
                    ok = false
                    break
                } else if (results[i] != 'OK') {
                    ok = false
                    alert(results[i])
                    break
                }
            }
            // Query
            if (ok) {
                // Prepare data
                let data = []
                for (let i=0, leni=form.domCells.length; i<leni; i++) {
                    let l = []
                    for (let j=0, lenj=form.domCells[i].length; j<lenj; j++) {
                        let cell = form.domCells[i][j]
                        if (cell.domSelect !== undefined) {
                            l.push([cell.domSelect.value.toLowerCase(), cell.domInput.value])
                        } else if (cell.recordID !== undefined) {
                            l.push(['new', cell.recordID])
                        }
                    }
                    data.push(l)
                }

                // Send data
                let xhr = new XMLHttpRequest()
                xhr.form = this
                xhr.open('POST', '', true)
                xhr.responseType = 'json'
                xhr.onload = function() {
                    if (this.status == 200) {
                        let status = this.getResponseHeader('Query-Status')
                        if (status == 'OK') {
                            alert('Query has been successfully executed')
                            // Redirect
                            window.location.href = form.referrer
                        } else {
                            alert('Query failed: '+status)
                        }
                    } else {
                        alert('Request failed: '+this.statusText)
                    }
                }
                // Send
                xhr.send(JSON.stringify({'prefix':form.inputPrefix.getValue(), 'query':data}))
            }
        }).catch(reason => {
            alert(reason)
        })
    }
}
