
/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

export { Textarea }

class Textarea {
    constructor(args, dom) {
        if (dom === undefined) {
            this.dom = document.createElement('TEXTAREA')
        } else {
            this.dom = dom
        }
        // Attributes
        if ('always_export' in args) {
            this.alwaysExport = args['always_export']
        } else {
            this.alwaysExport = false
        }
        // DOM attributes
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
        if ('class' in args) {
            this.dom.className = args['class']
        }
        if ('maxlength' in args) {
            this.dom.maxLength = args['maxlength']
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
            value = this.dom.value
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
