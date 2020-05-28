/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { createElement } from './utils.js'
import { Board } from './board.js'

export { Table }

class Table extends Board {
    constructor(dom, domLoader, columns, columnInfos, level, levelInfos, baseURL) {
        super()
        this.dom = dom
        this.body = dom.tBodies[0]
        this.domLoader = domLoader
        this.columns = columns
        this.columnInfos = columnInfos
        this.level = level
        this.levelInfos = levelInfos
        this.baseURL = baseURL

        this.initHeader()
    }

    initHeader() {
        let row = document.createElement('TR')
        row.className = 'shtable-header'
        for (let i=0, leni=this.columns.length; i<leni; i++) {
            let el = createElement('TH', undefined, this.columnInfos[this.columns[i]['name']]['label'])
            row.appendChild(el)
        }
        // Add control header
        let el = document.createElement('TH')
        row.appendChild(el)
        this.dom.tHead.appendChild(row)
    }

    addContent(response) {
        // Add row
        let newLines = document.createDocumentFragment()
        for (let i=0, leni=response.length; i<leni; i++) {
            let row = document.createElement('TR')
            // Add content cell(s)
            for (let j=0, lenj=this.columns.length; j<lenj; j++) {
                let el = document.createElement('TD')
                // Add anchor
                if (j == 0) {
                    let anchor = document.createElement('SPAN')
                    anchor.className = 'anchor'
                    anchor.id = response[i][this.levelInfos['column_id']]
                    el.appendChild(anchor)
                }
                // Add content
                let content = this.toHuman(response[i][this.columns[j]['name']])
                if (typeof content === 'string' && content.startsWith('data:image')) {
                    let cell = createElement('DIV', 'tooltip', '▣')
                    let tooltip = createElement('SPAN', 'tooltipimg', undefined)
                    // Add image
                    let image = new Image()
                    image.src = content
                    tooltip.appendChild(image)
                    // Add tooltip
                    cell.appendChild(tooltip)
                    el.appendChild(cell)
                } else if (content.length > 15) { // CSS max-width is 20em
                    let cell = createElement('DIV', 'cell', content)
                    el.appendChild(cell)
                } else {
                    el.appendChild(document.createTextNode(content))
                }
                // Add to row
                row.appendChild(el)
            }
            // Add control cell
            let el = this.getControlCell(response[i])
            row.appendChild(el)
            // Add to lines
            newLines.appendChild(row)
        }
        this.body.appendChild(newLines)
    }

    getControlCell(record) {
        let cts = this.getControlElements(record)
        let cell = document.createElement('TD')
        for (let i=0, leni=cts.length; i<leni; i++) {
            cell.appendChild(cts[i])
        }
        return cell
    }

    getControlDuplicate(record) {
        // Duplicate
        let form = document.createElement('FORM')
        form.method = 'get'
        form.action = this.getActionURL('new')
        let input = document.createElement('INPUT')
        input.name = 'record_id'
        input.type = 'hidden'
        input.value = record[this.levelInfos['column_id']]
        form.appendChild(input)
        let button = createElement('BUTTON', 'button', 'Duplicate')
        button.type = 'submit'
        form.appendChild(button)
        return form
    }

    getControlElements(record) {
        let cts = []
        cts.push(this.getControlEdit(record))
        cts.push(this.getControlRemove(record))
        return cts
    }
}
