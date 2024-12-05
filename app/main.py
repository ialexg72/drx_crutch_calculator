# app.py
import os
import re
import uuid
import math
import docx
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify
from docx.table import Table, _Row, _Cell
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from datetime import datetime
from typing import List
from typing import Any
from docx import Document
from docx.text.paragraph import Paragraph
from lxml import etree
from typing import Union
from docx.shared import Inches
import subprocess
import shutil
from app.src.calculate import dcs_services
from src.calculate import k8s, webserver, ms, nomad, reverseproxy
import src.docx.delete_unnecessary_information as delete_unnecessary_information
app = Flask(__name__)

#=======================================================Общие настройки============================================================#
#Массив для отключения сервисов при составлении схемы
layers_to_toggle = []

#=======================================================Маршуруты============================================================#
@app.route('/questionnaire', methods=['GET'])
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_xml():
    logger.info("Начата обработка загруженного XML файла")
    if 'xml_file' not in request.files:
        logger.error("Файл не был загружен в запросе")
        return "Файл не загружен", 400
    
    file = request.files['xml_file']
    if file.filename == '':
        logger.error("Загружен файл с пустым именем")
        return "Имя файла пустое", 400
    
    if not file.filename.lower().endswith('.xml'):
        logger.error(f"Попытка загрузки файла неверного формата: {file.filename}")
        return "Неподдерживаемый формат файла. Пожалуйста, загрузите XML файл.", 400
    
#=======================================================Работа с XML============================================================#
    
    # Сохраняем загруженный XML файл
    try: 
        filename = f"{uuid.uuid4()}.xml"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"XML файл успешно сохранен: {filepath}")
        tree = ET.parse(filepath)
        root = tree.getroot()
        logger.debug("XML файл успешно распарсен")
    except ET.ParseError:
        logger.error(f"Не удалось спарсить данные в XML")
        raise

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
        #Общая информация
    organization = data.get('organization', '')
    logging.debug(f"Организация {organization}")
    operationsystem = data.get('ostype', '')
    logging.debug(f"Оепрационная система {operationsystem}")
    version = data.get('version', '')
    logging.debug(f"Версия {version}")
    kubernetes = data.get('kubernetes', '')
    logging.debug(f"kubernetes {kubernetes}")
    s3storage = data.get('s3storage', '')
    logging.debug(f"S3 Хранилище {s3storage}")
    redundancy = data.get('redundancy', '')
    logging.debug(f"Отказоустойчивость {redundancy}")
    monitoring = data.get('monitoring', '')
    logging.debug(f"Мониторинг {monitoring}")
    dev_kontur = data.get('dev_kontur', '')
    logging.debug(f"Среда разработки {dev_kontur}")
    test_kontur = data.get('test_kontur', '')
    database = data.get('database', '')
    logging.debug(f"Тип СУБД {database}")
        #Активность пользователей
    registeredUsers = int(data.get('registeredUsers', ''))
    peakLoad = int(data.get('peakLoad', ''))
    peakPeriod = data.get('peakPeriod', '')
    concurrent_users = int(data.get('concurrentUsers', ''))
    mobileusers = int(data.get('mobileappusers', ''))
    lk_users = int(data.get('lkusers', ''))
    logging.info(f"Пользователи личного кабинета {lk_users}")
        #Прирост данных
    importhistorydata = int(data.get('importhistorydata', ''))
    annualdatagrowth = int(data.get('annualdatagrowth', ''))
    midsizedoc = int(data.get('midsizedoc', ''))
        #Импорт данных в систему
    dcs = data.get('dcs', '')
    dcsdochours = int(data.get('dcsdochours', ''))
        #Интеграция
    onlineeditor = data.get('onlineeditor', '')
    integrationsystems = data.get('integrationsystems', '')
        #Поиск и обработка данных
    elasticsearch = data.get('elasticsearch', '')
    ario = data.get('ario', '')
    ariodocin = int(data.get('ariodocin', ''))

#=======================================================Условия для выбора шаблона Word============================================================#
    # Загружаем шаблон Word
    if operationsystem.lower() == "linux":
        template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f'RecomendBaseTpl{version}_linux.docx')
        if kubernetes.lower() == "true":
            template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f'RecomendBaseTpl{version}_kubernetes.docx')
    else:
        template_path = os.path.join(app.config['TEMPLATE_FOLDER'], f'RecomendBaseTpl{version}_windows.docx')
    if not os.path.exists(template_path):
        logging.debug("Шаблон Word не найден.")
    try:
        doc = docx.Document(template_path)
        logging.debug(f"Выбран шаблон {template_path}")
    except ET.ParseError:
        logging.error(f"Не удалось подобрать шаблон")
        raise
#=======================================================Функции манипуляций с текстом ============================================================#
    
    #Подгружаем расчеты сервисов
    k8s_count, k8s_cpu, k8s_ram, k8s_hdd = k8s.calculate_kubernetes(kubernetes)
    webserver_count, webserver_cpu, webserver_ram, webserver_hdd = webserver.calculate_webserver(concurrent_users, redundancy)
    ms_count, ms_cpu, ms_ram, ms_hdd = ms.calculate_ms(redundancy, concurrent_users)
    nomad_count, nomad_cpu, nomad_ram, nomad_hdd = nomad.calculate_nomad(redundancy, mobileusers)
    reverseproxy_count, reverseproxy_cpu, reverseproxy_ram, reverseproxy_hdd = reverseproxy.calculate_reverseproxy(redundancy, concurrent_users) 
    sql_count, sql_cpu, sql_ram, sql_hdd = sql.calculate_sql(redundancy, concurrent_users, lk_users)
    dcs_count, dcs_cpu, dcs_ram, dcs_hdd = dcs.calculate_dcs(redundancy, dcsdochours)
    elasticsearch_count, elasticsearch_cpu, elasticsearch_ram, elasticsearch_hdd = calculate_elasticsearch(redundancy, elasticsearch, annualdatagrowth, midsizedoc)
    ario_count, ario_cpu, ario_ram, ario_hdd, dtes_count, dtes_cpu, dtes_ram, dtes_hdd = calculate_ario(operationsystem, ariodocin)
    #=======================================================Расчеты сайзинга хранилищ============================================================#
    #Исторические данные
    importhistorydata_size = round(importhistorydata * midsizedoc /1024 / 1024)
    logger.info(f"{importhistorydata} * {midsizedoc} = {importhistorydata_size}")
    #Годовой прирост документов
    annualdatagrowth_size = round(annualdatagrowth * midsizedoc / 1024 / 1024)
    #Объем основого хранилища тел документов
    main_storage_doc = round((annualdatagrowth_size * 6) + importhistorydata_size)
    #Объем резервного хранилища
    reserve_storage_doc = round(main_storage_doc*2)
    #Объем основного хранилища БД
    if concurrent_users != 0 or sql_count != 0:
        main_storage_db = main_storage_doc * 0.025 + (concurrent_users / 100 * 5)
        if redundancy.lower() == "true" and database.lower() == "postgres":
            if main_storage_db < 100:
                main_storage_db = 200
            else:
                main_storage_db = main_storage_db * 2
        else:
            if main_storage_db < 100:
                main_storage_db = 100
            else:
                main_storage_db  
        main_storage_db = int(main_storage_db)
    else:
        main_storage_db = 0
    #Объем резервного хранилища БД
    if database.lower() == "postgres" and redundancy.lower() == "true":
        reserve_storage_db = main_storage_db*8/2
    else:
        reserve_storage_db = main_storage_db*8
    #Разделы высокоскоростных данных (разделы ВМ под ОС, разделы БД)
    highspeed_storage = (
        int(main_storage_db)
        +int(webserver_count*webserver_hdd)
        +int(ms_count*ms_hdd)
        +int(k8s_count*k8s_hdd)
        +int(nomad_count*nomad_hdd)
        +int(reverseproxy_count*reverseproxy_hdd)
        +int(sql_count*100)
        +int(dcs_count*dcs_hdd)
        +int(elasticsearch_count*elasticsearch_hdd)
        +int(monitoring_count*monitoring_hdd)
        +int(ario_count*ario_hdd)
        +int(dtes_count*dtes_hdd)
        +int(onlineeditor_count*onlineeditor_hdd)
        +int(lk_count*lk_hdd)
        +int(additional_lk_count*additional_lk_hdd)
        +int(rrm_count*rrm_hdd)
        +int(logstash_count*logstash_hdd)
    )
    #Разделы индексов полнотекстового поиска
    def calculate_serachindex_size(elasticsearch, redundancy, database, main_storage_doc, main_storage_db):
        if elasticsearch.lower() != "false":
            if redundancy.lower() == "true" and database.lower() == "postgres":
                value = main_storage_doc * 0.05 + (main_storage_db * 0.05) / 2
            else:
                value = main_storage_doc * 0.05 + main_storage_db * 0.05
            # Округление вверх до ближайшего целого числа
            result = math.ceil(value)
        else:
            result = 0
        return result
    elasticsearch_serachindex_size = calculate_serachindex_size(elasticsearch, redundancy, database, main_storage_doc, main_storage_db)
    #Разделы средненагруженных данных (ФХ тел документов) = main storage doc
    #Разделы сервисных баз данных СУБД
    service_db_size = math.ceil(concurrent_users/500*2)
    #Разделы низконагруженных данных (резервное хранение/копирование)
    lowspeed_storage = (reserve_storage_db + reserve_storage_doc)

#=======================================================Вызываем функцию замены плейсхолдеров в word на значения переменных============================================================#
    replacements = {
        # Блок с общей информацией 
        "UsersPeak": str(f"{concurrent_users} пользователей «Directum RX»" if lk_users == 0 else f"{concurrent_users} пользователей «Directum RX» и {lk_users} пользователей  «Личный кабинет»"),
        "CompanyName": str(organization),
        "CurrentDate": str(current_date),
        "TotalUsers": str(registeredUsers),
        "ImportPeriod": str("До 250" if dcsdochours < 250 else dcsdochours),
        "ExtIntegration": str(integrationsystems),
        # Условия фнукционирования
        "OSTypeSQL": str(operationsystem),
        "DBTypeSQL": str(database),
        #Активность пользователей
        "UserCount": str(registeredUsers),
        "UsersForecast": str(concurrent_users),
        "K8SCOUNT": str(k8s_count),
        "K8SCPU": str(k8s_cpu),
        "K8SRAM": str(k8s_ram),
        "K8SHDD": str(k8s_hdd),
        #Блок Веб-сервер
        "WEBCOUNT": str(webserver_count),
        "WEBCPU": str(webserver_cpu),
        "WEBRAM": str(webserver_ram),
        "WEBHDD": str(webserver_hdd),
        #Блок микросервисов
        "MSCOUNT": str(ms_count),
        "MSCPU": str(ms_cpu), 
        "MSRAM": str(ms_ram),
        "MSHDD": str(ms_hdd),
        #Nomad
        "NOMADCOUNT": str(nomad_count),
        "NOMADCPU": str(nomad_cpu),
        "NOMADRAM": str(nomad_ram),
        "NOMADHDD": str(nomad_hdd),
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
        #Доп узел Logstash
        "LOGSTASHCOUNT": str(logstash_count),
        "LOGSTASHCPU": str(logstash_cpu),
        "LOGSTASHRAM": str(logstash_ram),
        "LOGSTASHHDD": str(logstash_hdd),
        #Интеграция с онлайн редакторами
        "ONLINEEDITORCOUNT": str(onlineeditor_count),
        "ONLINEEDITORCPU": str(onlineeditor_cpu),
        "ONLINEEDITORRAM": str(onlineeditor_ram),
        "ONLINEEDITORHDD": str(onlineeditor_hdd),
        #Узлы АРИО
        "ARIOCOUNT": str(ario_count),
        "ARIOCPU": str(ario_cpu),
        "ARIORAM": str(ario_ram),
        "ARIOHDD": str(ario_hdd),
        "DTESCOUNT": str(dtes_count),
        "DTESCPU": str(dtes_cpu),
        "DTESRAM": str(dtes_ram),
        "DTESHDD": str(dtes_hdd),
        #Узлы RabbitMQ, etcd + keepalived + haproxy 
        "RRMCOUNT": str(rrm_count),
        "RRMCPU": str(rrm_cpu),
        "RRMRAM": str(rrm_ram),
        "RRMHDD": str(rrm_hdd),
        #Личный кабинет
        "LKCOUNT": str(lk_count),
        "LKCPU": str(lk_cpu),
        "LKRAM": str(lk_ram),
        "LKHDD": str(lk_hdd),
        "ADDRXNODECOUNT": str(additional_lk_count),
        "ADDRXNODECPU": str(additional_lk_cpu),
        "ADDRXNODERAM": str(additional_lk_ram),
        "ADDRXNODEHDD": str(additional_lk_hdd),
        #S3 Tool
        "S3CPU": str(s3storage_cpu),
        "S3RAM": str(s3storage_ram),
        "S3COUNT": str(s3storage_count),
        #Сумма ресурсов
        "UnitsCPU": str((webserver_count*webserver_cpu)+(ms_count*ms_cpu)+(k8s_count*k8s_cpu)+(nomad_count*nomad_cpu)+(reverseproxy_count*reverseproxy_cpu)+(sql_count*sql_cpu)
            +(dcs_count*dcs_cpu)+(elasticsearch_count*elasticsearch_cpu)+(monitoring_count*monitoring_cpu)+(ario_count*ario_cpu)+(dtes_count*dtes_cpu)
            +(onlineeditor_count*onlineeditor_cpu)+(lkcalcultions["lk_count"]*lkcalcultions["lk_cpu"])
            +(lkcalcultions["additional_lk_count"]*lkcalcultions["additional_lk_cpu"])
            +(s3storage_count*s3storage_cpu)
            +(rrm_count*rrm_cpu)+(logstash_count*logstash_cpu)
            ), 
        "UnitsRAM": str((webserver_count*webserver_ram)+(ms_count*ms_ram)+(k8s_count*k8s_ram)+(nomad_count*nomad_ram)+(reverseproxy_count*reverseproxy_ram)+(sql_count*sql_ram)
            +(dcs_count*dcs_ram)+(elasticsearch_count*elasticsearch_ram)+(monitoring_count*monitoring_ram)+(ario_count*ario_ram)+(dtes_count*dtes_ram)
            +(onlineeditor_count*onlineeditor_ram)
            +(lk_count*lk_ram)+(additional_lk_count*additional_lk_ram)
            +(s3storage_count*s3storage_ram)
            +(rrm_count*rrm_ram)+(logstash_count*logstash_ram)
            ),
        # Прирост и миграция
        "ImportDataSize": str(round(importhistorydata_size / 1024, 1)) + " ТБ" if importhistorydata_size >= 1000 else str(importhistorydata_size) + " ГБ",
        "YearlyDataSize": str(round(annualdatagrowth_size / 1024, 1)) + " ТБ" if annualdatagrowth_size >= 1000 else str(annualdatagrowth_size) + " ГБ",
        "SQLStorageSize": str(round(main_storage_db / 1024, 1)) + " ТБ" if main_storage_db >= 1000 else str(main_storage_db) + " ГБ",
        "SQLResStorageSize": str(round(reserve_storage_db / 1024, 1)) + " ТБ" if reserve_storage_db >= 1000 else str(reserve_storage_db) + " ГБ",
        "FastStorageSize": str(round(highspeed_storage / 1024, 1)) + " ТБ" if highspeed_storage >= 1000 else str(highspeed_storage) + " ГБ",
        "SearchIndexSize": str(round(elasticsearch_serachindex_size / 1024, 1)) + " ТБ" if int(elasticsearch_serachindex_size) >= 1000 else str(elasticsearch_serachindex_size) + " ГБ", 
        "MidStorageSize": str(round(main_storage_doc / 1024, 1)) + " ТБ" if main_storage_doc >= 1000 else str(main_storage_doc) + " ГБ",
        "ServiceDBStorageSize": str(round(service_db_size / 1024, 1)) + " ТБ" if service_db_size >= 1000 else str(service_db_size) + " ГБ",
        "SlowStorageSize": str(round(lowspeed_storage / 1024, 1)) + " ТБ" if lowspeed_storage >= 1000 else str(lowspeed_storage) + " ГБ",
        "FStorageSize": str(round(main_storage_doc / 1024, 1)) + " ТБ" if main_storage_doc >= 1000 else str(main_storage_doc) + " ГБ",
        "FResStorageSize": str(round(reserve_storage_doc / 1024, 1)) + " ТБ" if reserve_storage_doc >= 1000 else str(reserve_storage_doc) + " ГБ",
    }
    for placeholder, value in replacements.items():
        replace_placeholder(doc, placeholder, value)

    # Удаление ненужной текстовой информации из файла word
    delete_unnecessary_information.main(
        doc,
        kubernetes, 
        k8s_count, 
        ms_count, 
        nomad_count, 
        reverseproxy_count, 
        dcs_count, 
        elasticsearch_count, 
        rrm_count, 
        s3storage_count, 
        ario_count, 
        dtes_count, 
        monitoring_count,
        onlineeditor_count,
        logstash_count,
        lk_count,
        additional_lk_count,
        redundancy,
        importhistorydata_size,
        test_kontur,
        dev_kontur
        )

    #=======================================================Подготавливаем имя файла для сохранения ============================================================#
    def sanitize_filename(filename):
        """
        Очищает имя файла, удаляя любые кавычки и подстроку "ООО".

        :param filename: Исходное имя файла (строка).
        :return: Очищенное имя файла (строка).
        """
        # Разделяем имя файла на имя и расширение
        name, ext = os.path.splitext(filename)
        
        # Удаляем все типы кавычек
        # Добавляем сюда любые другие типы кавычек, если необходимо
        quotes_pattern = r'[\"\'«»“”‘’„‟]'
        name = re.sub(quotes_pattern, '', name)
        
        # Удаляем подстроку "ООО" (без учёта регистра)
        name = re.sub(r'\bООО\b[ _-]*', '', name, flags=re.IGNORECASE)
        
        # Удаляем возможные лишние разделители, например, двойные подчёркивания
        name = re.sub(r'[_-]{2,}', '_', name)
        
        # Удаляем ведущие и завершающие разделители и пробелы
        name = name.strip('_- ')
        
        # Собираем обратно имя файла с расширением
        sanitized_filename = f"{name}{ext}"    
        return sanitized_filename

    temp_report_filename = f"Рекомендации_по_характеристикам_серверов_{organization}_{current_date}.docx"
    report_filename = sanitize_filename(temp_report_filename)
    report_path = os.path.join(app.config['REPORT_FOLDER'], report_filename)

#=======================================================Функции работы со схемами DrawIO============================================================#
    #Указываем место хранение схем
    TEMPLATE_SCHEMES = r'schemes_template'
    app.config['TEMPLATE_SCHEMES'] = TEMPLATE_SCHEMES
    
    
    #Вызываем функцию и записываем выбор в переменную
    scheme_template = select_scheme_template(
        redundancy,
        operationsystem,
        kubernetes,
        lk_users,
        concurrent_users
    )
    
    #Вызываем функцию конвертации в PNG
    try:
        saved_scheme = drawing_scheme(redundancy, layers_to_toggle, template_path, scheme_template)
        logger.info(f"Схема успешно сохранена в файле {saved_scheme}.") 
    except ValueError as se:
        logger.error(f"Произошла ошибка: {se}")
    
    #вызываем функцию вставки схемы в файл
    try:
        replace_placeholder_with_image(
            placeholder="PASTESCHEME",
            image_path=saved_scheme,
            width_inches=5
        )
        logger.info(f"Заполнитель  успешно заменен на изображение  в документе.")
    except ValueError as ve:
        logger.error(f"Произошла ошибка: {ve}")

    doc.save(report_path)

    # Удаляем загруженный XML файл (опционально)
    
    os.remove(filepath)

    report_link = url_for('download_report', filename=report_filename)

    # Логирование информации о запросе
    try:
        logger.info(f"Рендеринг шаблона 'index.html' с отчетной ссылкой: {report_link}")
        return render_template('index.html', report_link=report_link)
    except:
        logger.error(f"Ошибка при рендеринге шаблона 'index.html'")

@app.route('/reports/<filename>')
def download_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
