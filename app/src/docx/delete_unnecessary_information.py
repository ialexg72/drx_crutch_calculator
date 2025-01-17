import src.docx.text_edit_func as text_edit_func
def main(
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
    dev_kontur,
    operationsystem
    ):
    if kubernetes.lower() == "false":
        if k8s_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел администрирования Kubernetes", 6)
            text_edit_func.remove_specific_rows(doc, "Kubernetes API server", 7)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел администрирования Kubernetes")
            text_edit_func.delete_paragraphs_by_text(doc, "На узле генерируется конфигурационный файл config.yml и сертификат для проверки токена")       
        if ms_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узлы микросервисов", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Узлы микросервисов")
        if nomad_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узлы сервиса NOMAD", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис NOMAD (NomadService)")
        if reverseproxy_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узлы reverse proxy", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "reverse-proxy")
        if dcs_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел службы ввода документов", 6)
            text_edit_func.remove_specific_rows(doc, "Периодичность импорта через средство захвата документов, док./час", 0)
            text_edit_func.delete_paragraphs_by_text(doc, "Узлы DCS")
        if elasticsearch_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел полнотекстового поиска", 6)
            text_edit_func.remove_specific_rows(doc, "Разделы для индексов полнотекстового поиска", 0)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел полнотекстового поиска – виртуальная машина")
            text_edit_func.delete_paragraphs_by_text(doc, "Хранилище для индексов полнотекстового поиска")
        if rrm_count == 0 and operationsystem.lower() == "linux":
            text_edit_func.delete_paragraphs_by_text(doc, "Узлы RabbitMQ, etcd+haproxy+keepalived (RMQ + EHK)")
            text_edit_func.remove_specific_rows(doc, "Узлы RabbitMQ, etcd + keepalived + haproxy (для кластера PG)", 6)
        if rrm_count == 0 and operationsystem.lower() == "windows":
            text_edit_func.delete_paragraphs_by_text(doc, "Узлы RabbitMQ")
            text_edit_func.remove_specific_rows(doc, "Узлы RabbitMQ", 6)
        if s3storage_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел переноса данных в объектные хранилища S3", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Объектное S3 хранилище")
            text_edit_func.delete_paragraphs_by_text(doc, "Узел переноса данных в объектные хранилища S3")
        if ario_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел сервисов Directum Ario", 6)
            text_edit_func.remove_specific_rows(doc, "Узел сервисов Directum Text Extractor Service", 6)
            text_edit_func.remove_specific_rows(doc, "Сервисы Ario", 0)
            text_edit_func.delete_paragraphs_by_text(doc, "Сервисы Ario")
            text_edit_func.delete_paragraphs_by_text(doc, "** - для сервисов Ario рекомендуется использовать процессоры")
        if dtes_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел сервисов Directum Text Extractor Service", 6)
        if monitoring_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел решения «Мониторинг системы Directum RX»", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел решения «Мониторинг системы Directum RX»")
            text_edit_func.remove_specific_rows(doc, "Узел Logstash", 6)
            text_edit_func.remove_specific_rows(doc, "Разделы для индексов системы мониторинга", 0)
        if onlineeditor_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел решения «Интеграция с онлайн-редакторами OnlyOffice и Р7-Офис»", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел решения «Интеграция с онлайн-редакторами»")
        if logstash_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел Logstash", 6)
        if lk_count == 0:
            text_edit_func.delete_paragraphs_by_text(doc, "«Личный кабинет» - решение позволяет")
            text_edit_func.delete_paragraphs_by_text(doc, "Архитектура платформы личного кабинета")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервер приложения личного кабинета")
            text_edit_func.delete_paragraphs_by_text(doc, "Сайт личного кабинета (EssSite)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис идентификации (IdentityService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Cервис подписания (SignService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис документов (DocumentService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис сообщений (MessageBroker)")
            text_edit_func.delete_paragraphs_by_text(doc, "Cервис предпросмотра (PreviewService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис хранения файлов предпросмотра (PreviewStorage)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис хранения BLOB-объектов (BlobStorageService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервер размещения контента (ContentServer)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервер сеансов (SessionServer)")
            text_edit_func.remove_specific_rows(doc, "Узлы решения «Личный кабинет»", 6)
            text_edit_func.remove_specific_rows(doc, "Дополнительный сервисный узел Directum RX для «Личный кабинет»", 6)
            text_edit_func.remove_specific_rows(doc, "HR Pro (личный кабинет)", 0)
        if additional_lk_count == 0:
            text_edit_func.remove_specific_rows(doc, "Дополнительный сервисный узел Directum RX для «Личный кабинет»", 6)
        if importhistorydata_size == 0:
            text_edit_func.remove_specific_rows(doc, "Исторические данные", 0)
        if test_kontur.lower() == "false":
            text_edit_func.delete_paragraphs_by_text(doc, "среде тестирования;")
            text_edit_func.remove_heading_and_content(doc, "Минимальные требования к узлам тестового контура")
        if dev_kontur.lower() == "false":
            text_edit_func.delete_paragraphs_by_text(doc, "среде разработки;")
            text_edit_func.remove_heading_and_content(doc, "Минимальные требования к узлам контура разработки")
    if kubernetes.lower() == "true":
        if lk_count == 0:
            text_edit_func.delete_paragraphs_by_text(doc, "«Личный кабинет» - решение позволяет")
            text_edit_func.delete_paragraphs_by_text(doc, "Архитектура платформы личного кабинета")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервер приложения личного кабинета")
            text_edit_func.delete_paragraphs_by_text(doc, "Сайт личного кабинета (EssSite)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис идентификации (IdentityService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Cервис подписания (SignService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис документов (DocumentService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис сообщений (MessageBroker)")
            text_edit_func.delete_paragraphs_by_text(doc, "Cервис предпросмотра (PreviewService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис хранения файлов предпросмотра (PreviewStorage)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервис хранения BLOB-объектов (BlobStorageService)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервер размещения контента (ContentServer)")
            text_edit_func.delete_paragraphs_by_text(doc, "Сервер сеансов (SessionServer)")
            text_edit_func.remove_specific_rows(doc, "Узлы решения «Личный кабинет»", 6)
            text_edit_func.remove_specific_rows(doc, "Дополнительный сервисный узел Directum RX для «Личный кабинет»", 6)
            text_edit_func.remove_specific_rows(doc, "HR Pro (личный кабинет)", 0)
        if additional_lk_count == 0:
            text_edit_func.remove_specific_rows(doc, "Дополнительный сервисный узел Directum RX для «Личный кабинет»", 6)
        if ms_count == 0:
            text_edit_func.remove_specific_rows(doc, "Поды микросервисов Directum RX", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Поды микросервисов Directum RX")
        if nomad_count == 0:
            text_edit_func.remove_specific_rows(doc, "Поды сервиса NOMAD", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Поды NOMAD (NomadService)")
        if reverseproxy_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узлы reverse proxy", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Узлы reverse proxy")
        if dcs_count == 0:
            text_edit_func.remove_specific_rows(doc, "Поды службы ввода документов", 6)
            text_edit_func.remove_specific_rows(doc, "Периодичность импорта через средство захвата документов, док./час", 0)
            text_edit_func.delete_paragraphs_by_text(doc, "Поды DCS")
        if elasticsearch_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел полнотекстового поиска", 6)
            text_edit_func.remove_specific_rows(doc, "Разделы для индексов полнотекстового поиска", 0)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел полнотекстового поиска – виртуальная машина")
            text_edit_func.delete_paragraphs_by_text(doc, "Хранилище для индексов полнотекстового поиска")
        if rrm_count == 0:
            text_edit_func.delete_paragraphs_by_text(doc, "Узлы RabbitMQ, etcd+haproxy+keepalived (RMQ + EHK)")
            text_edit_func.remove_specific_rows(doc, "Узлы RabbitMQ, etcd + keepalived + haproxy (для кластера PG)", 6)
        if s3storage_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел переноса данных в объектные хранилища S3", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Объектное S3 хранилище")
            text_edit_func.delete_paragraphs_by_text(doc, "Узел переноса данных в объектные хранилища S3")
        if ario_count == 0:
            text_edit_func.remove_specific_rows(doc, "Поды сервисов Directum Ario", 6)
            text_edit_func.remove_specific_rows(doc, "Поды сервисов Directum Text Extractor Service", 6)
            text_edit_func.remove_specific_rows(doc, "Сервисы Ario", 0)
            text_edit_func.delete_paragraphs_by_text(doc, "Поды с сервисами Ario")
            text_edit_func.delete_paragraphs_by_text(doc, "** - для сервисов Ario рекомендуется использовать процессоры")
        if dtes_count == 0:
            text_edit_func.remove_specific_rows(doc, "Поды сервисов Directum Text Extractor Service", 6)
        if onlineeditor_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел решения «Интеграция с онлайн-редакторами OnlyOffice и Р7-Офис»", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел решения «Интеграция с онлайн-редакторами»")
        if monitoring_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел решения «Мониторинг системы Directum RX»", 6)
            text_edit_func.delete_paragraphs_by_text(doc, "Узел решения «Мониторинг системы Directum RX»")
            text_edit_func.remove_specific_rows(doc, "Узел Logstash", 6)
            text_edit_func.remove_specific_rows(doc, "Разделы для индексов системы мониторинга", 0)
        if logstash_count == 0:
            text_edit_func.remove_specific_rows(doc, "Узел Logstash", 6)
        if importhistorydata_size == 0:
            text_edit_func.remove_specific_rows(doc, "Исторические данные, объем в ГБ", 0)
        if test_kontur.lower() == "false":
            text_edit_func.delete_paragraphs_by_text(doc, "среде тестирования;")
            text_edit_func.remove_heading_and_content(doc, "Минимальные требования к узлам тестового контура")
        if dev_kontur.lower() == "false":
            text_edit_func.delete_paragraphs_by_text(doc, "среде разработки;")
            text_edit_func.remove_heading_and_content(doc, "Минимальные требования к узлам контура разработки")
    if redundancy.lower() == "false":
        text_edit_func.delete_paragraphs_by_text(doc, "Представленная инсталляция работает в режиме распределения нагрузки")
        text_edit_func.delete_paragraphs_by_text(doc, "Зеленые блоки")
        text_edit_func.delete_paragraphs_by_text(doc, "Красные блоки")