/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2022 Charles E. Vejnar
*/

import { TableForm } from '../tableform.js';

export { MutantTableForm }

class MutantTableForm extends TableForm {
    fillForm(queryArgs) {
        // Add parent ID
        for (let i=0, leni=this.inputs.length; i<leni; i++) {
            for (let [column, input] of form.inputs[i]) {
                if (column == queryArgs['parent_record_level']) {
                    input.initValue(queryArgs['parent_record_id'])
                }
            }
        }
    }
}
