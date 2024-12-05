export function escapeXML(str) {
    const entities = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&apos;'
    };
    return str.replace(/[&<>"']/g, char => entities[char]);
}

export function jsonToXML(obj) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<survey>\n';
    for (const key in obj) {
        const value = obj[key] === null || obj[key] === undefined ? '' : obj[key].toString();
        xml += `  <${key}>${escapeXML(value)}</${key}>\n`;
    }
    xml += '</survey>';
    return xml;
}

export async function exportToXML(data) {
    const xml = jsonToXML(data);
    try {
        const response = await fetch('/save-xml', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/xml'
            },
            body: xml
        });
        
        if (response.ok) {
            // Перенаправляем на страницу обработки
            window.location.href = '/processing';
        } else {
            throw new Error('Ошибка при отправке XML');
        }
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
