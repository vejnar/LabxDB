/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { createElement, joinURLs, removeChildren } from './utils.js'
import { Input } from './widget/input.js'

export { Form }

class Form {
    getOptions() {
        let form = this
        return new Promise(function(resolve, reject) {
            let formData = new FormData()
            formData.set('sort_criterion', '0 group_name ASC')
            formData.append('sort_criterion', '0 option ASC')
            formData.set('limit', 'ALL')

            let xhr = new XMLHttpRequest()
            xhr.open('POST', joinURLs([form.baseURL, form.name, 'option']), true)
            xhr.responseType = 'json'
            xhr.onload = function() {
                if (this.status == 200) {
                    let status = this.getResponseHeader('Query-Status')
                    if (status == 'OK') {
                        // Save options
                        form.options = this.response
                        resolve(form)
                    } else {
                        reject(Error('Query failed: ' + status))
                    }
                } else {
                    alert('Request failed: ' + this.statusText)
                    reject(Error(xhr.statusText))
                }
            }
            // Send
            xhr.send(formData)
        })
    }

    getAddOption(column) {
        let button = createElement('BUTTON', 'button', '+')
        button.Form = this
        button.column = column
        button.onclick = function (e) { this.Form.addOption(this.column) }
        return button
    }

    appendCancelButton(container) {
        let cancelButton = createElement('BUTTON', 'button', 'Cancel')
        cancelButton.Form = this
        cancelButton.onclick = function (e) { window.location.href = this.Form.getReferrerURL() }
        container.appendChild(cancelButton)
    }

    appendControlButton(container) {
        // Cancel
        this.appendCancelButton(container)
        // Submit
        let submitButton = createElement('BUTTON', 'button', 'Submit')
        submitButton.Form = this
        submitButton.onclick = function (e) { this.Form.submitForm() }
        container.appendChild(submitButton)
    }

    getReferrerURL() {
        if (this.referrer.length == 0) {
            return window.location.origin
        } else {
            let url = new URL(this.referrer)
            let newHref = url.origin + url.pathname
            if (this.referrerParams !== undefined && this.referrerParams.length > 0) {
                let params = new URLSearchParams(this.referrerParams)
                newHref += '?' + params.toString()
            }
            if (this.queryArgs['record_id'] !== undefined) {
                newHref += '#' + this.queryArgs['record_id']
            }
            return newHref
        }
    }

    submitForm(action) {
        let data = this.prepareData()
        if (data != null) {
            // Send data
            let xhr = new XMLHttpRequest()
            xhr.form = this
            xhr.open('POST', '', true)
            xhr.responseType = 'json'
            xhr.onload = function() {
                if (this.status == 200) {
                    let status = this.getResponseHeader('Query-Status')
                    if (status == 'OK') {
                        // Redirect
                        if (action === undefined || action == 'redirect') {
                            window.location.href = this.form.getReferrerURL()
                        // Reload
                        } else if (action == 'reload') {
                            window.location.reload()
                        }
                    } else {
                        alert('Query failed: ' + status)
                    }
                } else {
                    alert('Request failed: ' + this.statusText)
                }
            }
            // Send
            xhr.send(JSON.stringify(data))
        }
    }

    addOption(column) {
        // Toggle modal on
        this.toggleModal('on')
        // Add dialog
        this.loadFrameOption(column, 'New option')
    }

    toggleModal(toggle) {
        if (typeof toggle == 'undefined') {
            if (this.domModal.style.opacity == '1') {
                toggle = 'off'
            } else {
                toggle = 'on'
            }
        }
        if (toggle == 'on') {
            this.domModal.style.opacity = '1'
            this.domModal.style.pointerEvents = 'auto'
        } else {
            this.domModal.style.opacity = '0'
            this.domModal.style.pointerEvents = 'none'
        }
    }

    loadFrameOption(column, label) {
        removeChildren(this.domModalWindow)
        this.domModalWindow.appendChild(createElement('DIV', 'tooltip', label))
        let input = new Input({'name':column, 'required':true})
        this.domModalWindow.appendChild(input.dom)
        // Cancel
        let cancel = createElement('BUTTON', 'button', 'Cancel')
        cancel.Form = this
        cancel.onclick = function (e) { this.Form.toggleModal('off') }
        this.domModalWindow.appendChild(cancel)
        // Submit
        let submit = createElement('BUTTON', 'button', 'Submit')
        submit.Form = this
        submit.column = column
        submit.input = input
        submit.onclick = function (e) { if (this.input.reportValidity()) { this.Form.submitAddOption(this.column, this.input.getValue()) } }
        this.domModalWindow.appendChild(submit)
    }

    submitAddOption(column, newOption) {
        let data = [{'group_name':column['name'], 'option':newOption}]

        // Send data
        let xhr = new XMLHttpRequest()
        xhr.form = this
        xhr.open('POST', joinURLs([form.baseURL, this.name, 'option', 'new']), true)
        xhr.responseType = 'json'
        xhr.onload = function() {
            if (this.status == 200) {
                let status = this.getResponseHeader('Query-Status')
                if (status == 'OK') {
                    // Add new option
                    for (let i=0, leni=this.form.inputs.length; i<leni; i++) {
                        for (let [column, input] of this.form.inputs[i]) {
                            if (column == data[0]['group_name']) {
                                input.addOption({value:data[0]['option'], first:true})
                            }
                        }
                    }
                    // Reset modal
                    this.form.toggleModal('off')
                } else {
                    alert('Query failed: ' + status)
                }
            } else {
                alert('Request failed: ' + this.statusText)
            }
        }
        // Send
        xhr.send(JSON.stringify(data))
    }

    parseCriterion(paramsString) {
        let urlParams = new URLSearchParams(paramsString)
        let params = urlParams.getAll('search_criterion').map(element => ['search_criterion', element]) 
        params = params.concat(urlParams.getAll('sort_criterion').map(element => ['sort_criterion', element]))
        params = params.concat(urlParams.getAll('limit').map(element => ['limit', element]))
        return params
    }
}
