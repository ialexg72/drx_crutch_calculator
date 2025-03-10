// Инициализация всех тултипов на странице
document.addEventListener('DOMContentLoaded', () => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    // Инициализация формы
    initializeForm();
});

// Основная функция инициализации формы
function initializeForm() {
    const form = document.getElementById('surveyForm');
    const versionSelect = document.getElementById('version');
    const s3Checkbox = document.getElementById('s3storage');
    const dcsCheckbox = document.getElementById('dcs');
    const dcsInput = document.getElementById('dcsdochours');
    const arioCheckbox = document.getElementById('ario');
    const arioInput = document.getElementById('ariodocin');
    const osRadios = document.querySelectorAll('input[name="ostype"]');
    const exportBtn = document.getElementById('exportXml');

    // Инициализация состояний
    updateDatabaseOptions();
    checkVersion();
    checkDCS();
    checkArio();
    loadFormData();

    // Добавление обработчиков событий
    form.addEventListener('submit', handleFormSubmit);
    versionSelect.addEventListener('change', checkVersion);
    dcsCheckbox.addEventListener('change', checkDCS);
    arioCheckbox.addEventListener('change', checkArio);
    osRadios.forEach(radio => radio.addEventListener('change', updateDatabaseOptions));
    exportBtn?.addEventListener('click', handleExport);
}

// Обновление опций базы данных
function updateDatabaseOptions() {
    const selectedOS = document.querySelector('input[name="ostype"]:checked');
    const selectedOSValue = selectedOS ? selectedOS.value : null;
    const postgresRadio = document.getElementById('postgres');
    const mssqlRadio = document.getElementById('mssql');
    const kubernetesCheckbox = document.getElementById('kubernetes');

    if (!postgresRadio || !mssqlRadio) return;

    if (selectedOSValue === 'Linux') {
        mssqlRadio.disabled = true;
        postgresRadio.disabled = false;
        postgresRadio.checked = true;
        if (kubernetesCheckbox) {
            kubernetesCheckbox.disabled = false;
        }
    } else if (selectedOSValue === 'Windows') {
        postgresRadio.disabled = true;
        mssqlRadio.disabled = false;
        mssqlRadio.checked = true;
        if (kubernetesCheckbox) {
            kubernetesCheckbox.disabled = true;
            kubernetesCheckbox.checked = false;
        }
    } else {
        postgresRadio.disabled = false;
        mssqlRadio.disabled = false;
        if (kubernetesCheckbox) {
            kubernetesCheckbox.disabled = false;
        }
    }
}

// Сравнение версий
function compareVersions(selected, required) {
    if (!selected || !required) return -1;
    const selectedParts = selected.split('.').map(Number);
    const requiredParts = required.split('.').map(Number);
    
    for (let i = 0; i < requiredParts.length; i++) {
        if (selectedParts[i] > requiredParts[i]) return 1;
        if (selectedParts[i] < requiredParts[i]) return -1;
    }
    return 0;
}

// Проверка версии
function checkVersion() {
    const versionSelect = document.getElementById('version');
    const s3Checkbox = document.getElementById('s3storage');
    const lkusers = document.getElementById('lkusers')
    
    if (!versionSelect || !s3Checkbox || !lkusers) return;

    const selectedVersion = versionSelect.value;

    if (!selectedVersion) {
        s3Checkbox.disabled = true;
        s3Checkbox.checked = false;
        lkusers.disabled = false;
        return;
    }

    const comparison = compareVersions(selectedVersion, '4.11');
    s3Checkbox.disabled = comparison < 0;
    if (comparison < 0) s3Checkbox.checked = false;

    // Отключаем поле lkusers при выборе версии 4.12
    if (selectedVersion === '4.12') {
        lkusers.disabled = true; // Делаем lkusers недоступным
        lkusers.value = 0;
    } else {
        lkusers.disabled = false; // Активируем поле, если выбрана другая версия
    }
}

// Проверка DCS
function checkDCS() {
    const dcsCheckbox = document.getElementById('dcs');
    const dcsInput = document.getElementById('dcsdochours');
    
    if (!dcsCheckbox || !dcsInput) return;

    dcsInput.disabled = !dcsCheckbox.checked;
    if (!dcsCheckbox.checked) {
        dcsInput.value = '0';
    }
}

// Проверка Ario
function checkArio() {
    const arioCheckbox = document.getElementById('ario');
    const arioInput = document.getElementById('ariodocin');
    
    if (!arioCheckbox || !arioInput) return;

    arioInput.disabled = !arioCheckbox.checked;
    if (!arioCheckbox.checked) {
        arioInput.value = '0';
    }
}

// Обработка отправки формы
function handleFormSubmit(e) {
    e.preventDefault();
    
    try {
        const formData = collectFormData();
        localStorage.setItem('surveyData', JSON.stringify(formData));
        showAlert('Данные успешно сохранены!', 'success');
    } catch (error) {
        console.error('Error saving form data:', error);
        showAlert('Ошибка при сохранении данных!', 'danger');
    }
}

// Сбор данных формы
function collectFormData() {
    return {
        organization: document.getElementById('organization')?.value,
        version: document.getElementById('version')?.value,
        kubernetes: document.getElementById('kubernetes')?.checked,
        s3storage: document.getElementById('s3storage')?.checked,
        redundancy: document.getElementById('redundancy')?.checked,
        ansible: document.getElementById('ansible')?.checked,
        test_kontur: document.getElementById('test_kontur')?.checked,
        dev_kontur: document.getElementById('dev_kontur')?.checked,
        monitoring: document.getElementById('monitoring')?.checked,
        ostype: document.querySelector('input[name="ostype"]:checked')?.value,
        database: document.querySelector('input[name="database"]:checked')?.value,
        registeredUsers: document.getElementById('registeredUsers')?.value,
        peakLoad: document.getElementById('peakLoad')?.value,
        peakPeriod: document.getElementById('peakPeriod')?.value,
        concurrentUsers: document.getElementById('concurrentUsers')?.value,
        mobileappusers: document.getElementById('mobileappusers')?.value,
        lkusers: document.getElementById('lkusers')?.value,
        importhistorydata: document.getElementById('importhistorydata')?.value,
        annualdatagrowth: document.getElementById('annualdatagrowth')?.value,
        midsizedoc: document.getElementById('midsizedoc')?.value,
        dcs: document.getElementById('dcs')?.checked,
        dcsdochours: document.getElementById('dcsdochours')?.value,
        onlineeditor: document.getElementById('onlineeditor')?.value,
        integrationsystems: document.getElementById('integrationsystems')?.value,
        elasticsearch: document.getElementById('elasticsearch')?.checked,
        ario: document.getElementById('ario')?.checked,
        genii: document.getElementById('genii')?.checked,
        ariodocin: document.getElementById('ariodocin')?.value
    };
}

// Загрузка данных формы
function loadFormData() {
    try {
        const savedData = localStorage.getItem('surveyData');
        if (!savedData) return;

        const data = JSON.parse(savedData);
        Object.entries(data).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (!element) return;

            if (element.type === 'checkbox') {
                element.checked = value;
            } else if (element.type === 'radio') {
                const radio = document.querySelector(`input[name="${key}"][value="${value}"]`);
                if (radio) radio.checked = true;
            } else {
                element.value = value;
            }
        });

        // Обновление зависимых полей
        checkDCS();
        checkArio();
    } catch (error) {
        console.error('Error loading form data:', error);
        showAlert('Ошибка при загрузке сохраненных данных!', 'danger');
    }
}

// Обработка экспорта
async function handleExport() {
    try {
        // Показываем модальное окно загрузки
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();

        const formData = collectFormData();
        const xmlData = jsonToXML(formData);
        
        const response = await fetch('/process-xml', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/xml',
                'X-Organization-Name': btoa(unescape(encodeURIComponent(formData.organization || 'Unknown')))
            },
            body: xmlData
        });
        
        const result = await response.json();
        
        // Скрываем модальное окно загрузки
        loadingModal.hide();
        
        if (response.ok && result.success) {
            // Создаем ссылку на отчет
            const reportLinkDiv = document.getElementById('reportLink');
            reportLinkDiv.innerHTML = `<a href="${result.report_link}" class="btn btn-primary" target="_blank">
                <i class="bi bi-download"></i> Скачать отчет
            </a>`;
            
            // Показываем модальное окно с результатом
            const reportModal = new bootstrap.Modal(document.getElementById('reportModal'));
            reportModal.show();
        } else {
            showAlert(`Ошибка при обработке XML: ${result.error || 'Неизвестная ошибка'}`, 'danger');
        }
    } catch (error) {
        // Скрываем модальное окно загрузки в случае ошибки
        const loadingModal = document.getElementById('loadingModal');
        if (loadingModal) {
            bootstrap.Modal.getInstance(loadingModal)?.hide();
        }
        
        console.error('Detailed export error:', error);
        showAlert('Произошла ошибка при экспорте данных', 'danger');
    }
}

// Загрузка XML файла
function downloadXML(xml) {
    const blob = new Blob([xml], { type: 'application/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    try {
        a.href = url;
        a.download = 'surveyData.xml';
        a.click();
    } finally {
        URL.revokeObjectURL(url);
    }
}

// Конвертация JSON в XML
function jsonToXML(obj) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<survey>\n';
    
    for (const [key, value] of Object.entries(obj)) {
        if (value !== null && value !== undefined && value !== '') {
            xml += `  <${key}>${escapeXML(String(value))}</${key}>\n`;
        }
    }
    
    return xml + '</survey>';
}

// Экранирование XML
function escapeXML(str) {
    return str.replace(/[<>&'"]/g, char => {
        switch (char) {
            case '<': return '&lt;';
            case '>': return '&gt;';
            case '&': return '&amp;';
            case "'": return '&apos;';
            case '"': return '&quot;';
            default: return char;
        }
    });
}

// Отображение уведомлений
function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts-container') 
        || createAlertsContainer();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    alertsContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

// Создание контейнера для уведомлений
function createAlertsContainer() {
    const container = document.createElement('div');
    container.id = 'alerts-container';
    container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1050;';
    document.body.appendChild(container);
    return container;
}