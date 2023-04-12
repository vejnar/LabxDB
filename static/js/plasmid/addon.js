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
        case 'plasmid_filename':
            r = plasmidFilename(t)
            break
        case 'plasmid_today':
            r = plasmidToday(t)
            break
        default:
            alert('Unknown operation: '+op)
    }
    return r
}

function initDate(input) {
    return getDate()
}

function plasmidToday(button) {
    button.parentNode.getElementsByTagName('INPUT')[0].value = getDate()
}

function plasmidFilename(button) {
    // Plasmid number
    let plasmidNumber = button.Form.remoteData['plasmid_number']
    // Get name
    let domName
    let domInputs = button.parentNode.parentNode.getElementsByTagName('INPUT')
    for (let i=0, leni=domInputs.length; i<leni; i++) {
        if (domInputs[i].name == 'name') {
            domName = domInputs[i]
        }
    }
    // Prepare filename
    let name = domName.value
    name = name.replace(/\s/g, '_')
    name = name.replace(/[^A-Za-z0-9._-]/g, '')
    name = `${plasmidNumber}_${name}.dna`

    button.parentNode.getElementsByTagName('INPUT')[0].value = name
}
