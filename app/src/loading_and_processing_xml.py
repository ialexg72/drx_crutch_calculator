import os
import re
import uuid
import docx
import logging
import logging.config
from . import settings
from flask import Flask,request, render_template, url_for, jsonify
from datetime import datetime
import xml.etree.ElementTree as ET

from src.docx import select_word_template, text_edit_func, delete_unnecessary_information
from src.drawio import drawio_func, select_scheme_template
from src.calculate import k8s, rrm_services, s3_services, lk_services,webserver, ms, nomad, reverseproxy, storage, sql, ario_services, dcs_services, elasticsearch_services, monitoring_services, onlineeditor_services
import src.docx.delete_unnecessary_information as delete_unnecessary_information

app = Flask(__name__)
app.config.from_object(settings.Config) 

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

layers_to_toggle = []

calculation_status = {
    'status': 'not_started',  # 'not_started', 'processing', 'completed', 'failed'
    'progress': 0,
    'message': '',
    'report_link': None
}

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
    operationsystem = data.get('ostype', '')
    version = data.get('version', '')
    kubernetes = data.get('kubernetes', '')
    s3storage = data.get('s3storage', '')
    redundancy = data.get('redundancy', '')
    monitoring = data.get('monitoring', '')
    dev_kontur = data.get('dev_kontur', '')
    test_kontur = data.get('test_kontur', '')
    database = data.get('database', '')
        #Активность пользователей
    registeredUsers = int(data.get('registeredUsers', ''))
    peakLoad = int(data.get('peakLoad', ''))
    peakPeriod = data.get('peakPeriod', '')
    concurrent_users = int(data.get('concurrentUsers', ''))
    mobileusers = int(data.get('mobileappusers', ''))
    lk_users = int(data.get('lkusers', ''))
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

    calculation_status['progress'] = 30
    calculation_status['message'] = 'Расчет конфигурации...'
    # Calculating resources and assigning values to variables
    k8s_resources = k8s.calculate_kubernetes(kubernetes)
    webserver_resources = webserver.calculate_webserver(concurrent_users, redundancy)
    ms_resources = ms.calculate_ms(redundancy, concurrent_users)
    nomad_resources = nomad.calculate_nomad(redundancy, mobileusers)
    reverseproxy_resources = reverseproxy.calculate_reverseproxy(redundancy, concurrent_users)
    sql_resources = sql.calculate_sql(redundancy, concurrent_users, lk_users)
    dcs_resources = dcs_services.calculate_dcs(redundancy, dcsdochours)
    elasticsearch_resources = elasticsearch_services.calculate_elasticsearch(elasticsearch, annualdatagrowth, midsizedoc)
    ario_resources = ario_services.calculate_ario(operationsystem, ariodocin, ario)
    monitoring_resources = monitoring_services.calculate_monitoring(monitoring, concurrent_users)
    onlineeditor_resources = onlineeditor_services.calculate_online_editor(onlineeditor, concurrent_users)
    rrm_resources = rrm_services.calculate_rrm(redundancy, concurrent_users)
    lk_resources = lk_services.calculate_lk(redundancy, lk_users, concurrent_users)
    s3storage_resources = s3_services.calculate_s3_storage(s3storage)

    # Unpacking resources
    k8s_count, k8s_cpu, k8s_ram, k8s_hdd = k8s_resources
    webserver_count, webserver_cpu, webserver_ram, webserver_hdd = webserver_resources
    ms_count, ms_cpu, ms_ram, ms_hdd = ms_resources
    nomad_count, nomad_cpu, nomad_ram, nomad_hdd = nomad_resources
    reverseproxy_count, reverseproxy_cpu, reverseproxy_ram, reverseproxy_hdd = reverseproxy_resources
    sql_count, sql_cpu, sql_ram, sql_hdd = sql_resources
    dcs_count, dcs_cpu, dcs_ram, dcs_hdd = dcs_resources
    elasticsearch_count, elasticsearch_cpu, elasticsearch_ram, elasticsearch_hdd = elasticsearch_resources
    ario_count, ario_cpu, ario_ram, ario_hdd, dtes_count, dtes_cpu, dtes_ram, dtes_hdd = ario_resources
    monitoring_count, monitoring_hdd, monitoring_cpu, monitoring_ram, logstash_count, logstash_hdd, logstash_cpu, logstash_ram, monitoring_index_size = monitoring_resources
    onlineeditor_count, onlineeditor_cpu, onlineeditor_ram, onlineeditor_hdd = onlineeditor_resources
    rrm_count, rrm_cpu, rrm_ram, rrm_hdd = rrm_resources
    lk_count, lk_cpu, lk_ram, lk_hdd, additional_lk_count, additional_lk_cpu, additional_lk_ram, additional_lk_hdd = lk_resources
    s3storage_cpu, s3storage_ram, s3storage_count = s3storage_resources

    #Подгружаем расчеты хранилищ
    main_storage_doc, main_storage_db, reserve_storage_doc, reserve_storage_db, highspeed_storage, elasticsearch_search_index_size, service_db_size, lowspeed_storage, annualdatagrowth_size, importhistorydata_size = storage.calculate_storage(
        importhistorydata, 
        midsizedoc, 
        annualdatagrowth, 
        redundancy, 
        database, 
        concurrent_users, 
        sql_count,
        webserver_count,
        webserver_hdd, 
        ms_count,
        ms_hdd,
        k8s_count,
        k8s_hdd,
        nomad_count,
        nomad_hdd,
        reverseproxy_count,
        reverseproxy_hdd,
        dcs_count,
        dcs_hdd,
        elasticsearch,
        elasticsearch_count,
        elasticsearch_hdd,
        monitoring_count,
        monitoring_hdd,
        ario_count,
        ario_hdd,
        dtes_count,
        dtes_hdd,
        onlineeditor_count,
        onlineeditor_hdd,
        lk_count,
        lk_hdd,
        additional_lk_count,
        additional_lk_hdd,
        rrm_count,
        rrm_hdd,
        logstash_count,
        logstash_hdd
    )
    
    #Подгружаем шаблон Word
    template_path = select_word_template.select_word_template(operationsystem, kubernetes, version, app)
    logger.debug(f"Путь к шаблону: {template_path}")
    doc = docx.Document(template_path)

    #Подгружаем шаблон Drawio
    scheme_template = select_scheme_template.select_scheme_template(
        redundancy,
        operationsystem,
        kubernetes,
        lk_users,
        concurrent_users
    )

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
            +(onlineeditor_count*onlineeditor_cpu)+(lk_count*lk_cpu)
            +(additional_lk_count*additional_lk_cpu)
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
        "SearchIndexSize": str(round(elasticsearch_search_index_size / 1024, 1)) + " ТБ" if int(elasticsearch_search_index_size) >= 1000 else str(elasticsearch_search_index_size) + " ГБ", 
        "MidStorageSize": str(round(main_storage_doc / 1024, 1)) + " ТБ" if main_storage_doc >= 1000 else str(main_storage_doc) + " ГБ",
        "ServiceDBStorageSize": str(round(service_db_size / 1024, 1)) + " ТБ" if service_db_size >= 1000 else str(service_db_size) + " ГБ",
        "SlowStorageSize": str(round(lowspeed_storage / 1024, 1)) + " ТБ" if lowspeed_storage >= 1000 else str(lowspeed_storage) + " ГБ",
        "FStorageSize": str(round(main_storage_doc / 1024, 1)) + " ТБ" if main_storage_doc >= 1000 else str(main_storage_doc) + " ГБ",
        "FResStorageSize": str(round(reserve_storage_doc / 1024, 1)) + " ТБ" if reserve_storage_doc >= 1000 else str(reserve_storage_doc) + " ГБ",
    }
    for placeholder, value in replacements.items():
        text_edit_func.replace_placeholder(doc, placeholder, value)

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
    
    calculation_status['progress'] = 60
    calculation_status['message'] = 'Подготовка схемы...'
    #Указываем место хранение схем
    TEMPLATE_SCHEMES = r'schemes_template'
    app.config['TEMPLATE_SCHEMES'] = TEMPLATE_SCHEMES
    
    #Вызываем функцию конвертации в PNG
    try:
        saved_scheme = drawio_func.drawing_scheme(redundancy, layers_to_toggle, template_path, scheme_template)
        logger.info(f"Схема успешно сохранена в файле {saved_scheme}.") 
    except ValueError as se:
        logger.error(f"Произошла ошибка: {se}")
    
    #вызываем функцию вставки схемы в файл
    try:
        drawio_func.replace_placeholder_with_image(
            doc,
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
        logging.debug(f"Рендеринг шаблона 'index.html' с отчетной ссылкой: {report_link}")
        return render_template('index.html', report_link=report_link)
    except:
        logging.error(f"Ошибка при рендеринге шаблона 'index.html'")

def upload_xml2():
    calculation_status['progress'] = 10
    calculation_status['message'] = 'Обработка XML...'
    
    logger.info("Начата обработка загруженного XML файла")
    
    xml_data = request.data.decode('utf-8')
    
    # Сохраняем загруженный XML файл
    try: 
        filename = f"{uuid.uuid4()}.xml"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_data)
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
    operationsystem = data.get('ostype', '')
    version = data.get('version', '')
    kubernetes = data.get('kubernetes', '')
    s3storage = data.get('s3storage', '')
    redundancy = data.get('redundancy', '')
    monitoring = data.get('monitoring', '')
    dev_kontur = data.get('dev_kontur', '')
    test_kontur = data.get('test_kontur', '')
    database = data.get('database', '')
        #Активность пользователей
    registeredUsers = int(data.get('registeredUsers', ''))
    peakLoad = int(data.get('peakLoad', ''))
    peakPeriod = data.get('peakPeriod', '')
    concurrent_users = int(data.get('concurrentUsers', ''))
    mobileusers = int(data.get('mobileappusers', ''))
    lk_users = int(data.get('lkusers', ''))
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

    calculation_status['progress'] = 30
    calculation_status['message'] = 'Вычисление ресурсов сервисов...'
    # Calculating resources and assigning values to variables
    k8s_resources = k8s.calculate_kubernetes(kubernetes)
    webserver_resources = webserver.calculate_webserver(concurrent_users, redundancy)
    ms_resources = ms.calculate_ms(redundancy, concurrent_users)
    nomad_resources = nomad.calculate_nomad(redundancy, mobileusers)
    reverseproxy_resources = reverseproxy.calculate_reverseproxy(redundancy, concurrent_users)
    sql_resources = sql.calculate_sql(redundancy, concurrent_users, lk_users)
    dcs_resources = dcs_services.calculate_dcs(redundancy, dcsdochours)
    elasticsearch_resources = elasticsearch_services.calculate_elasticsearch(elasticsearch, annualdatagrowth, midsizedoc)
    ario_resources = ario_services.calculate_ario(operationsystem, ariodocin, ario)
    monitoring_resources = monitoring_services.calculate_monitoring(monitoring, concurrent_users)
    onlineeditor_resources = onlineeditor_services.calculate_online_editor(onlineeditor, concurrent_users)
    rrm_resources = rrm_services.calculate_rrm(redundancy, concurrent_users)
    lk_resources = lk_services.calculate_lk(redundancy, lk_users, concurrent_users)
    s3storage_resources = s3_services.calculate_s3_storage(s3storage)

    # Unpacking resources
    k8s_count, k8s_cpu, k8s_ram, k8s_hdd = k8s_resources
    webserver_count, webserver_cpu, webserver_ram, webserver_hdd = webserver_resources
    ms_count, ms_cpu, ms_ram, ms_hdd = ms_resources
    nomad_count, nomad_cpu, nomad_ram, nomad_hdd = nomad_resources
    reverseproxy_count, reverseproxy_cpu, reverseproxy_ram, reverseproxy_hdd = reverseproxy_resources
    sql_count, sql_cpu, sql_ram, sql_hdd = sql_resources
    dcs_count, dcs_cpu, dcs_ram, dcs_hdd = dcs_resources
    elasticsearch_count, elasticsearch_cpu, elasticsearch_ram, elasticsearch_hdd = elasticsearch_resources
    ario_count, ario_cpu, ario_ram, ario_hdd, dtes_count, dtes_cpu, dtes_ram, dtes_hdd = ario_resources
    monitoring_count, monitoring_hdd, monitoring_cpu, monitoring_ram, logstash_count, logstash_hdd, logstash_cpu, logstash_ram, monitoring_index_size = monitoring_resources
    onlineeditor_count, onlineeditor_cpu, onlineeditor_ram, onlineeditor_hdd = onlineeditor_resources
    rrm_count, rrm_cpu, rrm_ram, rrm_hdd = rrm_resources
    lk_count, lk_cpu, lk_ram, lk_hdd, additional_lk_count, additional_lk_cpu, additional_lk_ram, additional_lk_hdd = lk_resources
    s3storage_cpu, s3storage_ram, s3storage_count = s3storage_resources

    calculation_status['progress'] = 60
    calculation_status['message'] = 'Вычисление ресурсов хранилищ...'
    #Подгружаем расчеты хранилищ
    main_storage_doc, main_storage_db, reserve_storage_doc, reserve_storage_db, highspeed_storage, elasticsearch_search_index_size, service_db_size, lowspeed_storage, annualdatagrowth_size, importhistorydata_size = storage.calculate_storage(
        importhistorydata, 
        midsizedoc, 
        annualdatagrowth, 
        redundancy, 
        database, 
        concurrent_users, 
        sql_count,
        webserver_count,
        webserver_hdd, 
        ms_count,
        ms_hdd,
        k8s_count,
        k8s_hdd,
        nomad_count,
        nomad_hdd,
        reverseproxy_count,
        reverseproxy_hdd,
        dcs_count,
        dcs_hdd,
        elasticsearch,
        elasticsearch_count,
        elasticsearch_hdd,
        monitoring_count,
        monitoring_hdd,
        ario_count,
        ario_hdd,
        dtes_count,
        dtes_hdd,
        onlineeditor_count,
        onlineeditor_hdd,
        lk_count,
        lk_hdd,
        additional_lk_count,
        additional_lk_hdd,
        rrm_count,
        rrm_hdd,
        logstash_count,
        logstash_hdd
    )
    
    calculation_status['progress'] = 70
    calculation_status['message'] = 'Заполнение шаблона...'
    #Подгружаем шаблон Word
    template_path = select_word_template.select_word_template(operationsystem, kubernetes, version, app)
    logger.debug(f"Путь к шаблону: {template_path}")
    doc = docx.Document(template_path)

    #Подгружаем шаблон Drawio
    scheme_template = select_scheme_template.select_scheme_template(
        redundancy,
        operationsystem,
        kubernetes,
        lk_users,
        concurrent_users
    )

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
            +(onlineeditor_count*onlineeditor_cpu)+(lk_count*lk_cpu)
            +(additional_lk_count*additional_lk_cpu)
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
        "SearchIndexSize": str(round(elasticsearch_search_index_size / 1024, 1)) + " ТБ" if int(elasticsearch_search_index_size) >= 1000 else str(elasticsearch_search_index_size) + " ГБ", 
        "MidStorageSize": str(round(main_storage_doc / 1024, 1)) + " ТБ" if main_storage_doc >= 1000 else str(main_storage_doc) + " ГБ",
        "ServiceDBStorageSize": str(round(service_db_size / 1024, 1)) + " ТБ" if service_db_size >= 1000 else str(service_db_size) + " ГБ",
        "SlowStorageSize": str(round(lowspeed_storage / 1024, 1)) + " ТБ" if lowspeed_storage >= 1000 else str(lowspeed_storage) + " ГБ",
        "FStorageSize": str(round(main_storage_doc / 1024, 1)) + " ТБ" if main_storage_doc >= 1000 else str(main_storage_doc) + " ГБ",
        "FResStorageSize": str(round(reserve_storage_doc / 1024, 1)) + " ТБ" if reserve_storage_doc >= 1000 else str(reserve_storage_doc) + " ГБ",
    }
    for placeholder, value in replacements.items():
        text_edit_func.replace_placeholder(doc, placeholder, value)

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
    calculation_status['progress'] = 90
    calculation_status['message'] = 'Вставка схемы...'#Указываем место хранение схем
    TEMPLATE_SCHEMES = r'schemes_template'
    app.config['TEMPLATE_SCHEMES'] = TEMPLATE_SCHEMES
    
    #Вызываем функцию конвертации в PNG
    try:
        saved_scheme = drawio_func.drawing_scheme(redundancy, layers_to_toggle, template_path, scheme_template)
        logger.info(f"Схема успешно сохранена в файле {saved_scheme}.") 
    except ValueError as se:
        logger.error(f"Произошла ошибка: {se}")
    
    #вызываем функцию вставки схемы в файл
    try:
        drawio_func.replace_placeholder_with_image(
            doc,
            placeholder="PASTESCHEME",
            image_path=saved_scheme,
            width_inches=5
        )
        logger.info(f"Заполнитель  успешно заменен на изображение  в документе.")
    except ValueError as ve:
        logger.error(f"Произошла ошибка: {ve}")

    calculation_status['progress'] = 100
    calculation_status['message'] = 'Сохранение расчета...'
    doc.save(report_path)

    # Удаляем загруженный XML файл (опционально)
    
    os.remove(filepath)

    report_link = url_for('download_report', filename=report_filename)

    try:
        return jsonify({
            'success': True,
            'report_link': report_link,
            'message': 'Отчет успешно создан'
        })
    except Exception as e:
        logger.error(f"Ошибка при создании JSON-ответа: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при создании отчета'
        }), 500