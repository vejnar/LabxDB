/*
 LabxDB

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright (C) 2018-2020 Charles E. Vejnar
*/

import { Table } from '../table.js';

export { FishTable }

class FishTable extends Table {
    getControlElements(record) {
        let cts = []
        // Edit, Remove, and Duplicate
        cts.push(this.getControlEdit(record))
        cts.push(this.getControlRemove(record))
        cts.push(this.getControlDuplicate(record))
        // Return
        return cts
    }
}
