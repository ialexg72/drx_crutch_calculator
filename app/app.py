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

    # Закидываем данные из XML в переменные
    operationsystem = data.get('system', '')
    monitoring = data.get('monitoring', '')
    concurrent_users = int(data.get('concurrentUsers', ''))
    redundancy = data.get('redundancy', '')
    mobileusers = int(data.get('mobileappusers', ''))
    lk_users = int(data.get('lkusers', ''))
    dcs = data.get('dcs', '')
    dcsdochours = int(data.get('dcsdochours', ''))
    elasticsearch = data.get('elasticsearch', '')
    annualdatagrowth = int(data.get('annualdatagrowth', ''))
    midsizedoc = int(data.get('midsizedoc', ''))
    ario = data.get('ario', '')
    ariodocin = int(data.get('ariodocin', ''))

    # Загружаем шаблон Word
    if operationsystem.lower() == "linux":
        template_path = os.path.join(app.config['TEMPLATE_FOLDER'], 'RecomendBaseTpl4.10_linux.docx')
    else:
        template_path = os.path.join(app.config['TEMPLATE_FOLDER'], 'RecomendBaseTpl4.10_winux.docx')
    if not os.path.exists(template_path):
        return "Шаблон Word не найден.", 500
    doc = Document(template_path)

    #Функция для удаления не нужных блоков в таблицах
    def delete_rows(table, start_row, end_row):
       """
       Удаляет строки из таблицы от start_row до end_row включительно.
       
       :param table: Объект таблицы из python-docx
       :param start_row: Начальный индекс строки для удаления (0-based)
       :param end_row: Конечный индекс строки для удаления (0-based)
       """
       # Проверяем, что индексы корректны
       total_rows = len(table.rows)
       if start_row < 0 or end_row >= total_rows or start_row > end_row:
           raise IndexError("Неверный диапазон индексов строк для удаления.")
       
       # Рекомендуется удалять строки в обратном порядке, чтобы индексы не смещались
       for row_idx in range(end_row, start_row - 1, -1):
           row = table.rows[row_idx]
           tbl = table._tbl
           tr = row._tr
           tbl.remove(tr)
           print(f"Удалена строка с индексом {row_idx}.")

    # 1. Расчет узлов веб-серверов
    # 1.1 Рассчет кол-во узлов веб-сервера.
    def calculate_webserver_count(concurrent_users, redundancy):
        if concurrent_users > 0:
            count = concurrent_users / 2500
            count_rnd = math.ceil(count)
            if redundancy.lower()  == "true":
                count_rnd = count_rnd + 1
            else:
                count_rnd
        else:
            count_rnd = "0"
        return count_rnd
    webserver_count = calculate_webserver_count(concurrent_users, redundancy)

    # 1.2 Расчет кол-во ядер для узлов веб-сервера
    def round_up_to_even(SRVUNITCPUWS):
        if SRVUNITCPUWS % 2 == 0:
            return SRVUNITCPUWS
        else:
            return SRVUNITCPUWS + 1
    def compute_result(concurrent_users, webserver_count, redundancy):
        if concurrent_users == 0 or webserver_count == 0:
            SRVUNITCPUWS = 0
        elif concurrent_users < 501:
            SRVUNITCPUWS = 6
        else:
            if redundancy.lower() == "true":
                if webserver_count - 1 <= 0:
                    raise ValueError("При redundancy='true' значение webserver_count должно быть больше 1.")
                temp = concurrent_users / (webserver_count - 1) / 500
                temp_rounded_up = math.ceil(temp)
                SRVUNITCPUWS = temp_rounded_up * 2 + 2
            else:
                temp = concurrent_users / webserver_count / 500
                temp_rounded_up = math.ceil(temp)
                SRVUNITCPUWS = temp_rounded_up * 2 + 2
        SRVUNITCPUWS = round_up_to_even(SRVUNITCPUWS)
        return SRVUNITCPUWS
    SRVUNITCPUWS = compute_result(concurrent_users, webserver_count, redundancy)
    
    # 1.3 Считаем кол-во ОЗУ
    def calculate_srvunitram_ws_value(concurrent_users, webserver_count, redundancy):
        if concurrent_users == 0:
            temp = 0
        elif concurrent_users < 501:
            temp = 14
        elif concurrent_users < 2501:
            temp = 12
        else:
            if redundancy.lower() == "true":
                if webserver_count <= 1:
                    raise ValueError("webserver_count должно быть больше 1, если redundancy равно 'Да'.")
                ceil_value = math.ceil(concurrent_users / (webserver_count - 1) / 500)
            else:
                ceil_value = math.ceil(concurrent_users / webserver_count / 500)
            temp = ceil_value * 2 + 2
        # Функция ЧЁТН: округление до ближайшего четного числа
        if temp % 2 == 0:
            return temp
        else:
            return temp + 1
    SRVUNIT_RAM_WS = calculate_srvunitram_ws_value(concurrent_users, webserver_count, redundancy)
    
    # 1.4 Диск для веб-сервера
    if SRVUNITCPUWS != 0:
        SRVUNITHDD = "100"
    else:
        SRVUNITHDD = "0"

    # 2. Расчет узлов микросервисов --------------------------------------------------------------
    # 2.1 Расчет кол-ва узлов
    if concurrent_users > 500:
        numofms = concurrent_users / 2500
        numofms_rnd = math.ceil(numofms)
        if redundancy.lower()  == "true":
            numofms_rnd = numofms_rnd + 1
        else:
            numofms_rnd
    else:
        numofms_rnd = "0"

    #2.2 Расчет кол-ва ядер
    def round_up_to_ms(SRVUNIT_MS_CPU):
        if SRVUNIT_MS_CPU % 2 == 0:
            return SRVUNIT_MS_CPU
        else:
            return SRVUNIT_MS_CPU + 1
    def compute_result(concurrent_users, numofms_rnd, redundancy):
        if concurrent_users == 0 or numofms_rnd == 0:
            SRVUNIT_MS_CPU = 0
        elif concurrent_users < 1001:
            SRVUNIT_MS_CPU = 6
        else:
            if redundancy.lower() == "true":
                if numofms_rnd - 1 <= 0:
                    raise ValueError("При redundancy='true' значение numofmsrnd должно быть больше 1.")
                temp_ms_up = concurrent_users / (numofms_rnd - 1) / 500
                temp_roundedms_up = math.ceil(temp_ms_up)
                SRVUNIT_MS_CPU = temp_roundedms_up * 2 + 2
            else:
                temp_ms_up = concurrent_users / numofms_rnd / 500
                temp_roundedms_up = math.ceil(temp_ms_up)
                SRVUNIT_MS_CPU = temp_roundedms_up * 2 + 2
        SRVUNIT_MS_CPU = round_up_to_ms(SRVUNIT_MS_CPU)
        return SRVUNIT_MS_CPU
    SRVUNIT_MS_CPU = compute_result(concurrent_users, numofms_rnd, redundancy)

    # 2.3 Расчет кол-ва RAM
    def calculate_SRVUNIT_MS_RAM(concurrent_users, numofms_rnd, redundancy):
        if concurrent_users == 0 or numofms_rnd == 0:
            value = 0
        elif concurrent_users < 1501:
            value = 12
        else:
            if redundancy.lower() == "true":
                denominator = numofms_rnd - 1
                if denominator > 0:
                    temp = math.ceil(concurrent_users / denominator / 1000)
                    value = temp * 6
                else:
                    value = 0
            else:
                temp = math.ceil(concurrent_users / numofms_rnd / 1000)
                value = temp * 6
        if value % 2 != 0:
            value += 1
        return value
    SRVUNIT_MS_RAM = calculate_SRVUNIT_MS_RAM(concurrent_users, numofms_rnd, redundancy)

    #2.4 Расчет HDD
    if concurrent_users > 500:
        SRVUNIT_MS_HDD = 100
    else:
        SRVUNIT_MS_HDD = 0

    # 3 Расчеты для сервиса Nomad
    # 3.1 Считаем кол-во узлов
    def calculate_nomad_count(mobileusers, redundancy):
        if mobileusers < 100:
            count = 0
        else:
            divided_value = mobileusers / 1000
            rounded_value = math.ceil(divided_value)
            if redundancy.lower() == "true":
                return rounded_value + 1
            else:
                return rounded_value

    #3.2 Считаем CPU
    def calculate_nomad_cpu(mobileusers, redundancy):
        if mobileusers == 0:
            return 0
        else:
            divided_value = mobileusers / 1000
            rounded_value = math.ceil(divided_value)
            if redundancy.lower() == "true":
                return rounded_value + 1
            else:
                return rounded_value

    #3.3 Считаем RAM
    nomad_count = calculate_nomad_count(mobileusers, redundancy)
    def calculate_nomad_ram(mobileusers, redundancy, nomad_count):
        if mobileusers < 100:
            result = 0
        else:
            if redundancy.lower() == "true":
                if nomad_count == 1:
                    raise ValueError("G5 не должно быть равно 1, чтобы избежать деления на ноль.")
                value = (mobileusers / (nomad_count - 1)) / 50 * 1.5 + 2
            else:
                value = (mobileusers / nomad_count) / 50 * 1.5 + 2
            rounded = math.ceil(value)  
            if rounded % 2 != 0:
                rounded += 1
            result = rounded
        return result    

    #3.4 Считаем HDD
    def calculate_nomad_hdd(mobileusers):
        if mobileusers != 0:
            calculate_nomad_hdd = 100
        else:
            calculate_nomad_hdd = 0
        return calculate_nomad_hdd        

    #4 Считаем reverse proxy узлы
    def calculate_reverseproxy_count(concurrent_users, redundancy):
        if concurrent_users != 0:
            if redundancy.lower() == "true":
                result = 2
            else:
                if concurrent_users < 500:
                    result = 0
                else:
                    result = 1
        else:
            result = 0
        return result
    reverseproxy_count = calculate_reverseproxy_count(concurrent_users, redundancy)
    def calculate_reverseproxy_cpu(reverseproxy_count, concurrent_users):
        if reverseproxy_count != 0:
            divided = concurrent_users / 5000
            ceiled = math.ceil(divided)
            multiplied = ceiled * 2
        else:
            multiplied = 0
        if multiplied % 2 != 0:
            multiplied += 1 
        return multiplied
    reverseproxy_cpu = calculate_reverseproxy_cpu(reverseproxy_count, concurrent_users)
    def calculate_reverseproxy_ram(reverseproxy_count, concurrent_users):
        if reverseproxy_count != 0:
            divided = concurrent_users / 5000
            ceiled = math.ceil(divided)
            multiplied = ceiled * 2
        else:
            multiplied = 0
        if multiplied % 2 != 0:
            multiplied += 1 
        return multiplied
    reverseproxy_ram = calculate_reverseproxy_ram(reverseproxy_count, concurrent_users)
    def calculate_reverseproxy_hdd(reverseproxy_count):
        if reverseproxy_count != 0:
            rp_hdd = 50
        else:
            rp_hdd = 0
        return rp_hdd
    reverseproxy_hdd = calculate_reverseproxy_hdd(reverseproxy_count)
    
    #5 Расчет СУБД
    def calculate_sql_count(redundancy):
        if redundancy.lower() == "true":
            count = 2
        else:
            count = 1
        return count
    sql_count = calculate_sql_count(redundancy)

    def calculate_sql_cpu(concurrent_users, redundancy, lk_users):
        if concurrent_users < 501:
            cpu = 6 + (lk_users/10000)*2
        elif concurrent_users < 1500:
            cpu = 8 + (lk_users/10000)*2
        else:
            cpu = math.ceil(concurrent_users/400)*2+(lk_users/10000)*2
        if cpu >= 0:
            ceil_num = math.ceil(cpu)
            if ceil_num % 2 == 0:
                return ceil_num
            else:
                return ceil_num + 1
        else:
            floor_num = math.floor(number)
            if floor_num % 2 == 0:
                return floor_num
            else:
                return floor_num - 1
    sql_cpu = calculate_sql_cpu(concurrent_users, redundancy, lk_users)

    def calculate_sql_ram(concurrent_users, redundancy, lk_users):
        if concurrent_users > 50 or redundancy == "Да":
            if concurrent_users < 500:
                value = math.ceil(concurrent_users / 125) + 6 + (lk_users / 10000) * 4
            elif concurrent_users < 2000:
                value = 16 + (lk_users / 10000) * 4
            else:
                value = math.ceil(concurrent_users / 400) * 4 + (lk_users / 10000) * 4
        else:
            value = 0
        rounded_value = math.ceil(value)
        if rounded_value % 2 != 0:
            even_value = rounded_value + 1
        else:
            even_value = rounded_value
        return even_value
    sql_ram = calculate_sql_ram(concurrent_users, redundancy, lk_users)

    #Служба ввода документов DCS
    def calculate_dcs_count(dcs):
        if dcs.lower() == "true":
            count = 1
        else:
            count = 0
        return count
    dcs_count = calculate_dcs_count(dcs)

    def calculate_dcs_cpu(dcs, dcsdochours):
        if dcs.lower() == "true":
            rounded_up = math.ceil(dcsdochours / 150)
            intermediate_result = rounded_up + 2
        else:
            intermediate_result = 0
        if intermediate_result % 2 != 0:
            final_result = intermediate_result + 1
        else:
            final_result = intermediate_result
        return final_result
    dcs_cpu = calculate_dcs_cpu(dcs, dcsdochours)

    def calculate_dcs_ram(dcs, dcsdochours):
        if dcs.lower() == "true":
            rounded_up = math.ceil(dcsdochours / 150)*2
            intermediate_result = rounded_up + 2
        else:
            intermediate_result = 0
        if intermediate_result % 2 != 0:
            final_result = intermediate_result + 1
        else:
            final_result = intermediate_result
        return final_result
    dcs_ram = calculate_dcs_ram(dcs, dcsdochours)

    def calculate_dcs_hdd(dcs):
        if dcs.lower() == "true":
            hdd = 50
        else:
            hdd = 0
        return hdd
    dcs_hdd = calculate_dcs_hdd(dcs)

    def calculate_search_count(elasticsearch):
        if elasticsearch.lower() == "true":
            count = 1
        else:
            count = 0
        return count
    elasticsearch_count = calculate_search_count(elasticsearch)

    def calculate_search_cpu(elasticsearch):
        if elasticsearch.lower() == "true":
            cpu = 8
        else:
            cpu = 0
        return cpu
    elasticsearch_cpu = calculate_search_cpu(elasticsearch)

    def calculate_search_ram(elasticsearch, midsizedoc, annualdatagrowth):
        if elasticsearch.lower() == "true":
            ram = annualdatagrowth * midsizedoc
            gigabytes = ram / (1024 ** 3)
            if gigabytes > 6:
                intermediate_result = 32
            else:
                intermediate_result = 16
        else:
            intermediate_result = 0
        if intermediate_result == 0:
           return 0
        elif intermediate_result % 2 == 0:
           return intermediate_result
        elif intermediate_result > 0:
           return intermediate_result + 1
        else:
           return intermediate_result - 1
    elasticsearch_ram = calculate_search_ram(elasticsearch, midsizedoc, annualdatagrowth)

    def calculate_search_hdd(elasticsearch):
        if elasticsearch.lower() == "true":
            hdd = 50
        else:
            hdd = 0
        return hdd
    elasticsearch_hdd = calculate_search_hdd(elasticsearch)

    #Мониторинг (Обеовил схему)
    if monitoring.lower() == "true":
        monitoring_count = 1
        monitoring_hdd = 50
        monitoring_cpu = 16 if concurrent_users > 3000 else 8
        monitoring_ram = 32 if concurrent_users > 3000 else 16  
    else:
        pass

    #Узлы АРИО
    if ario.lower() == "true":
        if operationsystem.lower() == "linux":    
            ario_count = 1
            ario_hdd = 100
            def calculate_ario_cpu(ariodocin):
                if ariodocin <= 25000:
                    return 4
                elif ariodocin <= 55000:
                    return 8
                elif ariodocin <= 90000:
                    return 12
                elif ariodocin <= 150000:
                    return 10
                elif ariodocin <= 250000:
                    return 16
                else:
                    return "Error"           
            ario_cpu = calculate_ario_cpu(ariodocin)

            def calculate_ario_ram(ariodocin):
                if ariodocin <= 25000:
                    return 20
                elif ariodocin <= 55000:
                    return 24
                elif ariodocin <= 90000:
                    return 40
                elif ariodocin <= 150000:
                    return 14
                elif ariodocin <= 250000:
                    return 24
                else:
                    return "Error"
            ario_ram = calculate_ario_ram(ariodocin)

            if ariodocin > 90000:
                dtes_count = 1
                dtes_hdd = 100
                def calculate_dtes_cpu(ariodocin):
                    if ariodocin <= 150000:
                        return 10
                    elif ariodocin <= 250000:
                        return 16
                    else:
                        return "Error"
                dtes_cpu = calculate_dtes_cpu(ariodocin)
                def calculate_dtes_ram(ariodocin):
                    if ariodocin <= 150000:
                        return 28
                    elif ariodocin <= 250000:
                        return 48
                    else:
                        return "Error"
                dtes_ram = calculate_dtes_ram(ariodocin)
            else:
                dtes_count = 0
                dtes_cpu = 0
                dtes_ram = 0
                dtes_hdd = 0
                if len(doc.tables) > 3:
                    # Выбираем таблицу с индексом 3 (четвёртую таблицу)
                    table = doc.tables[3]
                    # Определяем диапазон строк для удаления
                    start_index = 64
                    end_index = 70
                    try:
                        delete_rows(table, start_index, end_index)
                        print(f"Строки с индексами {start_index} по {end_index} из таблицы 3 удалены и документ сохранён как '{output_doc}'.")
                    except IndexError as e:
                        print(f"Ошибка: {e}")
                else:
                    print(f"В документе содержится только {len(doc.tables)} таблиц. Таблица с индексом 3 отсутствует.")
        else:
            pass    
    else:
        pass    

    #А тут вызовы функции
    def remove_row(table, row):
        tbl = table._tbl
        tr = row._tr
        tbl.remove(tr)   
    row = table.rows[0]
    remove_row(table, row)

    #Функция для замены текста в шаблоне
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
        #Блок Веб-сервер
        "WEBCOUNT": str(webserver_count),
        "WEBCPU": str(SRVUNITCPUWS),
        "WEBRAM": str(SRVUNIT_RAM_WS),
        "WEBHDD": str(SRVUNITHDD),
        #Блок микросервисов
        "MSCOUNT": str(numofms_rnd),
        "MSCPU": str(SRVUNIT_MS_CPU), 
        "MSRAM": str(SRVUNIT_MS_RAM),
        "MSHDD": str(SRVUNIT_MS_HDD),
        #Nomad
        "NOMADCOUNT": str(calculate_nomad_count(mobileusers, redundancy)),
        "NOMADCPU": str(calculate_nomad_cpu(mobileusers, redundancy)),
        "NOMADRAM": str(calculate_nomad_ram(mobileusers, redundancy, nomad_count)),
        "NOMADHDD": str(calculate_nomad_hdd(mobileusers)),
        #ReversePorxy
        "RPCOUNT": str(reverseproxy_count),
        "RPCPU": str(reverseproxy_cpu),
        "RPRAM": str(reverseproxy_ram),
        "RPHDD": str(reverseproxy_hdd),
        #СУБД
        "SQLCOUNT": str(sql_count),
        "SQLCPU": str(sql_cpu),
        "SQLRAM": str(sql_ram),
        "SQLHDD": str("100"),
        #СУБД
        "DCSCOUNT": str(dcs_count),
        "DCSCPU": str(dcs_cpu),
        "DCSRAM": str(dcs_ram),
        "DCSHDD": str(dcs_hdd),
        #Полнотекстовый поиск
        "ELASTICCOUNT": str(elasticsearch_count),
        "ELASTICCPU": str(elasticsearch_cpu),
        "ELASTICRAM": str(elasticsearch_ram),
        "ELASTICHDD": str(elasticsearch_hdd),
        #Мониторинг
        "MONITORINGCOUNT": str(monitoring_count),
        "MONITORINGCPU": str(monitoring_cpu),
        "MONITORINGRAM": str(monitoring_ram),
        "MONITORINGHDD": str(monitoring_hdd),
        #Узлы АРИО
        "ARIOCOUNT": str(ario_count),
        "ARIOCPU": str(ario_cpu),
        "ARIORAM": str(ario_ram),
        "ARIOHDD": str(ario_hdd),
        "DTESCOUNT": str(dtes_count),
        "DTESCPU": str(dtes_cpu),
        "DTESRAM": str(dtes_ram),
        "DTESHDD": str(dtes_hdd)
        # Прирост и миграция
        #"ImportDataSize": str(data.get('importhistorydata', '')),
        #"YearlyDataSize": str(data.get('annualdatagrowth', '')),
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
