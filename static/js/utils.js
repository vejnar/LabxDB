/*
 LabxDB: Utils

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://www.mozilla.org/MPL/2.0/.

 Copyright © 2018 Charles E. Vejnar
*/

export { addLoadEvent, createElement, removeElement, removeChildren, replaceChildren, joinURLs, getDate }

function addLoadEvent(func) {
    let oldonload = window.onload
    if (typeof window.onload != 'function') {
        window.onload = func
    } else {
        window.onload = function() {
            if (oldonload) {
                oldonload()
            }
            func()
        }
    }
}

function createElement(type, cls, content) {
    let el = document.createElement(type)
    if (typeof content !== 'undefined') { el.textContent = content }
    if (typeof cls !== 'undefined') { el.className = cls }
    return el
}

function removeElement(el) {
    el.parentNode.removeChild(el)
}

function removeChildren(el) {
    while (el.firstChild) {
        el.removeChild(el.firstChild)
    }
}

function replaceChildren(node, el) {
    removeChildren(node)
    node.appendChild(el)
}

function joinURLs(urls) {
    let furls = ''
    for (let i=0, leni=urls.length-1; i<leni; i++) {
        if (urls[i][urls[i].length-1] == '/') {
            furls += urls[i]
        } else {
            furls += urls[i] + '/'
        }
    }
    furls += urls[urls.length-1]
    return furls
}

function getDate() {
    let today = new Date()
    return today.getFullYear().toString() + '-' + (today.getMonth() + 1).toString().padStart(2, '0') + '-' + today.getDate().toString().padStart(2, '0')
}
