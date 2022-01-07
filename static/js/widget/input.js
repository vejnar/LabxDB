/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2022 Charles E. Vejnar
*/

export { Input }

class Input {
    constructor(args, dom) {
        if (dom === undefined) {
            this.dom = document.createElement('INPUT')
        } else {
            this.dom = dom
        }
        // Attributes
        if ('always_export' in args) {
            this.alwaysExport = args['always_export']
        } else {
            this.alwaysExport = false
        }
        if ('search_type' in args) {
            this.castType = args['search_type']
        }
        // DOM attributes
        if ('gui_type' in args) {
            this.dom.type = args['gui_type']
        } else {
            this.dom.type = 'text'
        }
        if ('name' in args) {
            this.dom.name = args['name']
        }
        if ('spellcheck' in args) {
            this.dom.spellcheck = args['spellcheck']
        } else {
            this.dom.spellcheck = false
        }
        if ('required' in args) {
            this.dom.required = args['required']
        }
        if ('size' in args) {
            this.dom.size = args['size']
        }
        if ('pattern' in args) {
            this.dom.pattern = args['pattern']
        }
        if ('accept' in args) {
            this.dom.accept = args['accept']
        }
    }

    initValue(value) {
        this.setValue(value)
        this.remoteValue = value
    }

    setValue(value) {
        this.dom.value = value
    }

    getValue() {
        let value
        if (this.dom.value.length == 0) {
            value = null
        } else {
            if (value !== null && this.castType !== undefined && this.castType == 'equal_number') {
                value = Number(this.dom.value)
            } else {
                value = this.dom.value
            }
        }
        return value
    }

    hasChanged() {
        if (this.remoteValue === undefined || this.remoteValue != this.getValue()) {
            return true
        } else {
            return false
        }
    }

    addEventListener(type, listener) {
        this.dom.addEventListener(type, listener)
    }

    reportValidity() {
        return this.dom.reportValidity()
    }
}
