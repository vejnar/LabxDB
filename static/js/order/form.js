/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright © 2018 Charles E. Vejnar
*/

import { TableForm } from '../tableform.js';
import { getDate } from '../utils.js'

export { OrderTableForm }

class OrderTableForm extends TableForm {
    postFillForm(queryArgs) {
        return new Promise(function(resolve, reject) {
            // Only if record is set, e.g. Duplicate form
            if (queryArgs['record_id'] !== undefined) {
                for (let [column, input] of form.inputs[0]) {
                    if (column == 'date_insert') {
                        input.setValue(getDate())
                    }
                    if (column == 'status') {
                        input.setValue('to order')
                    }
                    if (column == 'date_order') {
                        input.setValue(null)
                    }
                }
            }
            resolve()
        })
    }
}
