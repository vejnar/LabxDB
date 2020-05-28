/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { joinURLs, removeElement } from './utils.js'

export { Toolbar }

function sortSymbol(o) {
    if (o == 'ASC') {
        return '↓'
    } else if (o == 'DESC') {
        return '↑'
    } else {
        return ''
    }
}

class Toolbar {
    constructor(dom, columns, columnInfos, levels, levelInfos, baseURL) {
        this.dom = dom
        this.columns = columns
        this.columnInfos = columnInfos
        this.levels = levels
        this.levelInfos = levelInfos
        this.baseURL = baseURL

        this.initNew()
        this.initSearch()
        this.initSort()
    }

    initNew() {
        if (this.levels.length == 1) {
            let level = this.levels[0]
            let button = document.createElement('A')
            button.className = 'button'
            button.href = joinURLs([this.baseURL, this.levelInfos[level]['url'], 'new'])
            button.textContent = 'Add new ' + this.levelInfos[level]['label']
            document.getElementById('new_record').appendChild(button)
        }
    }

    initSearch() {
        let search = document.getElementById('search_column')
        if (this.levels.length == 1) {
            this.addSearchOptions(search, this.columns[this.levels[0]], this.columnInfos[this.levels[0]], this.levels[0])
        } else {
            for (let i=0, leni=this.levels.length; i<leni; i++) {
                let group = document.createElement('OPTGROUP')
                group.label = this.levelInfos[i]['label']
                this.addSearchOptions(group, this.columns[i], this.columnInfos[i], this.levels[i])
                search.appendChild(group)
            }
        }
    }

    keyPressSearch(event) {
        if (event.key == 'Enter') {
            this.addSearchCriterion()
        }
    }

    addSearchOptions(dom, columns, columnInfos, level) {
        // Option ALL
        let el = document.createElement('OPTION')
        el.textContent = 'All'
        el.value = 'ALL'
        el.levelSearch = level
        dom.appendChild(el)
        // Other option(s)
        for (let i=0, leni=columns.length; i<leni; i++) {
            let el = document.createElement('OPTION')
            el.textContent = columnInfos[columns[i]['name']]['label']
            el.value = columns[i]['name']
            el.levelSearch = level
            dom.appendChild(el)
        }
    }

    initSearchCriterions(criterions) {
        for (let i=0, leni=criterions.length; i<leni; i++) {
            this.addSearchCriterion(criterions[i][0], criterions[i][1], criterions[i][2], criterions[i][3])
        }
    }

    addSearchCriterion(searchLevel, searchColumn, searchType, searchText) {
        // Get search criteria
        let searchLabel
        if (searchColumn == null) {
            let selColumn = document.getElementById('search_column')
            searchColumn = selColumn.value
            searchLabel = selColumn.options[selColumn.selectedIndex].text
            searchLevel = selColumn.options[selColumn.selectedIndex].levelSearch
            searchText = document.getElementById('search_text').value
            searchType = document.getElementById('search_type').value
        } else {
            if (searchColumn == 'ALL') {
                searchLabel = 'ALL'
            } else {
                searchLabel = this.columnInfos[searchLevel][searchColumn]['label']
            }
        }
        // Convert empty searchText to null
        if (searchText.length == 0) {
            searchText = 'null'
        }
        // Prepare new search elements
        let sLabel = document.createElement('DIV')
        sLabel.className = 'button-label'
        if (searchType == 'EQUAL') {
            sLabel.textContent = searchLabel + '='
        } else if (searchType == 'FUZZY') {
            sLabel.textContent = searchLabel + '~'
        }
        let sText = document.createElement('I')
        sText.textContent = searchText
        sLabel.appendChild(sText)
        let sButton = document.createElement('BUTTON')
        sButton.className = 'button delete delete-symbol'
        sButton.type = 'button'
        sButton.onclick = function (e) { removeElement(this.parentNode) }
        let sInput = document.createElement('INPUT')
        sInput.name = 'search_criterion'
        sInput.type = 'hidden'
        sInput.value = `${searchLevel} ${searchColumn} ${searchType} ${searchText}`
        let sDiv = document.createElement('DIV')
        sDiv.className = 'control-search-sort-criterion'
        // Add label, button and input
        sDiv.appendChild(sLabel)
        sDiv.appendChild(sButton)
        sDiv.appendChild(sInput)
        // Add to main search div
        let mainDiv = document.getElementById('control-search')
        mainDiv.appendChild(sDiv)
    }

    getSearchCriterions() {
        let searchCriterions = []
        let children = document.getElementById('control-search').children
        for (let i=0, leni=children.length; i<leni; i++) {
            let els = children[i].getElementsByTagName('INPUT')
            for (let j=0, lenj=els.length; j<lenj; j++) {
                if (els[j].name == 'search_criterion') {
                    searchCriterions.push(els[j].value)
                }
            }
        }
        return searchCriterions
    }

    initSort() {
        let sort = document.getElementById('sort_column')
        if (this.levels.length == 1) {
            this.addSortOptions(sort, this.columns[this.levels[0]], this.columnInfos[this.levels[0]], this.levels[0])
        } else {
            for (let i=0, leni=this.levels.length; i<leni; i++) {
                let group = document.createElement('OPTGROUP')
                group.label = this.levelInfos[i]['label']
                this.addSortOptions(group, this.columns[i], this.columnInfos[i], this.levels[i])
                sort.appendChild(group)
            }
        }
    }

    addSortOptions(dom, columns, columnInfos, level) {
        for (let i=0, leni=columns.length; i<leni; i++) {
            let el = document.createElement('OPTION')
            el.textContent = columnInfos[columns[i]['name']]['label']
            el.value = columns[i]['name']
            el.levelSort = level
            dom.appendChild(el)
        }
    }

    initSortCriterions(criterions) {
        for (let i=0, leni=criterions.length; i<leni; i++) {
            this.addSortCriterion(criterions[i][0], criterions[i][1], criterions[i][2], criterions[i][3])
        }
    }
    
    addSortCriterion(sortLevel, sortColumn, sortOrder, sortLabel) {
        // Get sort criteria
        if (sortColumn == null) {
            let selColumn = document.getElementById('sort_column')
            sortColumn = selColumn.value
            sortOrder = document.getElementById('sort_order').value
            sortLabel = selColumn.options[selColumn.selectedIndex].text
            sortLevel = selColumn.options[selColumn.selectedIndex].levelSort
        }
        // Prepare new sort elements
        let sLabel = document.createElement('DIV')
        sLabel.className = 'button-label'
        sLabel.textContent = `${sortSymbol(sortOrder)} ${sortLabel} `
        let sButton = document.createElement('BUTTON')
        sButton.className = 'button delete delete-symbol'
        sButton.type = 'button'
        sButton.onclick = function (e) { removeElement(this.parentNode) }
        let sInput = document.createElement('INPUT')
        sInput.name = 'sort_criterion'
        sInput.type = 'hidden'
        sInput.value = `${sortLevel} ${sortColumn} ${sortOrder} ${sortLabel}`
        let sDiv = document.createElement('DIV')
        sDiv.className = 'control-search-sort-criterion'

        sDiv.appendChild(sLabel)
        sDiv.appendChild(sButton)
        sDiv.appendChild(sInput)
        // Add to main sort div
        let mainDiv = document.getElementById('control-sort')
        mainDiv.appendChild(sDiv)
    }

    getSortCriterions() {
        let sortCriterions = []
        let children = document.getElementById('control-sort').children
        for (let i=0, leni=children.length; i<leni; i++) {
            let els = children[i].getElementsByTagName('INPUT')
            for (let j=0, lenj=els.length; j<lenj; j++) {
                if (els[j].name == 'sort_criterion') {
                    sortCriterions.push(els[j].value)
                }
            }
        }
        return sortCriterions
    }

    initLimit(limits) {
        let limit = document.getElementById('limit')
        for (let i=0, leni=limits.length; i<leni; i++) {
            let el = document.createElement('OPTION')
            el.textContent = limits[i][0]
            el.value = limits[i][1]
            if (limits[i][2]) {
                el.selected = true
            }
            limit.appendChild(el)
        }
    }

    getLimit() {
        return document.getElementById('limit').value
    }
}
