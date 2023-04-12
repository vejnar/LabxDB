/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright © 2018 Charles E. Vejnar
*/

export { SelectBool }

class SelectBool {
    constructor(args, dom) {
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
        // DOM attributes
        if ('name' in args) {
            this.dom.name = args['name']
        }
        if ('required' in args) {
            this.dom.required = args['required']
        }
        // Option: None
        let option = document.createElement('OPTION')
        option.rawValue = null
        option.textContent = 'None'
        option.hidden = true
        // If option is required then None is not a valid option
        if ('required' in args && args['required']) {
            option.value = ''
        }
        this.dom.appendChild(option)
        // Option: Yes
        option = document.createElement('OPTION')
        option.rawValue = true
        option.textContent = 'Yes'
        this.dom.appendChild(option)
        // Option: No
        option = document.createElement('OPTION')
        option.rawValue = false
        option.textContent = 'No'
        this.dom.appendChild(option)
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
        return this.dom.options[this.dom.selectedIndex].rawValue
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
