import { initTooltips } from './tooltips.js';
import { updateDatabaseOptions, checkVersion, checkDCS, checkArio } from './form-controls.js';
import { loadFormData, saveFormData } from './form-storage.js';
import { exportToXML } from './xml-export.js';
import { showAlert } from './ui-utils.js';

document.addEventListener('DOMContentLoaded', () => {
    // Инициализация тултипов
    initTooltips();

    // Получение элементов формы
    const form = document.getElementById('surveyForm');
    const clearButton = document.getElementById('clearButton');
    const exportBtn = document.getElementById('exportXml');
    const versionSelect = document.getElementById('version');
    const s3Checkbox = document.getElementById('s3storage');
    const dcsCheckbox = document.getElementById('dcs');
    const dcsInput = document.getElementById('dcsdochours');
    const arioCheckbox = document.getElementById('ario');
    const arioInput = document.getElementById('ariodocin');

    // Инициализация состояния формы
    loadFormData();
    updateDatabaseOptions();
    checkVersion(versionSelect, s3Checkbox);
    checkDCS(dcsCheckbox, dcsInput);
    checkArio(arioCheckbox, arioInput);

    // Обработчики событий
    document.querySelectorAll('input[name="ostype"]').forEach(radio => {
        radio.addEventListener('change', updateDatabaseOptions);
    });

    versionSelect.addEventListener('change', () => checkVersion(versionSelect, s3Checkbox));
    dcsCheckbox.addEventListener('change', () => checkDCS(dcsCheckbox, dcsInput));
    arioCheckbox.addEventListener('change', () => checkArio(arioCheckbox, arioInput));

    // Обработчик отправки формы
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            organization: document.getElementById('organization').value,
            version: versionSelect.value,
            kubernetes: document.getElementById('kubernetes').checked,
            s3storage: s3Checkbox.checked,
            redundancy: document.getElementById('redundancy').checked,
            test_kontur: document.getElementById('test_kontur').checked,
            dev_kontur: document.getElementById('dev_kontur').checked,
            monitoring: document.getElementById('monitoring').checked,
            ostype: document.querySelector('input[name="ostype"]:checked')?.value || '',
            database: document.querySelector('input[name="database"]:checked')?.value || '',
            registeredUsers: document.getElementById('registeredUsers').value,
            peakLoad: document.getElementById('peakLoad').value,
            peakPeriod: document.getElementById('peakPeriod').value,
            concurrentUsers: document.getElementById('concurrentUsers').value,
            mobileappusers: document.getElementById('mobileappusers').value,
            lkusers: document.getElementById('lkusers').value,
            importhistorydata: document.getElementById('importhistorydata').value,
            annualdatagrowth: document.getElementById('annualdatagrowth').value,
            midsizedoc: document.getElementById('midsizedoc').value,
            dcs: dcsCheckbox.checked,
            dcsdochours: dcsInput.value,
            onlineeditor: document.getElementById('onlineeditor').value,
            integrationsystems: document.getElementById('integrationsystems').value,
            elasticsearch: document.getElementById('elasticsearch').checked,
            ario: arioCheckbox.checked,
            ariodocin: arioInput.value
        };

        saveFormData(formData);
        showAlert('Данные успешно сохранены!', 'success');
    });
    // Обработчик кнопки очистки
    clearButton.addEventListener('click', () => {
        // Удаление данных из localStorage
        localStorage.removeItem('surveyData');

        // Сброс формы
        form.reset();

        // Отображение уведомления об очистке
        showAlert('Данные успешно очищены!', 'warning');
    });
     
    // Обработчик экспорта XML
    exportBtn.addEventListener('click', async () => {
        const savedData = localStorage.getItem('surveyData');
        if (!savedData) {
            showAlert('Нет данных для экспорта.', 'warning');
            return;
        }

        try {
            const data = JSON.parse(savedData);
            const result = await exportToXML(data);
            
            // Если нет ссылки на отчет, показываем стандартное сообщение об успехе
            if (!result.report_link) {
                showAlert('XML успешно отправлен на сервер!', 'success');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Ошибка при отправке XML на сервер.', 'danger');
        }
    });
});