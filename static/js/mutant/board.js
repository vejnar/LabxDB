/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { TreeBlock } from '../treeblock.js';
import { createElement, joinURLs } from '../utils.js'
import { Input } from '../widget/input.js';

export { MutantTreeBlock }

class MutantTreeBlock extends TreeBlock {
    getControlAdd(record, level) {
        // Add level+1
        let form = document.createElement('FORM')
        form.method = 'get'
        form.action = joinURLs([this.baseURL, this.levelInfos[level+1]['url'], 'new'])
        // Record ID
        let input = new Input({'name':'parent_record_id', 'gui_type':'hidden'})
        input.initValue(record[this.levelInfos[level]['column_id']])
        form.appendChild(input.dom)
        // Level record name
        input = new Input({'name':'parent_record_level', 'gui_type':'hidden'})
        input.initValue(this.levelInfos[level]['column_id'])
        form.appendChild(input.dom)
        // Button
        let button = createElement('BUTTON', 'button', 'Add ' + this.levelInfos[level+1]['label'])
        button.type = 'submit'
        form.appendChild(button)
        return form
    }

    getControlElements(record, level) {
        let cts = []
        // Add level+1
        if (level < this.levelInfos.length - 1) {
            cts.push(this.getControlAdd(record, level))
        }
        // Edit and Remove
        cts.push(this.getControlEdit(record, level))
        cts.push(this.getControlRemove(record, level))
        // Return
        return cts
    }
}
