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
        case 'init_custom':
            r = initCustom(t)
            break
        case 'received_today':
            r = receivedToday(t)
            break
        default:
            alert('Unknown operation: '+op)
    }
    return r
}

function initDate(input) {
    return getDate()
}

function initCustom(input) {
    return false
}

function receivedToday(button) {
    // Update date
    button.parentNode.getElementsByTagName('INPUT')[0].value = getDate()
}
