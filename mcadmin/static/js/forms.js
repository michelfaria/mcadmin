// mcadmin/static/js/forms.js

var FormsJs = {};

FormsJs.REGISTERED = 'formsjs-registered';
FormsJs.VALID = 'formsjs-valid';
FormsJs.INVALID = 'formsjs-invalid';
FormsJs.DIRTY = 'formsjs-dirty';
FormsJs.ERRMSG_SEPARATOR = ';';

/**
 * @callback InputEventCallback
 * @param {HTMLInputElement} el
 * @returns void
 */

/**
 * @param {HTMLFormElement} form - Form to be handled by this utility
 * @param {InputEventCallback?} onInvalid
 * @param {InputEventCallback?} onValid
 */
FormsJs.register = function (form, onInvalid, onValid) {
    [].forEach.call(form.elements, function (el) {
        if (el.classList.contains(FormsJs.REGISTERED)) {
            return; // Field already registered
        }

        el.classList.add(FormsJs.REGISTERED);

        if (el.tagName.toLowerCase() === 'input') {
            el.addEventListener('input', function (ev) {
                FormsJs._onInput.apply(this, [ev]);
            });

            el.addEventListener('focusout', function (ev) {
                FormsJs._onFocusOut.apply(this, [ev, onValid]);
            });

            el.addEventListener('invalid', function (ev) {
                FormsJs._onInvalid.apply(this, [ev, onInvalid]);
            });
        }
    });
};

/**
 * @this {HTMLInputElement}
 * @param {InputEvent} ev
 * @private
 */
FormsJs._onInput = function (ev) {
    this.classList.add(FormsJs.DIRTY);
};

/**
 * @this {HTMLInputElement}
 * @param {FocusEvent} ev
 * @param {InputEventCallback?} onValid
 * @private
 */
FormsJs._onFocusOut = function (ev, onValid) {
    if (this.classList.contains(FormsJs.DIRTY)) {
        if (this.checkValidity()) {

            this.classList.add(FormsJs.VALID);
            this.classList.remove(FormsJs.INVALID);

            if (onValid) {
                onValid(this);
            }
        }
    }
};

/**
 * @this {HTMLInputElement}
 * @param {Event} ev
 * @param {InputEventCallback?} cb
 * @private
 */
FormsJs._onInvalid = function (ev, cb) {
    this.classList.add(FormsJs.INVALID);
    this.classList.remove(FormsJs.VALID);

    var messages = [];

    for (var prop in this.validity) {
        if (this.validity[prop] === true) {
            messages.push(this.dataset[prop]);
        }
    }

    this.dataset.validityMessages = messages.join(FormsJs.ERRMSG_SEPARATOR);

    if (cb) {
        cb(this);
    }
};
