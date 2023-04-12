/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright © 2018 Charles E. Vejnar
*/

import { getDate } from '../utils.js'

export { addonStart }

function addonStart(op, t, e) {
    let r
    switch (op) {
        case 'init_date':
            r = initDate(t)
            break
        case 'fish_today':
            r = fishToday(t)
            break
        default:
            alert('Unknown operation: '+op)
    }
    return r
}

function initDate(input) {
    return getDate()
}

function fishToday(button) {
    button.parentNode.getElementsByTagName('INPUT')[0].value = getDate()
}
