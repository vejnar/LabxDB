/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright © 2018 Charles E. Vejnar
*/

export { SelectOption }

class SelectOption {
    constructor(args, options, dom) {
        if (dom === undefined) {
            this.dom = document.createElement('SELECT')
        } else {
            this.dom = dom
        }
        // Attributes
        if ('always_export' in args) {
            this.alwaysExport = args['always_export']
        } else {
            this.alwaysExport = false
        }
        if (options === undefined) {
            this.options = []
        } else {
            this.options = options
        }
        if ('search_type' in args) {
            this.castType = args['search_type']
        }
        // DOM attributes
        if ('name' in args) {
            this.dom.name = args['name']
        }
        if ('required' in args) {
            this.dom.required = args['required']
        }
        // Option
        let option = document.createElement('OPTION')
        option.rawValue = null
        option.textContent = 'None'
        // If option is required then None is not a valid option
        if ('required' in args && args['required']) {
            option.value = ''
        }
        this.dom.appendChild(option)
        // Add type option
        for (let i=0, leni=this.options.length; i<leni; i++) {
            if (this.options[i]['group_name'] == this.dom.name) {
                let value = this.options[i]['option']
                if ('optionValue' in this.options[i]) {
                    value = this.options[i]['optionValue']
                }
                this.addOption({value:value, textContent:this.options[i]['option']})
            }
        }
    }

    initValue(value) {
        this.setValue(value)
        this.remoteValue = value
    }

    setValue(value) {
        let options = this.dom.getElementsByTagName('OPTION')
        for (let i=0, leni=options.length; i<leni; i++) {
            if (options[i].rawValue == value) {
                options[i].selected = true
            }
        }
    }

    getValue() {
        let value = this.dom.options[this.dom.selectedIndex].rawValue
        if (value !== null && this.castType !== undefined && this.castType == 'equal_number') {
            value = Number(value)
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
    
    //addOption(value, first=false) {
    addOption({value, textContent=null, first=false} = {}) {
        let option = document.createElement('OPTION')
        option.rawValue = value
        if (textContent == null) {
            option.textContent = value
        } else {
            option.textContent = textContent
        }
        if (first) {
            this.dom.insertBefore(option, this.dom.firstChild)
        } else {
            this.dom.appendChild(option)
        }
    }
}
