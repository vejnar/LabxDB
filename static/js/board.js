/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2022 Charles E. Vejnar
*/

import { createElement, removeChildren, joinURLs } from './utils.js'

export { Board }

class Board {
    getRecords(form) {
        let formData = new FormData(form)

        // Empty body
        removeChildren(this.body)
        // Start loader
        this.toggleLoader('on')

        let xhr = new XMLHttpRequest()
        xhr.board = this
        // Post
        xhr.open('POST', form.action, true)
        xhr.responseType = 'json'
        xhr.onload = function() {
            // Stop loader
            this.board.toggleLoader('off')
            if (this.status == 200) {
                let status = this.getResponseHeader('Query-Status')
                if (status == 'OK') {
                    // Load new content
                    this.board.remoteData = this.response
                    this.board.addContent(this.response)
                    // Location: go to anchor if provided
                    if (window.location.hash.length > 0) {
                        window.location.hash = window.location.hash
                    }
                } else {
                    alert('Query failed: ' + status)
                }
            } else {
                alert('Request failed: ' + this.statusText)
            }
        }
        // Send
        xhr.send(formData)
    }

    toHuman(s) {
        if (s === true) {
            return 'Yes'
        } else if (s === false) {
            return 'No'
        } else if (s === null) {
            return ''
        } else {
            return s
        }
    }

    exportData() {
        // Prepare data
        let data = this.columns.join(',') + '\n'
        data = this.columns.map(c => c['name']) + '\n'
        for (let i=0, leni=this.remoteData.length; i<leni; i++) {
            let line = []
            for (let j=0, lenj=this.columns.length; j<lenj; j++) {
                let v = this.remoteData[i][this.columns[j]['name']]
                if (v == null) {
                    line.push(`""`)
                } else {
                    line.push(`"${v}"`)
                }
            }
            data += line.join(',') + '\n'
        }
        // Create link
        let link = document.createElement('A')
        link.download = 'export.csv'
        link.href = 'data:attachment/csv,' + encodeURIComponent(data)
        document.body.appendChild(link)
        // Fire link
        link.click()
        // Remove link when done
        document.body.removeChild(link)
    }

    toggleLoader(toggle) {
        if (typeof toggle == 'undefined') {
            if (this.domLoader.style.opacity = '1') {
                toggle = 'off'
            } else {
                toggle = 'on'
            }
        }
        if (toggle == 'on') {
            this.domLoader.style.opacity = '1'
        } else {
            this.domLoader.style.opacity = '0'
        }
    }

    getActionURL(action, record, level) {
        if (record === undefined) {
            return joinURLs([this.baseURL, this.levelInfos['url'], action])
        } else if (level === undefined) {
            return joinURLs([this.baseURL, this.levelInfos['url'], action, record[this.levelInfos['column_id']]])
        } else {
            return joinURLs([this.baseURL, this.levelInfos[level]['url'], action, record[this.levelInfos[level]['column_id']]])
        }
    }

    getControlEdit(record, level) {
        // Edit form
        let form = document.createElement('FORM')
        form.method = 'get'
        form.action = this.getActionURL('edit', record, level)
        let button = createElement('BUTTON', 'button', 'Edit')
        button.type = 'submit'
        form.appendChild(button)
        // Add the current search and sort criterions, and limit upon submit
        form.onsubmit = function (e) {
            let params = window.toolbar.getSearchCriterions().map(element => ['search_criterion', element])
            params = params.concat(window.toolbar.getSortCriterions().map(element => ['sort_criterion', element]))
            params = params.concat([['limit', window.toolbar.getLimit()]])
            for (let i=0, leni=params.length; i<leni; i++) {
                let input = document.createElement('INPUT')
                input.name = params[i][0]
                input.type = 'hidden'
                input.value = params[i][1]
                e.target.appendChild(input)
            }
        }
        return form
    }

    getControlRemove(record, level) {
        // Remove
        let form = document.createElement('FORM')
        form.method = 'get'
        form.action = this.getActionURL('remove', record, level)
        let button = createElement('BUTTON', 'button', 'Remove')
        button.type = 'submit'
        button.removeForm = form
        button.onclick = function (e) {
            // preventDefault to submit the form without leaving the page
            e.preventDefault()
            if (confirm('Delete this item?')) {
                let formData = new FormData(this.removeForm)
                let xhr = new XMLHttpRequest()
                // Post
                xhr.open('GET', this.removeForm.action, true)
                xhr.responseType = 'text'
                xhr.onload = function() {
                    if (this.status == 200) {
                        let status = this.getResponseHeader('Query-Status')
                        if (status == 'OK') {
                            window.location.reload()
                        } else {
                            alert('Query failed: ' + status)
                        }
                    } else {
                        alert('Request failed: ' + this.statusText)
                    }
                }
                // Send
                xhr.send(formData)
            }
        }
        form.appendChild(button)
        return form
    }
}
