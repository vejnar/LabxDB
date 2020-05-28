/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { createElement } from './utils.js'
import { Board } from './board.js'

export { TreeBlock }

class TreeBlock extends Board {
    constructor(dom, domToolbar, domLoader, columns, columnInfos, columnTitles, levels, levelInfos, baseURL) {
        super()
        this.dom = dom
        this.body = dom
        this.domToolbar = domToolbar
        this.domLoader = domLoader
        this.columnInfos = columnInfos
        this.columnTitles = columnTitles
        this.levels = levels
        this.levelInfos = levelInfos
        this.baseURL = baseURL

        // Remove duplicate(s) between columns and columnTitles
        this.columns = []
        for (let i=0, leni=levels.length; i<leni; i++) {
            this.columns.push([])
            for (let j=0, lenj=columns[i].length; j<lenj; j++) {
                let column = columns[i][j]
                if (this.columnTitles[i].indexOf(column['name']) == -1) {
                    this.columns[i].push(column)
                }
            }
        }

        // Init toolbar
        this.initToolbar()
    }

    initToolbar() {
        for (let i=0, leni=this.levels.length; i<leni; i++) {
            let button = createElement('BUTTON', 'button', 'Collapse '+this.levelInfos[i]['label'])
            button.board = this
            button.level = i
            button.levelLabel = this.levelInfos[i]['label']
            button.state = 'on'
            button.applyState = function () {
                let children = this.board.dom.getElementsByClassName('record-row-control')
                for (let i=0, leni=children.length; i<leni; i++) {
                    if (this.state != children[i].state && children[i].classList.contains('level'+this.level)) {
                        children[i].click()
                    }
                }
            }
            button.onclick = function (e) {
                if (this.state == 'on') {
                    this.state = 'off'
                    this.textContent = 'Expand ' + this.levelLabel
                } else {
                    this.state = 'on'
                    this.textContent = 'Collapse ' + this.levelLabel
                }
                this.applyState()
            }
            this.domToolbar.appendChild(button)
        }
    }

    applyCollapseExpand() {
        for (let i=0, leni=this.domToolbar.children.length; i<leni; i++) {
            this.domToolbar.children[i].applyState()
        }
    }

    addContentImperative(response) {
        let newLines = document.createDocumentFragment()
        for (let i=0, leni=response.length; i<leni; i++) {
            let a = response[i]
            let block = createElement('DIV', 'record-block', undefined)
            this.addRows(a, 0, block)
            if ('children' in a) {
                for (let j=0, lenj=a['children'].length; j<lenj; j++) {
                    let b = a['children'][j]
                    this.addRows(b, 1, block)
                    if ('children' in b) {
                        for (let k=0, lenk=b['children'].length; k<lenk; k++) {
                            let c = b['children'][k]
                            this.addRows(c, 2, block)
                        }
                    }
                }
            }
            newLines.appendChild(block)
        }
        this.body.appendChild(newLines)
    }

    addRows(response, level, block) {
        let row = createElement('DIV', 'record-row level'+level, undefined)
        for (let j=0, lenj=this.columns[level].length; j<lenj; j++) {
            let cell = createElement('DIV', 'record-cell', undefined)
            let colName = this.columns[level][j]['name']
            cell.appendChild(createElement('DIV', 'record-cell-title', this.columnInfos[level][colName]['label']))
            cell.appendChild(createElement('DIV', 'cell', this.toHuman(response[colName])))
            row.appendChild(cell)
        }
        block.appendChild(row)
    }

    addContent(response) {
        let newLines = document.createDocumentFragment()
        this.getRows(response, newLines, 0)
        this.body.appendChild(newLines)
        this.applyCollapseExpand()
    }

    getRows(response, parentBlock, level) {
        for (let i=0, leni=response.length; i<leni; i++) {
            // New block
            let block = createElement('DIV', 'record-block level'+level, undefined)
            // New row
            let row = createElement('DIV', 'record-row-container level'+level, undefined)
            // Expand/Collapse button
            let control = createElement('DIV', 'record-row-control level'+level, '▼')
            control.state = 'on'
            control.onclick = function (e) {
                let display
                if (this.state == 'on') {
                    this.style.transform = 'rotate(-90deg)'
                    this.state = 'off'
                    display = 'none'
                } else {
                    this.style.transform = ''
                    this.state = 'on'
                    display = ''
                }
                // Hide the data for the current level
                let children = this.parentNode.childNodes
                for (let i=0, leni=children.length; i<leni; i++) {
                    if (children[i].classList.contains('data')) {
                        children[i].style.display = display
                    }
                }
                // Hide sub-levels
                children = this.parentNode.parentNode.childNodes
                for (let i=0, leni=children.length; i<leni; i++) {
                    if (children[i].classList.contains('record-block')) {
                        children[i].style.display = display
                    }
                }
            }
            row.appendChild(control)
            // Toolbar
            let toolbar = createElement('DIV', 'record-row toolbar level'+level, undefined)
            // Title
            let titles = []
            for (let j=0, lenj=this.columnTitles[level].length; j<lenj; j++) {
                titles.push(response[i][this.columnTitles[level][j]])
            }
            toolbar.appendChild(createElement('DIV', 'toolbar-head', titles.join(' - ')))
            // Add control cell
            let el = this.getControlCell(response[i], level)
            toolbar.appendChild(el)
            toolbar.level = level
            row.appendChild(toolbar)

            // Data
            let rowData = createElement('DIV', 'record-row data level'+level, undefined)
            // Add content cell(s)
            for (let j=0, lenj=this.columns[level].length; j<lenj; j++) {
                let cell = createElement('DIV', 'record-cell', undefined)
                let colName = this.columns[level][j]['name']
                cell.appendChild(createElement('DIV', 'record-cell-title', this.columnInfos[level][colName]['label']))
                cell.appendChild(createElement('DIV', 'cell', this.toHuman(response[i][colName])))
                rowData.appendChild(cell)
            }
            row.appendChild(rowData)
            block.appendChild(row)
            
            // Add new block to parent block
            parentBlock.appendChild(block)

            // Recursive call using current block as parent
            if ('children' in response[i] && response[i]['children'] != null) {
                this.getRows(response[i]['children'], block, level + 1)
            }
        }
    }

    getControlCell(record, level) {
        let cts = this.getControlElements(record, level)
        let cell = document.createElement('DIV')
        for (let i=0, leni=cts.length; i<leni; i++) {
            cell.appendChild(cts[i])
        }
        return cell
    }

    getControlElements(record, level) {
        let cts = []
        cts.push(this.getControlEdit(record, level))
        cts.push(this.getControlRemove(record, level))
        return cts
    }
}
