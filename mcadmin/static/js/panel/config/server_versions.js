var versionPickerSelect;
var useSnapshotCheckbox;
var useCustomCheckbox;
var jarInputInput;

(function () {
    versionPickerSelect = document.getElementById('version-picker');
    useSnapshotCheckbox = document.getElementById('use-snapshot');
    useCustomCheckbox = document.getElementById('use-custom');
    jarInputInput = document.getElementById('jar-input');

    versionPickerSelect.addEventListener('change', onVersionPickerSelectChange);
    useSnapshotCheckbox.addEventListener('change', onUseSnapshotCheckboxChange);
    useCustomCheckbox.addEventListener('change', onUseCustomCheckboxChange);
    jarInputInput.addEventListener('change', onJarInputInputChange);
})();

/**
 * @this HTMLSelectElement
 * @param {Event} ev
 */
function onVersionPickerSelectChange(ev) {
    jarInputInput.value = versionPickerSelect.value;
}

/**
 * @this HTMLInputElement
 * @param {Event} ev
 */
function onJarInputInputChange(ev) {
    resetVersionPicker();
}

function setVisibilityByClass(klazz, visible) {
    var els = document.getElementsByClassName(klazz);
    for (var el of els) {
        if (visible) {
            el.classList.remove(HIDDEN);
        } else {
            el.classList.add(HIDDEN);
        }
    }
}

/**
 * @this HTMLInputElement
 * @param {Event} ev
 */
function onUseSnapshotCheckboxChange(ev) {
    resetVersionPicker();
    setVisibilityByClass('stable-version', !this.checked);
    setVisibilityByClass('snapshot-version', this.checked);
}

/**
 * @this HTMLInputElement
 * @param {Event} ev
 */
function onUseCustomCheckboxChange(ev) {
    setVisibilityByClass('version-picker', !this.checked);
    setVisibilityByClass('use-snapshot', !this.checked);
    setVisibilityByClass('jar-input', this.checked);
}

function resetVersionPicker() {
    versionPickerSelect.selectedIndex = 0;
}