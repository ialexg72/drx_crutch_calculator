import math
def calculate_elasticsearch(elasticsearch, annualdatagrowth, middocsize):
    """
    Calculate the number of Elasticsearch nodes, CPU, RAM, and HDD.

    Parameters:
    elasticsearch (str): Whether Elasticsearch is enabled.
    annualdatagrowth (int): The annual data growth in GB.
    middocsize (int): The middle size of a document in GB.

    Returns:
    int: The number of Elasticsearch nodes.
    int: The number of CPU cores.
    int: The amount of RAM in GB.
    int: The amount of HDD in GB.
    """
    if elasticsearch.lower() == "true":
        es_node_count = 1
        es_cpu = 8
        es_ram = annualdatagrowth * middocsize
        es_ram_gb = es_ram / (1024 ** 3)
        es_ram = 32 if es_ram_gb > 6 else 16
        es_ram = es_ram if es_ram % 2 == 0 else es_ram + 1
        es_hdd = 50
    else:
        es_node_count = 0
        es_cpu = 0
        es_ram = 0
        es_hdd = 0
    return es_node_count, es_cpu, es_ram, es_hdd