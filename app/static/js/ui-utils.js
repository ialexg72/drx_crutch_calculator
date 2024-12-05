export function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show fixed-top m-3`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        const alert = bootstrap.Alert.getInstance(alertDiv);
        if (alert) {
            alert.close();
        }
    }, 3000);
}