/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { Table } from '../table.js';
import { createElement, joinURLs } from '../utils.js'

export { SeqProjectTable }

class SeqProjectTable extends Table {
    getControlFullEdit(record) {
        // Edit form
        let form = document.createElement('FORM')
        form.method = 'get'
        form.action = joinURLs([this.baseURL, this.levelInfos['url'], 'fulledit', record[this.levelInfos['column_id']]])
        let button = createElement('BUTTON', 'button', 'Full edit')
        button.type = 'submit'
        form.appendChild(button)
        return form
    }

    getControlTreeView(record) {
        // Edit form
        let form = document.createElement('FORM')
        form.method = 'get'
        form.action = joinURLs([this.baseURL, 'seq/tree'])
        // Input
        let cref = this.levelInfos['column_ref']
        let input = document.createElement('INPUT')
        input.type = 'hidden'
        input.name = 'search_criterion'
        input.value = `${this.level} ${cref} EQUAL ${record[cref]}`
        form.appendChild(input)
        // Button
        let button = createElement('BUTTON', 'button', 'Tree view')
        button.type = 'submit'
        form.appendChild(button)
        return form
    }

    getControlElements(record) {
        let cts = []
        // Edit and Remove
        cts.push(this.getControlEdit(record))
        cts.push(this.getControlRemove(record))
        // Edit full project
        cts.push(this.getControlFullEdit(record))
        // View tree project
        cts.push(this.getControlTreeView(record))
        return cts
    }
}
