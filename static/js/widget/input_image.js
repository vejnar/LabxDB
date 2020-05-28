/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { createElement } from '../utils.js'

export { InputImage }

class InputImage {
    constructor(args, dom, domInput, domPreview) {
        if (domInput === undefined) {
            // Create container
            this.dom = document.createElement('DIV')
            // Add input
            this.domInput = document.createElement('INPUT')
            this.dom.appendChild(this.domInput)
            // Add removal button
            this.domButton = createElement('BUTTON', 'button', 'Remove image')
            this.domButton.Input = this
            this.domButton.onclick = function (e) {
                let input = this.Input
                // Remove nodes in preview
                while (input.domPreview.firstChild) {
                    input.domPreview.removeChild(input.domPreview.firstChild)
                }
                // Reset image
                input.domImage = null
                // Set required parameter (since image was removed)
                input.domInput.required = input.required
            }
            this.dom.appendChild(this.domButton)
            // Add preview
            this.domPreview = document.createElement('DIV')
            this.dom.appendChild(this.domPreview)
        } else {
            this.dom = dom
            this.domInput = domInput
            this.domPreview = domPreview
        }
        // Attributes
        if ('always_export' in args) {
            this.alwaysExport = args['always_export']
        } else {
            this.alwaysExport = false
        }
        if ('maxsize' in args) {
            this.maxsize = args['maxsize']
        } else {
            this.maxsize = null
        }
        this.domImage = null
        // DOM attributes
        if ('gui_type' in args) {
            this.domInput.type = args['gui_type']
        } else {
            this.domInput.type = 'file'
        }
        if ('name' in args) {
            this.domInput.name = args['name']
        }
        if ('required' in args) {
            this.domInput.required = args['required']
            // Save original required value
            this.required = args['required']
        } else {
            this.required = false
        }
        if ('accept' in args) {
            this.domInput.accept = args['accept']
        }
        // Events
        this.domInput.Input = this
        this.domInput.onchange = function (e) {
            let input = this.Input
            // Remove nodes in preview
            while (input.domPreview.firstChild) {
                input.domPreview.removeChild(input.domPreview.firstChild)
            }
            // Add image
            let curFiles = input.domInput.files
            if (curFiles.length == 1) {
                let curFile = curFiles[0]
                if (input.maxsize == null || curFile.size <= input.maxsize) {
                    if (curFile.type == 'image/png') {
                        // Add image to preview
                        input.domImage = document.createElement('img')
                        input.domPreview.appendChild(input.domImage)
                        // Read image
                        let reader = new FileReader()
                        reader.addEventListener('loadend', function () {
                            input.domImage.src = this.result
                        }, false)
                        reader.readAsDataURL(curFile)
                    } else {
                        input.domPreview.textContent = 'File is not a PNG'
                        input.value = ''
                    }
                } else {
                    input.domPreview.textContent = 'File is too large (Max 2MiB)'
                    input.value = ''
                }
            }
        }
    }

    initValue(value) {
        this.setValue(value)
        this.remoteValue = value
    }
    
    setValue(value) {
        if (value !== null) {
            // Add image
            this.domImage = document.createElement('img')
            this.domImage.src = value
            this.domPreview.appendChild(this.domImage)
            // Remove required parameter (since image is present)
            this.domInput.required = false
        }
    }

    getValue() {
        let value
        if (this.domImage == null || this.domImage.complete == false) {
            value = null
        } else {
            value = this.domImage.src
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
        this.domInput.addEventListener(type, listener)
    }

    reportValidity() {
        return this.domInput.reportValidity()
    }
}
