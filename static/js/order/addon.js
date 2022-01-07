/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2022 Charles E. Vejnar
*/

import { getDate } from '../utils.js'

export { addonStart }

function addonStart(op, t, e) {
    let r
    switch (op) {
        case 'init_date':
            r = initDate(t)
            break
        case 'init_status':
            r = initStatus(t)
            break
        case 'order_today_status':
            r = orderTodayStatus(t)
            break
        case 'order_today':
            r = orderToday(t)
            break
        case 'order_total':
            r = orderTotal(t)
            break
        default:
            alert('Unknown operation: '+op)
    }
    return r
}

function initDate(input) {
    return getDate()
}

function initStatus(input) {
    return 'to order'
}

function orderTodayStatus(button) {
    // Get status
    let domStatus
    let domInputs = button.parentNode.parentNode.getElementsByTagName('SELECT')
    for (let i=0, leni=domInputs.length; i<leni; i++) {
        if (domInputs[i].name == 'status') {
            domStatus = domInputs[i]
        }
    }
    domStatus.value = 'ordered'
    // Update date
    button.parentNode.getElementsByTagName('INPUT')[0].value = getDate()
}

function orderToday(button) {
    // Update date
    button.parentNode.getElementsByTagName('INPUT')[0].value = getDate()
}

function orderTotal(button) {
    // Get DOM inputs
    let domQuantity, domPrice, domTotal
    let domInputs = button.parentNode.parentNode.getElementsByTagName('INPUT')
    for (let i=0, leni=domInputs.length; i<leni; i++) {
        if (domInputs[i].name == 'quantity') {
            domQuantity = domInputs[i]
        }
        if (domInputs[i].name == 'unit_price') {
            domPrice = domInputs[i]
        }
        if (domInputs[i].name == 'total_price') {
            domTotal = domInputs[i]
        }
    }
    // Update total
    domTotal.value = (domQuantity.value * domPrice.value).toFixed(2)
}
