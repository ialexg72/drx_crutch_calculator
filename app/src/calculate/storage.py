import math
def calculate_storage(
    importhistorydata: int, 
    midsizedoc: int, 
    annualdatagrowth: int, 
    redundancy: str, 
    database: str, 
    concurrent_users: int, 
    sql_count: int,
    webserver_count: int,
    webserver_hdd: int, 
    ms_count: int,
    ms_hdd: int,
    k8s_count: int,
    k8s_hdd: int,
    nomad_count: int,
    nomad_hdd: int,
    reverseproxy_count: int,
    reverseproxy_hdd: int,
    dcs_count: int,
    dcs_hdd: int,
    elasticsearch: str,
    elasticsearch_count,
    elasticsearch_hdd: int,
    monitoring_count: int,
    monitoring_hdd: int,
    ario_count: int,
    ario_hdd: int,
    dtes_count: int,
    dtes_hdd: int,
    onlineeditor_count: int,
    onlineeditor_hdd: int,
    lk_count: int,
    lk_hdd: int,
    additional_lk_count: int,
    additional_lk_hdd: int,
    rrm_count: int,
    rrm_hdd: int,
    logstash_count: int,
    logstash_hdd: int
):
    """
    Calculate the storage requirements for various components of the system.

    Parameters:
    importhistorydata (int): The number of documents to be imported from history.
    midsizedoc (int): The average size of a document in MB.
    annualdatagrowth (int): The annual growth of documents in the system.
    redundancy (str): Whether redundancy is enabled.
    database (str): The type of database to use.
    concurrent_users (int): The number of concurrent users.
    sql_count (int): The number of SQL nodes.

    Returns:
    tuple: A tuple containing the main storage size for documents, main storage size for database, reserve storage size for documents, reserve storage size for database, high speed storage size, Elasticsearch search index size, service database size, and low speed storage size.
    """
    # Calculate the size of the imported documents
    importhistorydata_size = round(importhistorydata * midsizedoc / 1024 / 1024)

    # Calculate the annual growth of documents
    annualdatagrowth_size = round(annualdatagrowth * midsizedoc / 1024 / 1024)

    # Calculate the main storage size for documents
    main_storage_doc = round((annualdatagrowth_size * 6) + importhistorydata_size)

    # Calculate the reserve storage size for documents
    reserve_storage_doc = round(main_storage_doc * 2)

    # Calculate the main storage size for database
    if concurrent_users != 0 or sql_count != 0:
        main_storage_db = round(main_storage_doc * 0.025 + (concurrent_users / 100 * 5))
        if redundancy.lower() == "true" and database.lower() == "postgres":
            if main_storage_db < 100:
                main_storage_db = 200
            else:
                main_storage_db = main_storage_db * 2
        else:
            if main_storage_db < 100:
                main_storage_db = 100
            else:
                main_storage_db = main_storage_db
        main_storage_db = int(main_storage_db)
    else:
        main_storage_db = 0

    # Calculate the reserve storage size for database
    if database.lower() == "postgres" and redundancy.lower() == "true":
        reserve_storage_db = main_storage_db * 8 / 2
    else:
        reserve_storage_db = main_storage_db * 8

    # Calculate the high speed storage size
    highspeed_storage = (
        int(main_storage_db)
        + int(webserver_count * webserver_hdd)
        + int(ms_count * ms_hdd)
        + int(k8s_count * k8s_hdd)
        + int(nomad_count * nomad_hdd)
        + int(reverseproxy_count * reverseproxy_hdd)
        + int(sql_count * 100)
        + int(dcs_count * dcs_hdd)
        + int(elasticsearch_count * elasticsearch_hdd)
        + int(monitoring_count * monitoring_hdd)
        + int(ario_count * ario_hdd)
        + int(dtes_count * dtes_hdd)
        + int(onlineeditor_count * onlineeditor_hdd)
        + int(lk_count * lk_hdd)
        + int(additional_lk_count * additional_lk_hdd)
        + int(rrm_count * rrm_hdd)
        + int(logstash_count * logstash_hdd)
    )

    # Calculate the Elasticsearch search index size
    def calculate_elasticsearch_search_index_size(elasticsearch: str, redundancy: str, database: str, main_storage_doc: int, main_storage_db: int) -> int:
        if elasticsearch.lower() != "false":
            if redundancy.lower() == "true" and database.lower() == "postgres":
                value = main_storage_doc * 0.05 + (main_storage_db * 0.05) / 2
            else:
                value = main_storage_doc * 0.05 + main_storage_db * 0.05
            # Round up to the nearest whole numberа
            result = math.ceil(value)
        else:
            result = 0
        return result

    elasticsearch_search_index_size = calculate_elasticsearch_search_index_size(
        elasticsearch, redundancy, database, main_storage_doc, main_storage_db
    )

    # Calculate the service database size
    service_db_size = math.ceil(concurrent_users / 500 * 2)

    # Calculate the low speed storage size
    lowspeed_storage = (reserve_storage_db + reserve_storage_doc)

    return (
        main_storage_doc, main_storage_db, reserve_storage_doc, reserve_storage_db, highspeed_storage, 
        elasticsearch_search_index_size, service_db_size, lowspeed_storage, annualdatagrowth_size, importhistorydata_size,
        
    )