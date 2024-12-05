// Функции управления состоянием элементов формы
export function updateDatabaseOptions() {
    const selectedOS = document.querySelector('input[name="ostype"]:checked');
    const selectedOSValue = selectedOS ? selectedOS.value : null;
    const postgresRadio = document.getElementById('postgres');
    const mssqlRadio = document.getElementById('mssql');

    if (selectedOSValue === 'Linux') {
        mssqlRadio.disabled = true;
        postgresRadio.disabled = false;
        if (!postgresRadio.checked) {
            postgresRadio.checked = true;
        }
    } else if (selectedOSValue === 'Windows') {
        postgresRadio.disabled = true;
        mssqlRadio.disabled = false;
        if (!mssqlRadio.checked) {
            mssqlRadio.checked = true;
        }
    } else {
        postgresRadio.disabled = false;
        mssqlRadio.disabled = false;
    }
}

export function compareVersions(selected, required) {
    const selectedParts = selected.split('.').map(Number);
    const requiredParts = required.split('.').map(Number);
    for (let i = 0; i < requiredParts.length; i++) {
        if (selectedParts[i] > requiredParts[i]) return 1;
        if (selectedParts[i] < requiredParts[i]) return -1;
    }
    return 0;
}

export function checkVersion(versionSelect, s3Checkbox) {
    const selectedVersion = versionSelect.value;
    if (!selectedVersion) {
        s3Checkbox.disabled = true;
        s3Checkbox.checked = false;
        return;
    }

    const comparison = compareVersions(selectedVersion, '4.11');
    if (comparison >= 0) {
        s3Checkbox.disabled = false;
    } else {
        s3Checkbox.disabled = true;
        s3Checkbox.checked = false;
    }
}

export function checkDCS(dcsCheckbox, dcsInput) {
    if (dcsCheckbox.checked) {
        dcsInput.disabled = false;
    } else {
        dcsInput.disabled = true;
        dcsInput.value = '';
    }
}

export function checkArio(arioCheckbox, arioInput) {
    if (arioCheckbox.checked) {
        arioInput.disabled = false;
    } else {
        arioInput.disabled = true;
        arioInput.value = '';
    }
}