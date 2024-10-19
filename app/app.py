# app.py
import os
import uuid
import math
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from docx import Document
from datetime import datetime

app = Flask(__name__)

# Папки для загрузок и отчетов
UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'ready_reports'
TEMPLATE_FOLDER = 'word_templates'

# Убедимся, что папки существуют
for folder in [UPLOAD_FOLDER, REPORT_FOLDER, TEMPLATE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Настройки Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
app.config['TEMPLATE_FOLDER'] = TEMPLATE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Максимальный размер файла: 16MB

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_xml():
    if 'xml_file' not in request.files:
        return "Файл не загружен", 400
    file = request.files['xml_file']
    if file.filename == '':
        return "Имя файла пустое", 400
    if not file.filename.lower().endswith('.xml'):
        return "Неподдерживаемый формат файла. Пожалуйста, загрузите XML файл.", 400

    # Сохраняем загруженный XML файл
    filename = f"{uuid.uuid4()}.xml"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Парсим XML файл
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        return "Ошибка при разборе XML файла.", 400

    # Извлекаем необходимые данные из XML
    data = {}
    for child in root:
        data[child.tag] = child.text

    #Функция получения даты
    def get_current_date_formatted():
        today = datetime.today()
        return today.strftime("%d.%m.%Y")
    current_date = get_current_date_formatted()

    # Расчеты ------------------------------------------------------------------------------------------
    # Перекидываем данные в переменные
    concurrent_users = int(data.get('concurrentUsers', ''))
    redundancy = data.get('redundancy', '')
    # [Перекрестился, и пошел с богом]
    # 1. Расчет узлов веб-серверов
    # 1.1 Рассчитаем какое кол-во веб-сервером нам требуется.
    if concurrent_users > 0:
        numofws = concurrent_users / 2500
        numofwsrnd = math.ceil(numofws)
        if redundancy.lower()  == "true":
            numofwsrnd = numofwsrnd + 1
        else:
            numofwsrnd
    else:
        numofwsrnd = "0"

    # 1.2 Считаем кол-во ядер
    def round_up_to_even(SRVUNITCPUWS):
        if SRVUNITCPUWS % 2 == 0:
            return SRVUNITCPUWS
        else:
            return SRVUNITCPUWS + 1
    def compute_result(concurrent_users, numofwsrnd, redundancy):
        if concurrent_users == 0 or numofwsrnd == 0:
            SRVUNITCPUWS = 0
        elif concurrent_users < 501:
            SRVUNITCPUWS = 6
        else:
            if redundancy.lower() == "true":
                if numofwsrnd - 1 <= 0:
                    raise ValueError("При redundancy='true' значение numofwsrnd должно быть больше 1.")
                temp = concurrent_users / (numofwsrnd - 1) / 500
                temp_rounded_up = math.ceil(temp)
                SRVUNITCPUWS = temp_rounded_up * 2 + 2
            else:
                temp = concurrent_users / numofwsrnd / 500
                temp_rounded_up = math.ceil(temp)
                SRVUNITCPUWS = temp_rounded_up * 2 + 2
        SRVUNITCPUWS = round_up_to_even(SRVUNITCPUWS)
        return SRVUNITCPUWS
    SRVUNITCPUWS = compute_result(concurrent_users, numofwsrnd, redundancy)
    
    # 1.3 Считаем кол-во ОЗУ
    def calculate_srvunitram_ws_value(concurrent_users, numofwsrnd, redundancy):
        if concurrent_users == 0:
            temp = 0
        elif concurrent_users < 501:
            temp = 14
        elif concurrent_users < 2501:
            temp = 12
        else:
            if redundancy.lower() == "true":
                if numofwsrnd <= 1:
                    raise ValueError("numofwsrnd должно быть больше 1, если redundancy равно 'Да'.")
                ceil_value = math.ceil(concurrent_users / (numofwsrnd - 1) / 500)
            else:
                ceil_value = math.ceil(concurrent_users / numofwsrnd / 500)
            temp = ceil_value * 2 + 2
        # Функция ЧЁТН: округление до ближайшего четного числа
        if temp % 2 == 0:
            return temp
        else:
            return temp + 1
    SRVUNIT_RAM_WS = calculate_srvunitram_ws_value(concurrent_users, numofwsrnd, redundancy)
    
    # 1.4 Диск для веб-сервера
    if SRVUNITCPUWS != 0:
        SRVUNITHDD = "100"
    else:
        SRVUNITHDD = "0"

    # Загружаем шаблон Word
    template_path = os.path.join(app.config['TEMPLATE_FOLDER'], 'RecomendBaseTpl4.10.docx')
    if not os.path.exists(template_path):
        return "Шаблон Word не найден.", 500

    doc = Document(template_path)

    # Функция для замены текста в шаблоне
    def replace_placeholder(doc, placeholder, value):
        value = str(value)  # Преобразование значения в строку
        for paragraph in doc.paragraphs:
            if placeholder in paragraph.text:
                inline = paragraph.runs
                for i in range(len(inline)):
                    if placeholder in inline[i].text:
                        inline[i].text = inline[i].text.replace(placeholder, value)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    replace_placeholder(cell, placeholder, value)

    # Заменяем необходимые поля
    replacements = {
        # Блок с общей информацией 
        "CompanyName": data.get('organization', ''),
        "CurrentDate": str(current_date),
        "UsersPeak": data.get('peakLoad', ''),
        "TotalUsers": str(data.get('totalUsers', '')),
        # Условия фнукционирования
        "DBTypeSQL": str(data.get('database', '')),
        #Активность пользователей
        "UserCount": str(data.get('registeredUsers', '')),
        "UsersForecast": str(data.get('concurrentUsers', '')),
        # Блок Веб-сервер
        "SRVUNITCount": str(numofwsrnd),
        "SRVUNITCPU": str(SRVUNITCPUWS),
        "SRVUNITRAM": str(SRVUNIT_RAM_WS),
        "SRVUNITHDD": str(SRVUNITHDD),
        # Прирост и миграция
        "ImportDataSize": str(data.get('importhistorydata', '')),
        "YearlyDataSize": str(data.get('annualdatagrowth', '')),
    }

    for placeholder, value in replacements.items():
        replace_placeholder(doc, placeholder, value)

    # Сохраняем готовый отчет
    report_filename = f"report_{uuid.uuid4()}.docx"
    report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)
    doc.save(report_path)

    # Удаляем загруженный XML файл (опционально)
    os.remove(filepath)

    report_link = url_for('download_report', filename=report_filename)

    return render_template('index.html', report_link=report_link)

@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
