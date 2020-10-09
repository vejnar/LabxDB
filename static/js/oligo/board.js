/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { Table } from '../table.js';
import { createElement, getDate, joinURLs } from '../utils.js'

export { OligoTable }

class OligoTable extends Table {
    getControlElements(record) {
        let cts = []
        // Edit, Remove, and Duplicate
        cts.push(this.getControlEdit(record))
        cts.push(this.getControlRemove(record))
        cts.push(this.getControlDuplicate(record))
        // Ordered
        button = createElement('BUTTON', 'button', 'Ordered')
        button.type = 'submit'
        button.action = joinURLs([this.baseURL, this.levelInfos['url'], 'edit', record[this.levelInfos['column_id']]])
        button.onclick = function (e) {
            let xhr = new XMLHttpRequest()
            // Post
            xhr.open('POST', e.target.action, true)
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
            // Prepare
            let data = [{'status': 'ordered', 'date_order': getDate()}]
            // Send
            xhr.send(JSON.stringify(data))
        }
        cts.push(button)
        // Return
        return cts
    }
}
