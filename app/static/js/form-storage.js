export function loadFormData() {
    const savedData = localStorage.getItem('surveyData');
    if (savedData) {
        const formData = JSON.parse(savedData);
        Object.keys(formData).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = formData[key];
                } else if (element.type === 'radio') {
                    const radio = document.querySelector(`input[name="${key}"][value="${formData[key]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    element.value = formData[key];
                }
            }
        });
    }
}

export function saveFormData(formData) {
    localStorage.setItem('surveyData', JSON.stringify(formData));
}

// Обработчик кнопки очистки
clearButton.addEventListener('click', () => {
    // Удаление данных из localStorage
    localStorage.removeItem('surveyData');

    // Сброс формы
    form.reset();

    // Отображение уведомления об очистке
    showAlert('Данные успешно очищены!', 'warning');
});